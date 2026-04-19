# FranceConnect Monopoly - Mock Authentication (FastAPI)

This project provides a minimal digital authentication device that simulates a FranceConnect-like OAuth flow.

**Écosystème Monopoly :** l’API [services-Monopoly-](../services-Monopoly-/README.md#decouverte-des-services-ecosystem) expose `GET http://127.0.0.1:8004/ecosystem` pour lister les URLs de tous les microservices (dont ce mock en `8001` par défaut).

## Features

- Mock login flow with redirect/callback.
- `state` validation to prevent CSRF in OAuth redirection.
- Signed cookie-based local session (`HttpOnly`, configurable `Secure` and `SameSite`).
- Protected endpoint (`/me`) requiring authentication.
- Logout endpoint that clears the session.

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

- `APP_BASE_URL`: base URL used for redirects (default `http://127.0.0.1:8000`)
- `SESSION_SECRET`: signing secret for the cookie session
- `SESSION_COOKIE_NAME`: session cookie key
- `SESSION_SECURE`: set `true` in HTTPS environments
- `SESSION_SAMESITE`: cookie same-site policy (`lax`, `strict`, `none`)

## Run

```bash
uvicorn app.main:app --reload
```

## Manual test scenario

1. Open `http://127.0.0.1:8000/auth/login` in your browser.
2. Follow redirects through `/mock-franceconnect/authorize` and `/auth/callback`.
3. Call `GET /me` to retrieve the authenticated mock user.
4. Call `POST /auth/logout`.
5. Call `GET /me` again: it should return `401 Authentication required`.

## Endpoints

- `GET /` healthcheck
- `GET /auth/login` start authentication
- `GET /mock-franceconnect/authorize` mocked provider authorize endpoint
- `GET /auth/callback` callback consuming `code` and `state`
- `GET /me` protected user profile
- `POST /auth/logout` clear session
