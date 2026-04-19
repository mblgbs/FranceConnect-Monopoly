import os
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse

from .models import MessageResponse, MockUser, SessionPayload
from .session import clear_session, get_session, set_session


router = APIRouter(prefix="/auth", tags=["auth"])
mock_router = APIRouter(prefix="/mock-franceconnect", tags=["mock-provider"])

APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")


@router.get("/login")
def login() -> RedirectResponse:
    state = secrets.token_urlsafe(24)
    redirect_uri = f"{APP_BASE_URL}/auth/callback"
    query = urlencode({"state": state, "redirect_uri": redirect_uri})
    response = RedirectResponse(url=f"{APP_BASE_URL}/mock-franceconnect/authorize?{query}", status_code=status.HTTP_302_FOUND)
    set_session(response, SessionPayload(state=state))
    return response


@mock_router.get("/authorize")
def mock_authorize(
    state: str = Query(..., min_length=10),
    redirect_uri: str = Query(..., min_length=10),
) -> RedirectResponse:
    mock_code = secrets.token_urlsafe(18)
    query = urlencode({"code": mock_code, "state": state})
    return RedirectResponse(url=f"{redirect_uri}?{query}", status_code=status.HTTP_302_FOUND)


@router.get("/callback", response_model=MessageResponse)
def callback(
    request: Request,
    code: str = Query(..., min_length=8),
    state: str = Query(..., min_length=10),
) -> Response:
    session = get_session(request)
    if not session.state:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth state in session")
    if not secrets.compare_digest(state, session.state):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OAuth state")

    # In a real provider integration, `code` would be exchanged for user info at token/userinfo endpoints.
    user = MockUser(
        sub=f"mock-{code[:8]}",
        given_name="Jean",
        family_name="Dupont",
        email="jean.dupont@example.fr",
    )
    response = Response(
        content=MessageResponse(message="Authentication success").model_dump_json(),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )
    set_session(response, SessionPayload(user=user))
    return response


@router.post("/logout", response_model=MessageResponse)
def logout() -> Response:
    response = Response(
        content=MessageResponse(message="Logged out").model_dump_json(),
        media_type="application/json",
        status_code=status.HTTP_200_OK,
    )
    clear_session(response)
    return response
