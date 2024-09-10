from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependency.state import get_state
from api.schemas.session import (
    InvalidHeaderSchemeError,
    ExpiredSessionError,
    InvalidSessionTokenError,
    SessionError,
)
from api.state import State

import jwt


def get_customer_id(
    state: Annotated[State, Depends(get_state)],
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer())
    ],
) -> int | SessionError:
    """
    Use this dependency to get the customer ID from the JWT token stored in
    the `Authorization` header.
    """

    if credentials.scheme != "Bearer":
        return InvalidHeaderSchemeError()

    try:
        return jwt.decode(  # type:ignore
            credentials.credentials, state.jwt_secret, algorithms=["HS256"]
        )["customer_id"]

    except jwt.ExpiredSignatureError:
        return ExpiredSessionError()

    except jwt.InvalidTokenError:
        return InvalidSessionTokenError()
