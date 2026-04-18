# FranceConnect Monopoly - Mock Authentication (FastAPI)

This project provides a minimal digital authentication device that simulates a FranceConnect-like OAuth flow.

## Features

- Mock login flow with redirect/callback.
- `state` validation to prevent CSRF in OAuth redirection.
- Signed cookie-based local session (`HttpOnly`, configurable `Secure` and `SameSite`).
- Protected endpoint (`/me`) requiring authentication.
- Logout endpoint that clears the session.
- Access token issuance endpoint for API clients.
- Token introspection endpoint for downstream services.

## Requirements

- Python 3.10+

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and adjust values as needed.

Important variables:

- `APP_BASE_URL`: base URL used for redirects (default `http://127.0.0.1:8001`)
- `PORT`: local API port (recommended `8001`)
- `SESSION_SECRET`: signing secret for the cookie session
- `SESSION_COOKIE_NAME`: session cookie key
- `SESSION_SECURE`: set `true` in HTTPS environments
- `SESSION_SAMESITE`: cookie same-site policy (`lax`, `strict`, `none`)
- `TOKEN_SECRET`: signing secret for issued access tokens
- `TOKEN_TTL_SECONDS`: access token lifetime (default `900`)
- `TOKEN_ISSUER`: token issuer string used in metadata

## Run

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

## Manual test scenario

1. Open `http://127.0.0.1:8001/auth/login` in your browser.
2. Follow redirects through `/mock-franceconnect/authorize` and `/auth/callback`.
3. Call `GET /me` to retrieve the authenticated mock user.
4. Call `POST /auth/logout`.
5. Call `GET /me` again: it should return `401 Authentication required`.

## SSO API flow (MVP)

1. Run this service (IdP) and authenticate once via browser on `/auth/login`.
2. Call `POST /auth/token` with the session cookie to retrieve an `access_token`.
3. Call protected APIs with `Authorization: Bearer <access_token>`.
4. Consumer services validate tokens against `GET /auth/introspect`.

### Example cURL flow

```bash
# 1) Authenticate and keep cookie
curl -i -c cookies.txt "http://127.0.0.1:8001/auth/login"

# 2) Follow browser redirects manually once (or open /auth/login in browser),
#    then request a token using the same cookie jar
curl -s -b cookies.txt -X POST "http://127.0.0.1:8001/auth/token"

# 3) Use token on consumer services (examples)
curl -H "Authorization: Bearer <token>" "http://127.0.0.1:8002/comptes"
curl -H "Authorization: Bearer <token>" "http://127.0.0.1:8003/cards"
curl -H "Authorization: Bearer <token>" "http://localhost:3000/api/rooms"
```

### Integrate a new API service

Set these variables on the target service:

- `SERVICE_AUTH_ENABLED=true`
- `FRANCECONNECT_BASE_URL=http://127.0.0.1:8001`
- `AUTH_REQUEST_TIMEOUT_SECONDS=2.5` (Python services) or `AUTH_REQUEST_TIMEOUT_MS=2500` (Node)

The target service must:

1. Read `Authorization: Bearer <token>`.
2. Call `GET /auth/introspect` on FranceConnect.
3. Allow request only when `active=true`.

## Endpoints

- `GET /` healthcheck
- `GET /auth/login` start authentication
- `GET /mock-franceconnect/authorize` mocked provider authorize endpoint
- `GET /auth/callback` callback consuming `code` and `state`
- `GET /me` protected user profile
- `POST /auth/logout` clear session
- `POST /auth/token` issue `access_token` from authenticated session
- `GET /auth/introspect` validate bearer token
- `GET /auth/config` return MVP auth metadata
- `GET /jwks-or-config` simplified discovery helper
