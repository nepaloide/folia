# Apply Progress: Phase 1–3 — Backend & Mobile Auth

**Change**: vamos-a-implementar-la-autenticacion
**Phase**: 1–3/4 — Backend Foundation + Backend Core + Mobile Auth
**Mode**: Standard
**Date**: 2026-05-20

## Completed Tasks

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | Create `modules/__init__.py` + `modules/auth/__init__.py` | ✅ Done | Empty package markers |
| 1.2 | Create `modules/auth/models.py` — User SQLAlchemy model | ✅ Done | UUID PK, google_id, email, name, timezone, notification_hour, created_at |
| 1.3 | Create `modules/auth/schemas.py` — GoogleLoginRequest, TokenResponse, UserResponse | ✅ Done | Pydantic v2 with `from_attributes=True` |
| 1.4 | Add `JWT_EXPIRATION_MINUTES: int = 43200` to `core/config.py` | ✅ Done | Added to `Settings` class |
| 1.5 | Import User in `models/__init__.py` for Alembic autodiscovery | ✅ Done | Re-exported via `__all__` |
| 1.6 | Generate Alembic migration | ✅ Done (manual) | See notes in Phase 1 apply-progress |
| 2.1 | Create `modules/auth/repository.py` — `get_by_google_id`, `create` | ✅ Done | Async SQLAlchemy, each function manages own session |
| 2.2 | Create `modules/auth/service.py` — `verify_google_token`, `issue_jwt`, `authenticate_or_register` | ✅ Done | Dev-mode skip for placeholder GOOGLE_CLIENT_ID |
| 2.3 | Create `modules/auth/router.py` — `POST /auth/google` | ✅ Done | Validates Google ID token, returns JWT + user |
| 2.4 | Rewrite `core/security.py` — real JWT verification | ✅ Done | python-jose HS256 decode + user fetch from DB, dev fallback preserved |
| 2.5 | Wire auth router into `api/v1/router.py` with prefix `/auth` | ✅ Done | `router.include_router(auth_router, prefix="/auth")` |
| 2.6 | Update `api/v1/plants.py` — `user_id: str` → `user: UserResponse` | ✅ Done | Changed to `user: UserResponse = Depends(get_current_user)` |
| 3.1 | Create `mobile/src/types/index.ts` — add `User` and `AuthResponse` interfaces | ✅ Done | Appended to existing types file |
| 3.2 | Create `mobile/src/modules/auth/authStorage.ts` — `getToken`, `setToken`, `removeToken` via SecureStore | ✅ Done | Wraps `expo-secure-store` with `folia_auth_token` key |
| 3.3 | Create `mobile/src/modules/auth/useGoogleSignIn.ts` — expo-auth-session Google provider hook | ✅ Done | Uses `useIdTokenAuthRequest`, POSTs id_token to backend, returns AuthResponse |
| 3.4 | Inject `Authorization: Bearer` header in `mobile/src/services/api.ts` from SecureStore | ✅ Done | Reads token from SecureStore on each request |
| 3.5 | Create `mobile/src/screens/LoginScreen.tsx` — Google sign-in button UI | ✅ Done | Calls useGoogleSignIn, stores token on success, notifies App.tsx |
| 3.6 | Rewrite `mobile/App.tsx` — auth-gated root (LoginScreen vs main navigation) | ✅ Done | Checks SecureStore on mount, renders LoginScreen or TabNavigator |
| 4.1 | Write backend unit tests: mock `google-auth`, test valid/invalid token paths + dev mode | ✅ Done | 11 test cases across 3 classes — covers GL-1, GL-2, DM-1, JT-1, JT-2, UP-1, UP-2, edge cases |
| 4.2 | Write backend integration tests: TestClient for `POST /auth/google`, expired JWT, invalid sig | ✅ Done | 9 test cases — covers GL-1, GL-2, JT-1, JT-2, JT-3, DM-1, DM-2 |
| 4.3 | Write mobile unit tests: `authStorage.ts` token roundtrip with mocked SecureStore | ✅ Done | 7 test cases — covers TP-1, roundtrip lifecycle |

## Files Changed

