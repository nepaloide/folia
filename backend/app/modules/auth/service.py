"""Auth service layer.

Handles Google ID token verification, JWT signing, and user
auto-provisioning (authenticate-or-register flow).
"""

from uuid import UUID
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.modules.auth.models import User
from app.modules.auth import repository


async def verify_google_token(id_token: str) -> dict:
    """Verify a Google ID token and return the decoded claims.

    **Production mode** (GOOGLE_CLIENT_ID is a real ID):
        Delegates to ``google.oauth2.id_token.verify_oauth2_token``
        which validates the signature, audience, and expiry.

    **Dev mode** (GOOGLE_CLIENT_ID is the placeholder):
        Skips verification and returns mock user info so the API
        can be developed without a Google Cloud project.

    Returns:
        A dict with at least ``sub`` (Google user ID), ``email``,
        and ``name``.

    Raises:
        ValueError: If the token is invalid or verification fails.
    """
    if settings.GOOGLE_CLIENT_ID == "placeholder-local-dev":
        return {
            "sub": "placeholder-google-id",
            "email": "dev@folia.app",
            "name": "Dev User",
        }

    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token  # type: ignore[import-untyped]

        info = id_token.verify_oauth2_token(
            id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
        return info
    except ValueError as exc:
        raise ValueError("Invalid Google ID token") from exc


async def issue_jwt(user_id: UUID) -> str:
    """Sign a JWT for the given user.

    Claims:
        ``sub`` — str(user_id)
        ``exp`` — 30 days from now (configured via JWT_EXPIRATION_MINUTES)
        ``iat`` — now

    Uses HS256 with the app's SECRET_KEY.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
        "iat": now,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def authenticate_or_register(user_info: dict) -> User:
    """Find a user by Google ID or create one.

    This implements the auto-provisioning flow:

    1. Look up User by ``user_info["sub"]`` (google_id).
    2. If found → return existing User.
    3. If not found → create a new User with the provided info.

    Args:
        user_info: Dict from ``verify_google_token`` containing at
            least ``sub``, ``email``, and ``name``.

    Returns:
        User model instance (persisted).
    """
    google_id = user_info["sub"]
    email = user_info.get("email", "")
    name = user_info.get("name", "")

    user = await repository.get_by_google_id(google_id)
    if user is not None:
        return user

    return await repository.create(
        google_id=google_id,
        email=email,
        name=name,
    )
