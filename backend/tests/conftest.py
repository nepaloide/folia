"""Shared test fixtures for backend tests."""

import uuid

import pytest

from app.modules.auth.schemas import UserResponse


@pytest.fixture
def mock_user() -> UserResponse:
    """Return a standard test user response."""
    return UserResponse(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        email="test@test.com",
        name="Test User",
    )
