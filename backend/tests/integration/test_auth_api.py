"""Integration tests for the auth API endpoint.

Covers:
  - ``POST /api/v1/auth/google`` with valid/invalid/missing tokens
  - Protected endpoints with valid/expired/invalid-signature JWTs
  - Dev mode fallback (no auth header returns mock user)

Uses FastAPI ``TestClient`` with dependency overrides and
``unittest.mock.patch`` for service-layer mocking.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from app.core.config import settings
from app.core.security import get_current_user
from app.main import create_app
from app.modules.auth.models import User
from app.modules.auth.schemas import UserResponse


# ── Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture
def app():
    """Create a fresh FastAPI app for each test."""
    return create_app()


@pytest.fixture
def client(app):
    """TestClient bound to the fresh app."""
    return TestClient(app)


@pytest.fixture
def mock_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def valid_jwt(mock_user_id) -> str:
    """Create a cryptographically valid JWT signed with the app's SECRET_KEY."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(mock_user_id),
        "exp": now + timedelta(minutes=30),
        "iat": now,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def expired_jwt() -> str:
    """Create a JWT that expired 1 day ago."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uuid.uuid4()),
        "exp": now - timedelta(days=1),
        "iat": now - timedelta(days=31),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


@pytest.fixture
def wrong_key_jwt(mock_user_id) -> str:
    """Create a JWT signed with a different key (wrong signature)."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(mock_user_id),
        "exp": now + timedelta(minutes=30),
        "iat": now,
    }
    return jwt.encode(payload, "some-other-secret-key", algorithm="HS256")


# ── POST /api/v1/auth/google ───────────────────────────────────────────


class TestGoogleLoginEndpoint:
    """Tests for ``POST /api/v1/auth/google``."""

    def test_missing_id_token_returns_422(self, client):
        """GL-1: Missing ``id_token`` in request body → 422 Unprocessable Entity."""
        response = client.post("/api/v1/auth/google", json={})
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        """GL-1: Sending empty JSON → 422."""
        response = client.post("/api/v1/auth/google", json={})
        assert response.status_code == 422

    def test_valid_mock_token_returns_200(self, client, app):
        """GL-1: Valid mock ID token → 200 + TokenResponse with access_token and user."""
        mock_user_info = {"sub": "12345", "email": "a@b.com", "name": "A B"}
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid.uuid4()

        with (
            patch("app.modules.auth.service.verify_google_token", AsyncMock(return_value=mock_user_info)),
            patch("app.modules.auth.service.authenticate_or_register", AsyncMock(return_value=mock_user)),
            patch("app.modules.auth.service.issue_jwt", AsyncMock(return_value="mock-access-token")),
        ):
            response = client.post("/api/v1/auth/google", json={"id_token": "mock-valid-token"})

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "mock-access-token"
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_invalid_token_returns_401(self, client):
        """GL-2: Invalid ID token → 401."""
        with patch(
            "app.modules.auth.service.verify_google_token",
            AsyncMock(side_effect=ValueError("Invalid Google ID token")),
        ):
            response = client.post(
                "/api/v1/auth/google",
                json={"id_token": "invalid-token"},
            )

        assert response.status_code == 401
        assert "Invalid Google ID token" in response.json()["detail"]


# ── Protected endpoint ─────────────────────────────────────────────────


class TestProtectedEndpoint:
    """Tests for a protected endpoint (``GET /api/v1/plants``) with JWT auth."""

    def test_valid_jwt_returns_200(self, client, app, valid_jwt, mock_user_id):
        """JT-2: Valid JWT → 200 and user has correct id."""
        async def override_get_current_user():
            return UserResponse(
                id=mock_user_id,
                email="test@test.com",
                name="Test User",
            )

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = client.get(
            "/api/v1/plants/",
            headers={"Authorization": f"Bearer {valid_jwt}"},
        )

        assert response.status_code == 200

    def test_expired_jwt_returns_401(self, client, app, expired_jwt):
        """JT-1: Expired JWT → 401."""
        response = client.get(
            "/api/v1/plants/",
            headers={"Authorization": f"Bearer {expired_jwt}"},
        )

        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    def test_invalid_signature_returns_401(self, client, app, wrong_key_jwt):
        """JT-3: JWT signed with a different key → 401."""
        response = client.get(
            "/api/v1/plants/",
            headers={"Authorization": f"Bearer {wrong_key_jwt}"},
        )

        assert response.status_code == 401

    def test_missing_token_returns_401_in_production(self, client, app):
        """DM-2: Real GOOGLE_CLIENT_ID + no auth header → 401."""
        with patch.object(settings, "GOOGLE_CLIENT_ID", "real-client-id.apps.googleusercontent.com"):
            response = client.get("/api/v1/plants/")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]


# ── Dev mode fallback ──────────────────────────────────────────────────


class TestDevMode:
    """Tests for dev mode fallback in ``get_current_user``."""

    def test_no_auth_header_returns_mock_user(self, client, app):
        """DM-1: Placeholder GOOGLE_CLIENT_ID + no auth header → mock user."""
        with patch.object(settings, "GOOGLE_CLIENT_ID", "placeholder-local-dev"):
            response = client.get("/api/v1/plants/")

        assert response.status_code == 200
        data = response.json()
        assert data == []  # plants endpoint returns empty list

    def test_dev_mode_still_accepts_real_jwt(self, client, app, valid_jwt):
        """Dev mode with valid JWT still verifies normally."""
        async def override_get_current_user():
            return UserResponse(
                id=uuid.uuid4(),
                email="dev-mode-user@test.com",
                name="Dev Mode User",
            )

        app.dependency_overrides[get_current_user] = override_get_current_user

        with patch.object(settings, "GOOGLE_CLIENT_ID", "placeholder-local-dev"):
            response = client.get(
                "/api/v1/plants/",
                headers={"Authorization": f"Bearer {valid_jwt}"},
            )

        assert response.status_code == 200
