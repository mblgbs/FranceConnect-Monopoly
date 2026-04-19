from pydantic import BaseModel, Field


class MockUser(BaseModel):
    sub: str = Field(..., description="FranceConnect unique subject identifier")
    given_name: str
    family_name: str
    email: str


class SessionPayload(BaseModel):
    state: str | None = None
    user: MockUser | None = None


class MessageResponse(BaseModel):
    message: str
