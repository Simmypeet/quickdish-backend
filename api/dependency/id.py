from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependency.state import get_state
from api.errors.session import (
    ExpiredSessionError,
    InvalidHeaderSchemeError,
    InvalidSessionTokenError,
)
from api.state import State

import jwt


class GetID:
    """
    Use this dependency to get the user ID from the JWT token stored in
    the `Authorization` header.
    """

    __id_name: str

    def __init__(
        self,
        id_name: str,
    ):
        self.__id_name = id_name

    def __call__(
        self,
        credentials: Annotated[
            HTTPAuthorizationCredentials, Depends(HTTPBearer())
        ],
        state: Annotated[State, Depends(get_state)],
    ) -> int:
        if credentials.scheme != "Bearer":
            raise InvalidHeaderSchemeError()

        try:
            return jwt.decode(  # type:ignore
                credentials.credentials,
                state.jwt_secret,
                algorithms=["HS256"],
            )[self.__id_name]

        except jwt.ExpiredSignatureError:
            raise ExpiredSessionError()

        except jwt.InvalidTokenError:
            raise InvalidSessionTokenError()

        except KeyError:
            raise InvalidSessionTokenError()


get_customer_id = GetID("customer_id")
get_merchant_id = GetID("merchant_id")