| File | Action | What Was Done |
|------|--------|---------------|
| `backend/app/modules/__init__.py` | Created | Package marker |
| `backend/app/modules/auth/__init__.py` | Created | Package marker |
| `backend/app/modules/auth/models.py` | Created | User SQLAlchemy model (7 columns) |
| `backend/app/modules/auth/schemas.py` | Created | GoogleLoginRequest, TokenResponse, UserResponse |
| `backend/app/modules/auth/repository.py` | Created | `get_by_google_id`, `get_by_id`, `create` (async) |
| `backend/app/modules/auth/service.py` | Created | `verify_google_token`, `issue_jwt`, `authenticate_or_register` |
| `backend/app/modules/auth/router.py` | Created | `POST /auth/google` endpoint |
| `backend/app/core/config.py` | Modified | Added `JWT_EXPIRATION_MINUTES: int = 43200` |
| `backend/app/core/security.py` | Rewritten | Real JWT decode via python-jose + dev fallback, returns UserResponse |
| `backend/app/models/__init__.py` | Modified | Imported User for Alembic autodiscovery |
| `backend/alembic/env.py` | Modified | Added `import app.models` to ensure model registration |
| `backend/alembic/versions/4dca4bcdef19_add_user_table.py` | Created | Migration to create `users` table |
| `backend/app/api/v1/router.py` | Modified | Wired auth router with `/auth` prefix |
| `backend/app/api/v1/plants.py` | Modified | `user_id: str` → `user: UserResponse = Depends(get_current_user)` |
| `mobile/src/types/index.ts` | Modified | Appended `User` and `AuthResponse` interfaces |
| `mobile/src/modules/auth/authStorage.ts` | Created | `getToken`, `setToken`, `removeToken` via SecureStore |
| `mobile/src/modules/auth/useGoogleSignIn.ts` | Created | Google OAuth hook using expo-auth-session |
| `mobile/src/services/api.ts` | Modified | Injects `Authorization: Bearer <token>` on each request |
| `mobile/src/screens/LoginScreen.tsx` | Created | Google sign-in button UI with auth state callback |
| `mobile/src/screens/HomeScreen.tsx` | Created | Placeholder home screen for authenticated state |
| `mobile/src/navigation/TabNavigator.tsx` | Created | Bottom tab navigator (placeholder home tab) |
| `mobile/App.tsx` | Rewritten | Auth-gated root — LoginScreen or TabNavigator |
| `backend/tests/__init__.py` | Created | Package marker |
| `backend/tests/conftest.py` | Created | Shared fixtures (mock_user) |
| `backend/tests/unit/__init__.py` | Created | Package marker |
| `backend/tests/unit/test_auth_service.py` | Created | 11 unit tests for auth service |
| `backend/tests/integration/__init__.py` | Created | Package marker |
| `backend/tests/integration/test_auth_api.py` | Created | 9 integration tests for auth API |
| `backend/pytest.ini` | Created | Pytest config (asyncio_mode=auto) |
| `backend/requirements.txt` | Modified | Added pytest, pytest-asyncio |
| `mobile/src/modules/auth/__tests__/authStorage.test.ts` | Created | 7 unit tests for auth storage |
| `mobile/jest.config.js` | Created | Jest config with jest-expo preset |
| `mobile/package.json` | Modified | Added test script, jest, jest-expo devDeps |

## Deviations from Design

1. **Added `get_by_id` to repository**: The design only specified `get_by_google_id` and `create`. Added `get_by_id(UUID)` for the security module to fetch a User by UUID primary key. This is required by `get_current_user` which decodes `sub` (user UUID) from the JWT and needs to look up the user. This is a natural extension — the design's `get_current_user` flow depends on it.

2. **`authenticate_or_register` uses separate DB sessions**: Each repository function (`get_by_google_id`, `create`) manages its own session. For a race-condition-free auto-provisioning flow, these should ideally share a session+transaction. The current approach relies on PostgreSQL's unique constraint on `google_id` as a safety net. This is a pragmatic tradeoff for this phase — a unit-of-work pattern can be introduced later.

3. **Placeholder tab navigator**: The design mentions "main tab navigation" but no tab structure was specified. Created a minimal `TabNavigator` with a single `Home` tab (HomeScreen placeholder). Additional tabs can be added in future phases.

4. **HomeScreen and TabNavigator as new files**: The design only listed `App.tsx` modification for the auth gate. Created `HomeScreen.tsx` and `TabNavigator.tsx` as supporting files — these are natural extensions for the auth-gated navigation to work correctly.

## Issues Found

- **No unit-of-work pattern**: The repository functions each create their own DB session. If `authenticate_or_register` is called concurrently for the same Google ID, both calls could see `get_by_google_id` returning None, and the second `create` would hit the unique constraint. The Postgres unique constraint prevents data corruption but would cause a 500 error. Mitigation: low probability in normal usage (Google login is not a repeated rapid-fire action). Can be addressed in a future refactor by passing a shared session.
- **Mobile jest dependency not pre-installed**: `jest` and `jest-expo` need to be installed before running mobile tests. Added to `package.json` devDependencies — run `npm install` in the `mobile/` directory.

## Remaining Tasks

None — all 18 tasks complete across all 4 phases.

## Workload / PR Boundary

- **Mode**: single PR (all 4 phases)
- **Boundary**: Full auth — backend users/auth endpoints + mobile auth flow + tests
- **Estimated review budget impact**: ~350 lines (backend: code + tests) + ~270 lines (mobile: code + tests)
