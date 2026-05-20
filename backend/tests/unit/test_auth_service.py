"""Unit tests for auth service layer.

Covers:
  - ``verify_google_token`` (valid, invalid, dev mode)
  - ``issue_jwt`` (returns string, correct sub claim, has expiry)
  - ``authenticate_or_register`` (creates new user, returns existing)

Requires ``pytest`` and ``pytest-asyncio``.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.core.config import settings
from app.modules.auth import service
from app.modules.auth.models import User


# ── verify_google_token ────────────────────────────────────────────────


class TestVerifyGoogleToken:
    """Tests for ``service.verify_google_token()``."""

    @pytest.mark.asyncio
    async def test_dev_mode_returns_mock_info_without_calling_google(self):
        """DM-1: When GOOGLE_CLIENT_ID is placeholder, return mock info
        and do NOT call google-auth."""
        with patch.object(settings, "GOOGLE_CLIENT_ID", "placeholder-local-dev"):
            result = await service.verify_google_token("any-token")

        assert result == {
            "sub": "placeholder-google-id",
            "email": "dev@folia.app",
            "name": "Dev User",
        }

    @pytest.mark.asyncio
    @patch("google.oauth2.id_token.verify_oauth2_token")
    async def test_valid_token_returns_decoded_claims(self, mock_verify):
        """GL-1: Valid token returns the decoded claims dict from google-auth."""
        expected = {"sub": "12345", "email": "a@b.com", "name": "A B"}
        mock_verify.return_value = expected

        with patch.object(settings, "GOOGLE_CLIENT_ID", "real-client-id.apps.googleusercontent.com"):
            result = await service.verify_google_token("valid-token")

        assert result == expected
        mock_verify.assert_called_once()

    @pytest.mark.asyncio
    @patch("google.oauth2.id_token.verify_oauth2_token")
    async def test_invalid_token_raises_value_error(self, mock_verify):
        """GL-2: Invalid (expired/forged/wrong-audience) token raises ValueError."""
        mock_verify.side_effect = ValueError("Token verification failed")

        with patch.object(settings, "GOOGLE_CLIENT_ID", "real-client-id.apps.googleusercontent.com"):
            with pytest.raises(ValueError, match="Invalid Google ID token"):
                await service.verify_google_token("bad-token")

        mock_verify.assert_called_once()

    @pytest.mark.asyncio
    @patch("google.oauth2.id_token.verify_oauth2_token")
    async def test_google_auth_error_wrapped_properly(self, mock_verify):
        """GL-2: The original ValueError is wrapped in a new ValueError with a
        consistent message."""
        mock_verify.side_effect = ValueError("Signature verification failed")

        with patch.object(settings, "GOOGLE_CLIENT_ID", "real-client-id.apps.googleusercontent.com"):
            with pytest.raises(ValueError) as exc_info:
                await service.verify_google_token("bad-sig-token")

        assert "Invalid Google ID token" in str(exc_info.value)


# ── issue_jwt ──────────────────────────────────────────────────────────


class TestIssueJwt:
    """Tests for ``service.issue_jwt()``."""

    @pytest.mark.asyncio
    async def test_returns_string(self):
        """JT-2: issue_jwt returns a non-empty string."""
        token = await service.issue_jwt(uuid.uuid4())
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.asyncio
    async def test_contains_correct_sub_claim(self):
        """JT-2: The JWT contains the correct ``sub`` claim (user UUID as str)."""
        user_id = uuid.uuid4()
        token = await service.issue_jwt(user_id)

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["sub"] == str(user_id)

    @pytest.mark.asyncio
    async def test_has_expiry_in_future(self):
        """JT-1: The JWT has an ``exp`` claim set in the future (30-day window)."""
        token = await service.issue_jwt(uuid.uuid4())
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        assert "exp" in payload
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()
        assert "iat" in payload


# ── authenticate_or_register ───────────────────────────────────────────


class TestAuthenticateOrRegister:
    """Tests for ``service.authenticate_or_register()``."""

    @pytest.mark.asyncio
    async def test_creates_user_on_first_call(self):
        """UP-1: No existing user → creates and returns a new User."""
        user_info = {"sub": "new-google-id", "email": "new@test.com", "name": "New User"}

        mock_user = MagicMock(spec=User)
        mock_user.google_id = "new-google-id"
        mock_user.email = "new@test.com"
        mock_user.name = "New User"

        with (
            patch.object(service.repository, "get_by_google_id", AsyncMock(return_value=None)),
            patch.object(service.repository, "create", AsyncMock(return_value=mock_user)) as mock_create,
        ):
            result = await service.authenticate_or_register(user_info)

        assert result is mock_user
        mock_create.assert_awaited_once_with(
            google_id="new-google-id",
            email="new@test.com",
            name="New User",
        )

    @pytest.mark.asyncio
    async def test_returns_existing_user_on_second_call(self):
        """UP-2: Existing user with same google_id → returns existing, no INSERT."""
        user_info = {"sub": "existing-google-id", "email": "existing@test.com", "name": "Existing User"}

        existing_user = MagicMock(spec=User)
        existing_user.google_id = "existing-google-id"

        with (
            patch.object(service.repository, "get_by_google_id", AsyncMock(return_value=existing_user)),
            patch.object(service.repository, "create", AsyncMock()) as mock_create,
        ):
            result = await service.authenticate_or_register(user_info)

        assert result is existing_user
        mock_create.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_handles_missing_email_and_name(self):
        """UP-1: Missing email/name in user_info fall back to empty strings."""
        user_info = {"sub": "sparse-google-id"}

        mock_user = MagicMock(spec=User)
        mock_user.google_id = "sparse-google-id"

        with (
            patch.object(service.repository, "get_by_google_id", AsyncMock(return_value=None)),
            patch.object(service.repository, "create", AsyncMock(return_value=mock_user)) as mock_create,
        ):
            result = await service.authenticate_or_register(user_info)

        assert result is mock_user
        mock_create.assert_awaited_once_with(
            google_id="sparse-google-id",
            email="",
            name="",
        )
