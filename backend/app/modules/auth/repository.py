"""Async repository for User persistence.

Uses `async_session_factory` directly from core.database.
Each function manages its own session lifecycle.
"""

from uuid import UUID

from sqlalchemy import select

from app.core.database import async_session_factory
from app.modules.auth.models import User


async def get_by_google_id(google_id: str) -> User | None:
    """Find a user by their Google ID.

    Returns the User instance, or None if not found.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.google_id == google_id),
        )
        return result.scalar_one_or_none()


async def get_by_id(user_id: UUID) -> User | None:
    """Find a user by their UUID primary key.

    Returns the User instance, or None if not found.
    """
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.id == user_id),
        )
        return result.scalar_one_or_none()


async def create(google_id: str, email: str, name: str) -> User:
    """Create and persist a new User.

    Args:
        google_id: The Google account's sub claim (unique).
        email: Verified email from Google.
        name: Display name from Google.

    Returns:
        The newly created User instance with server-defaults populated.
    """
    async with async_session_factory() as session:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
