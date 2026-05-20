"""Real JWT verification via python-jose + dev mode fallback.

**Dev mode**: If ``GOOGLE_CLIENT_ID`` equals ``placeholder-local-dev``
and no JWT is provided, return a mock ``UserResponse``. If a JWT is
provided, decode it normally — this enables mixed-mode testing where
real tokens can be tried against a dev instance.

**Production**: Decode the JWT, extract ``sub`` (user UUID), fetch the
``User`` from the database, and return a ``UserResponse``.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select

from app.core.config import settings
from app.core.database import async_session_factory
from app.modules.auth.models import User
from app.modules.auth.schemas import UserResponse

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> UserResponse:
    """FastAPI dependency that returns the authenticated user.

    Resolution order:

    1. **No JWT + dev mode** — ``GOOGLE_CLIENT_ID`` is the placeholder
       AND no ``Authorization`` header → return a mock ``UserResponse``.
       This lets the entire API work locally without a frontend.

    2. **JWT present** — decode with ``python-jose`` (HS256), extract
       ``sub``, fetch the ``User`` from PostgreSQL, return ``UserResponse``.

    3. **JWT absent in production** — raise ``401``.
    4. **JWT invalid / expired / wrong user** — raise ``401``.

    Returns:
        ``UserResponse`` Pydantic schema (not the ORM model).

    Raises:
        ``HTTPException(401)`` — on missing/invalid/expired tokens.
    """
    # ── Case 1 & 3: no JWT provided ──────────────────────────────
    if credentials is None:
        if settings.GOOGLE_CLIENT_ID == "placeholder-local-dev":
            return UserResponse(
                id="00000000-0000-0000-0000-000000000001",
                email="dev@folia.app",
                name="Dev User",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # ── Case 2 & 4: JWT provided, decode it ──────────────────────
    try:
        payload: dict = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject claim",
            )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {exc}",
        )

    # ── Fetch User from DB ───────────────────────────────────────
    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.id == user_id),
        )
        user: User | None = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return UserResponse.model_validate(user)
