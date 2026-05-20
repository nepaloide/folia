"""Auth router — Google OAuth login endpoint.

POST /auth/google  →  exchange ID token for JWT
"""

from fastapi import APIRouter, HTTPException, status

from app.modules.auth.schemas import GoogleLoginRequest, TokenResponse, UserResponse
from app.modules.auth import service

router = APIRouter(tags=["auth"])


@router.post("/google", response_model=TokenResponse)
async def google_login(body: GoogleLoginRequest):
    """Exchange a Google ID token for a JWT session token.

    * Validates the Google ID token via google-auth.
    * Auto-provisions a User record on first login.
    * Returns a signed JWT (30-day expiry) and the user profile.

    **Dev mode**: When ``GOOGLE_CLIENT_ID`` is ``placeholder-local-dev``,
    the ID token is not verified and a mock user is returned. No Google
    Cloud project is needed.
    """
    try:
        user_info = await service.verify_google_token(body.id_token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    user = await service.authenticate_or_register(user_info)
    access_token = await service.issue_jwt(user.id)

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )
