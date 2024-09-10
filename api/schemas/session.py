"""Contains Pydantic models for session-related errors."""
from pydantic import BaseModel


class InvalidHeaderSchemeError(BaseModel):
    error: str = "expected 'Bearer' scheme in the 'Authorization' header"


class ExpiredSessionError(BaseModel):
    error: str = (
        "session has expired; re-authenticate to continue using the service"
    )


class InvalidSessionTokenError(BaseModel):
    error: str = (
        "invalid session token; cannot authenticate the user with the given token"
    )


SessionError = (
    ExpiredSessionError | InvalidSessionTokenError | InvalidHeaderSchemeError
)
