"""
Placeholder security module.

Swappable with real Google OAuth verification later. Currently returns
a mock user ID so the API can be developed without a frontend.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> str:
    """Return a verified user ID.

    Current implementation returns a placeholder ID when no token is
    provided.  Replace the body of this function with real Google token
    verification using `google-auth` when the frontend is ready.
    """
    if credentials is None:
        # ----- DEVELOPMENT MODE -----
        # Return a fixed placeholder so we can build the API without auth.
        return "00000000-0000-0000-0000-000000000001"

    # TODO: verify the Google ID token using google-auth:
    #   from google.oauth2 import id_token
    #   from google.auth.transport import requests
    #   info = id_token.verify_oauth2_token(
    #       credentials.credentials,
    #       requests.Request(),
    #       settings.GOOGLE_CLIENT_ID,
    #   )
    #   return info["sub"]

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Real token verification not yet implemented",
    )
