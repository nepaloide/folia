## Exploration: Google OAuth Authentication

### Current State

Backend has a mock `get_current_user` in `security.py` that returns a fixed UUID when no token is provided (dev mode). Real Google OAuth verification is commented out. The `GOOGLE_CLIENT_ID` and `SECRET_KEY` env vars exist with placeholder values (`placeholder-local-dev` and `dev-secret-key-no-usar-en-produccion-123456`).

All dependencies are already in `requirements.txt` (`python-jose`, `google-auth`, `httpx`). No User model exists. Alembic is async-configured with zero migrations (only `versions/.gitkeep`). The `modules/` structure from `architecture.md` does not exist yet — the project uses a flat `api/v1/` layout with only `plants` registered.

The mobile app has a basic API client (`api.ts`) with no auth headers, no token storage, and no auth types. `App.tsx` is a simple welcome screen. No `modules/auth/` exists on either backend or mobile.

### Affected Areas

- `backend/app/modules/auth/` — **will create**: new auth module (router, schemas, models, service, repository)
- `backend/app/core/security.py` — **will update**: JWT verification replacing mock, integrate with User model
- `backend/app/core/config.py` — **may update**: add JWT_EXPIRATION setting
- `backend/app/main.py` — **will update**: register auth router
- `backend/app/api/v1/plants.py` — **minor change**: user_id type from `str` to `UUID`
- `backend/app/models/__init__.py` — **will update**: import User model for Alembic discovery
- `backend/alembic/versions/` — **will create**: User table migration
- `backend/.env` — **will update**: replace placeholder values (user must provide real Google OAuth client ID)
- `mobile/src/services/api.ts` — **will update**: add auth header injection, token storage via SecureStore
- `mobile/src/types/index.ts` — **will update**: add User type, AuthResponse type
- `mobile/src/modules/auth/` — **will create**: Google Sign-In hook, auth storage utilities
- `mobile/App.tsx` — **will update**: auth-gated navigation (login vs main)
- `mobile/package.json` — **will update**: add `expo-auth-session`, `expo-secure-store` dependencies

### Approaches

1. **Full modular (modules/auth/) with JWT — RECOMMENDED**
   - Create `backend/app/modules/auth/` with full layered structure (router, schemas, models, service, repository)
   - Google OAuth ID token verification → JWT session token issuance (via `python-jose`)
   - User model with `google_id`, `email`, `name`, `timezone`, `notification_hour`, `created_at`
   - Alembic migration for User table
   - `get_current_user` verifies JWT and returns User model from DB
   - Dev fallback: when `GOOGLE_CLIENT_ID` is placeholder, return mock user
   - Pros: Follows `architecture.md` exactly, clean separation, establishes module pattern for all future features, auth is self-contained
   - Cons: Slightly more upfront setup, creates first module so establishes patterns that will propagate
   - Effort: **Medium** (8-10 files backend, 5-7 files mobile)

2. **Flat structure (api/v1/auth.py)**
   - Add auth endpoints to `backend/app/api/v1/auth.py`
   - User model in `app/models/user.py` (single models directory)
   - Same auth flow, just flatter file layout
   - Pros: Less disruption, fewer new directories, quicker to build
   - Cons: Diverges from `architecture.md`, will need refactoring later to migrate to `modules/`, doesn't establish module pattern for future features (plants, care, diagnosis)
   - Effort: **Low-Medium**

3. **Stateless Google token verification (no JWT)**
   - Verify the Google ID token on EVERY request in `get_current_user`
   - No JWT issuance at all — the Google token is the auth token
   - Pros: No JWT management, simpler token strategy, no refresh token needed
   - Cons: Every request goes to Google's servers for verification (latency + rate limits), tightly coupled to Google identity flow, harder to implement token revocation
   - Effort: **Low** (server-side only, fewer moving parts)

### Recommendation

**Approach 1 — Full modular with JWT.** Auth is critical infrastructure. Doing it right the first time establishes the module pattern for all future features (plants, care, diagnosis) and follows the architecture doc exactly. All backend dependencies are already installed. Key design points:

- **User model** in `modules/auth/models.py` using the schema from `architecture.md` (UUID PK, google_id, email, name, timezone, notification_hour, created_at)
- **JWT claims**: `sub` = user UUID, `exp` = 30 days (configurable via `JWT_EXPIRATION_MINUTES`)
- **`get_current_user`** decodes JWT, fetches User from DB via `auth.repository`, returns User model
- **Dev fallback**: if `GOOGLE_CLIENT_ID` is the placeholder `"placeholder-local-dev"` and no valid JWT is present, return mock user as today. This keeps development uninterrupted until real credentials exist.
- **Mobile**: `expo-auth-session` with Google provider for sign-in, `expo-secure-store` for token persistence, auth header injection in `api.ts`

### Auth Flow (detailed)

