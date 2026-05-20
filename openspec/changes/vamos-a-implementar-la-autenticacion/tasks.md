# Tasks: Google OAuth Authentication with JWT

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~500 (290 backend + 210 mobile) |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: Backend Auth → PR 2: Mobile Auth |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: Medium

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Backend auth (models, service, security, endpoint, migration, tests) | PR 1 → `main` | Full backend independently verifiable via TestClient + dev mode |
| 2 | Mobile auth (sign-in hook, token storage, API injection, gated nav, tests) | PR 2 → `main` | Depends on PR 1 being deployed; code changes are isolated |

## Phase 1: Backend Foundation

- [x] 1.1 Create `modules/__init__.py` + `modules/auth/__init__.py` package markers
- [x] 1.2 Create `modules/auth/models.py` — User SQLAlchemy model (UUID PK, google_id, email, name, timezone, notification_hour, created_at)
- [x] 1.3 Create `modules/auth/schemas.py` — GoogleLoginRequest, TokenResponse, UserResponse (Pydantic)
- [x] 1.4 Add `JWT_EXPIRATION_MINUTES: int = 43200` to `core/config.py`
- [x] 1.5 Import User in `models/__init__.py` for Alembic autodiscovery
- [x] 1.6 Generate Alembic migration: `alembic revision --autogenerate -m "add_user_table"`

## Phase 2: Backend Core

- [x] 2.1 Create `modules/auth/repository.py` — `get_by_google_id`, `create` (async, SQLAlchemy)
- [x] 2.2 Create `modules/auth/service.py` — `verify_google_token`, `issue_jwt`, `authenticate_or_register`
- [x] 2.3 Create `modules/auth/router.py` — `POST /auth/google`
- [x] 2.4 Rewrite `core/security.py` — real JWT verification via python-jose + dev mode fallback
- [x] 2.5 Wire auth router into `api/v1/router.py` with prefix `/auth`
- [x] 2.6 Update `api/v1/plants.py` — `user_id: str` → `user_id: UUID` in endpoint signatures

## Phase 3: Mobile Auth

- [x] 3.1 Create `mobile/src/types/index.ts` — add `User` and `AuthResponse` interfaces
- [x] 3.2 Create `mobile/src/modules/auth/authStorage.ts` — `getToken`, `setToken`, `removeToken` via SecureStore
- [x] 3.3 Create `mobile/src/modules/auth/useGoogleSignIn.ts` — expo-auth-session Google provider hook
- [x] 3.4 Inject `Authorization: Bearer` header in `mobile/src/services/api.ts` from SecureStore
- [x] 3.5 Create `mobile/src/screens/LoginScreen.tsx` — Google sign-in button UI
- [x] 3.6 Rewrite `mobile/App.tsx` — auth-gated root (LoginScreen vs main navigation)

## Phase 4: Testing

- [x] 4.1 Write backend unit tests: mock `google-auth`, test valid/invalid token paths + dev mode
- [x] 4.2 Write backend integration tests: TestClient for `POST /auth/google`, expired JWT, invalid sig
- [x] 4.3 Write mobile unit tests: `authStorage.ts` token roundtrip with mocked SecureStore

## Implementation Order

Start with Phase 1 (model + schemas → migration), then Phase 2 (repo → service → router → security). Both form PR 1 and are testable via TestClient + dev mode. Phase 3 (mobile) is PR 2, isolated and dependent only on the backend API. Phase 4 tests should be written alongside their respective PRs.
