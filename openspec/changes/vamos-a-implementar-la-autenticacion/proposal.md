# Proposal: Google OAuth Authentication with JWT

## Intent

Users cannot log in or persist identity across sessions. The app displays a welcome screen with no auth gating, and the backend uses a mock `get_current_user` returning a fixed UUID. This change ships a complete Google OAuth flow on both backend and mobile, enabling per-user data isolation for all future features (plants, care, diagnosis).

## Scope

### In Scope
- Backend `modules/auth/` with router, schemas, models, service, repository
- User model (SQLAlchemy) + Alembic migration
- Google ID token verification → JWT session tokens (30-day, python-jose)
- Dev mode fallback: mock user when `GOOGLE_CLIENT_ID` is placeholder
- `get_current_user` returns User model (UUID PK)
- `POST /api/v1/auth/google` endpoint
- Mobile: `expo-auth-session` Google sign-in + `expo-secure-store` token persistence
- Mobile: auth header injection in `api.ts`
- Mobile: auth-gated navigation (login screen vs main tabs)
- Update `api/v1/plants.py` user_id type from `str` to `UUID`

### Out of Scope
- Apple Sign-In (deferred — Google-only MVP)
- Refresh token rotation (30-day JWT is acceptable for MVP)
- Password-based auth (the app uses OAuth-only by design)
- Role-based access control (all users are equal for now)

## Capabilities

### New Capabilities
- `user-auth`: Google OAuth login flow, JWT token issuance/verification, User CRUD (auto-provision on first login), user preferences (timezone, notification_hour)

### Modified Capabilities
None.

## Approach

Full modular `modules/auth/` matching `architecture.md`. Backend verifies Google ID tokens via `google-auth`, issues JWTs via `python-jose`. Mobile uses `expo-auth-session` for Google sign-in, stores tokens in `expo-secure-store`, injects `Authorization: Bearer` on every request. Auth flows:

1. **Login**: Mobile → Google OAuth → ID token → POST `/auth/google` → Backend verifies → upserts User → returns JWT
2. **Auth request**: Mobile sends JWT → `get_current_user` decodes → fetches User from DB → returns User model
3. **Dev mode**: If `GOOGLE_CLIENT_ID` is `placeholder-local-dev` and no valid JWT, return mock user

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/modules/auth/` | New | Full module (router, schemas, models, service, repository) |
| `backend/app/core/security.py` | Modified | JWT verification with User model |
| `backend/app/core/config.py` | Modified | Optionally add JWT_EXPIRATION_MINUTES |
| `backend/app/main.py` | Modified | Register auth router |
| `backend/app/api/v1/plants.py` | Modified | user_id from `str` to `UUID` |
| `backend/app/models/__init__.py` | Modified | Import User for Alembic discovery |
| `backend/alembic/versions/` | New | User table migration |
| `backend/.env` | Modified | Update placeholder values |
| `mobile/src/modules/auth/` | New | Google sign-in hook, auth storage utils |
| `mobile/src/services/api.ts` | Modified | Auth header injection via SecureStore |
| `mobile/src/types/index.ts` | Modified | Add User/AuthResponse types |
| `mobile/App.tsx` | Modified | Auth-gated navigation |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Real Google OAuth creds required for full flow | High | Dev mode fallback keeps development unblocked; document setup steps |
| Expo SDK 54 package compatibility | Medium | Verify `expo-auth-session` + `expo-secure-store` against current Expo SDK 54 docs |
| Alembic first migration (no prior migrations) | Medium | Ensure `models/__init__.py` imports User before autogenerate |
| `str`→`UUID` type change breaks existing mock-dependent code | Low | Update all `Depends(get_current_user)` signatures in one pass |

## Rollback Plan

Git revert the commit(s) for this change. The old flat `api/v1/plants.py` structure remains untouched — no files removed, only new `modules/auth/` added. To drop the migration: `alembic downgrade -1` before revert.

## Dependencies

- Real Google OAuth credentials (web client ID for backend, iOS/Android client ID for mobile) — user must create via Google Cloud Console
- Post-MVP: Refresh token rotation

## Success Criteria

- [ ] A user can sign in with Google on mobile and receive a valid JWT
- [ ] Backend verifies the JWT on protected endpoints and returns the correct User
- [ ] Dev mode returns mock user when Google creds are placeholders (no regression)
- [ ] New User records are created on first login (auto-provision)
- [ ] Token persists across app restarts (SecureStore)
- [ ] Unauthenticated users see login screen; authenticated users see main tabs
- [ ] Alembic migration creates the User table cleanly (up + down)