1. **Mobile**: User taps "Sign in with Google" → `expo-auth-session` opens browser → user consents → Google returns ID token
2. **Mobile**: POST `{id_token}` to `POST /api/v1/auth/google`
3. **Backend** (`auth.service`): Verifies ID token via `google.oauth2.id_token.verify_oauth2_token` using `GOOGLE_CLIENT_ID`
4. **Backend** (`auth.repository`): Finds existing user by `google_id` or creates a new User record
5. **Backend** (`auth.service`): Generates JWT with `sub=user.id`, `exp=now+30d` via `python-jose.jwt.encode`
6. **Backend**: Returns `{access_token, token_type: "bearer", user: {id, email, name}}`
7. **Mobile**: Stores `access_token` in `expo-secure-store`
8. **Mobile** (`api.ts`): Injects `Authorization: Bearer <token>` on every subsequent request
9. **Backend** (`security.py`): `get_current_user` decodes JWT, fetches User from DB, returns User

### Sequence Diagram

```
Mobile App                Backend API                  Google          PostgreSQL
    │                         │                          │                │
    │  Google Sign-In         │                          │                │
    │──────────────────────────────────────────────────►  │                │
    │◄─────────────────────── ID token ────────────────── │                │
    │                         │                          │                │
    │  POST /auth/google      │                          │                │
    │  {id_token}             │                          │                │
    │────────────────────────►│                          │                │
    │                         │  verify_oauth2_token()    │                │
    │                         │─────────────────────────►│                │
    │                         │◄─────── {sub, email, ...}―│                │
    │                         │                          │                │
    │                         │  SELECT/INSERT user       │                │
    │                         │───────────────────────────│───────────────►│
    │                         │◄───────── User ──────────│────────────────│
    │                         │                          │                │
    │                         │  Sign JWT                 │                │
    │                         │  (python-jose, 30d)       │                │
    │                         │                          │                │
    │◄───────── {access_token, user} ─────────────────────│                │
    │                         │                          │                │
    │  Store token            │                          │                │
    │  (SecureStore)          │                          │                │
    │                         │                          │                │
    │  GET /plants            │                          │                │
    │  Authorization: Bearer..│                          │                │
    │────────────────────────►│                          │                │
    │                         │  Decode JWT               │                │
    │                         │  Fetch user               │                │
    │                         │───────────────────────────│───────────────►│
    │                         │◄───────── User ──────────│────────────────│
    │◄─────────── plants ────────────────────────────────│                │
```

### Risks

- **Real Google OAuth credentials**: The flow won't fully work without a real Google Cloud project + OAuth client ID for both web (backend) and native (mobile). This is external setup the user must do. Backend needs a Web client ID; mobile needs an iOS/Android client ID.
- **Expo SDK 54**: `expo-google-sign-in` is deprecated. Use `expo-auth-session` with Google provider. The `mobile/AGENTS.md` mandates reading exact Expo v54 docs before writing code.
- **Alembic first migration**: No existing migrations. The initial migration will create the entire User table structure. Must ensure `Base.metadata` includes User before autogenerate — `models/__init__.py` must import the User model.
- **Dev mode continuity**: The current mock `get_current_user` returns `str`. The real implementation should return a User model (or at minimum a UUID). All routes using `Depends(get_current_user)` will need their `user_id` parameter updated from `str` to `UUID` (or the User Pydantic schema).
- **No refresh token logic**: JWT with 30-day expiry is simple but not best practice. For MVP this is acceptable, but should be noted as tech debt for post-MVP.
- **Mobile navigation gating**: The app currently has no navigation structure. Adding auth means the navigation flow must handle: (1) unauthenticated → login screen, (2) authenticated → main tabs. This means navigation restructuring in the same change.

### Ready for Proposal

**Yes.** The user has a clear feature request, the architecture is well-defined in `architecture.md`, all backend dependencies are already installed, and there's prior exploration work saved. The proposal phase can proceed with confidence, though the user should be aware that:
1. Real Google OAuth credentials are an external blocker they need to handle
2. The mobile side requires Expo SDK 54-compatible packages which must be verified against current docs
3. This change will establish the module pattern that all future features will follow

### Return Envelope

**Status**: success
**Summary**: Exploration complete for `vamos-a-implementar-la-autenticacion`. Three approaches compared — full modular with JWT recommended. Auth flow documented with sequence diagram. Risks identified (Google credentials, Expo SDK 54, Alembic first migration, dev mode continuity).
**Artifacts**: `openspec/changes/vamos-a-implementar-la-autenticacion/exploration.md`
**Next**: sdd-propose
**Risks**: Real Google OAuth credentials required for full flow; Expo SDK 54 compatibility must be verified; dev mode mock type change (str→UUID) must be handled
**Skill Resolution**: paths-injected — 2 skills (_shared/sdd-phase-common.md, sdd-explore/SKILL.md)
