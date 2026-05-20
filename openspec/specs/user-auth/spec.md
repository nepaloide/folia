# user-auth Specification

## Purpose

The user-auth capability provides Google OAuth-based authentication across the stack: mobile sign-in, backend ID token verification, JWT session management, and user auto-provisioning. Enables per-user data isolation for all future features.

## Requirements

### Requirement: Google OAuth Login

The backend MUST expose `POST /api/v1/auth/google` that accepts a Google ID token, verifies it via `google-auth`, and returns a JWT.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| GL-1 | Valid token returns JWT | A valid Google ID token for the configured `GOOGLE_CLIENT_ID` | POST `{id_token}` to `/api/v1/auth/google` | Return `{access_token, token_type: "bearer", user{id, email, name}}` with 200 |
| GL-2 | Invalid token returns 401 | An expired, forged, or wrong-audience ID token | POST it to `/api/v1/auth/google` | Return 401 with `detail: "Invalid Google ID token"` |

### Requirement: JWT Session Tokens

The backend MUST issue JWTs with 30-day expiry containing `sub` (user UUID) and `exp`, encoded with `python-jose`/`HS256` using `SECRET_KEY`. The `get_current_user` dependency MUST decode the JWT, fetch the User from DB, and return the User model.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| JT-1 | Expired JWT rejected | A JWT issued 31 days ago | `get_current_user` decodes it | Raise 401 |
| JT-2 | Valid JWT returns user | A valid JWT with `sub` matching an existing user UUID | `get_current_user` decodes and fetches user | Return the matching User |
| JT-3 | Invalid signature rejected | A JWT signed with a different key | `get_current_user` decodes it | Raise 401 |

### Requirement: User Auto-Provisioning

The backend MUST create a User record on first Google login and return existing records on subsequent logins. The User model MUST include: `id` (UUID PK), `google_id`, `email`, `name`, `timezone`, `notification_hour`, `created_at`.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| UP-1 | First login creates user | No user exists with `google_id = "12345"` | Verified token with `sub: "12345"`, `email: "a@b.com"`, `name: "A B"` is processed | New User created with those fields, response includes new user |
| UP-2 | Returning login reuses user | User exists with `google_id = "12345"` | Verified token with `sub: "12345"` is processed | Existing User returned, no INSERT |

### Requirement: Dev Mode Fallback

When `GOOGLE_CLIENT_ID` equals `placeholder-local-dev`, `get_current_user` MUST return a mock User without requiring a JWT.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| DM-1 | Placeholder returns mock | `GOOGLE_CLIENT_ID` is `placeholder-local-dev` | Request without `Authorization` hits a protected endpoint | Return mock user with fixed UUID and `dev@folia.app` |
| DM-2 | Real client ID rejects | `GOOGLE_CLIENT_ID` is a real Google-issued ID | Request without `Authorization` hits a protected endpoint | Raise 401 |

### Requirement: Mobile Sign-In

The mobile app MUST use `expo-auth-session` for Google sign-in, POST the ID token to the backend, and store the returned JWT in `expo-secure-store`.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| MS-1 | Sign-in stores token | User is on login screen | User taps "Sign in with Google" and completes consent flow | ID token POSTed to backend, returned `access_token` stored in SecureStore |

### Requirement: Token Persistence

The mobile app MUST persist the JWT in `expo-secure-store` and load it on app startup.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| TP-1 | Token survives restart | A stored JWT in `expo-secure-store` | App restarts | Token loaded from storage and available for subsequent API calls |

### Requirement: Auth-Gated Navigation

The mobile app MUST show the login screen when no JWT exists and the main tab navigation when a valid JWT is present.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| AN-1 | No token shows login | No JWT in SecureStore | App launches | Login screen displayed |
| AN-2 | Valid token shows app | Valid JWT in SecureStore | App launches | Main tab navigation displayed |

### Requirement: Auth Header Injection

The mobile API client MUST include `Authorization: Bearer <token>` on every request when a token exists. When no token exists, the header MUST be omitted.

| ID | Scenario | GIVEN | WHEN | THEN |
|----|----------|-------|------|------|
| AH-1 | Token included in requests | Stored JWT in SecureStore | Any API request is made | `Authorization: Bearer <token>` header is present |
| AH-2 | No token, no header | No JWT stored | Any API request is made | No `Authorization` header is sent |
