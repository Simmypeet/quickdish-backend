from enum import Enum
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.configuration import Configuration
from api.dependencies.configuration import get_configuration
from api.errors.session import (
    ExpiredSessionError,
    InvalidHeaderSchemeError,
    InvalidSessionTokenError,
)

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
        configuration: Annotated[Configuration, Depends(get_configuration)],
    ) -> int:
        if credentials.scheme != "Bearer":
            raise InvalidHeaderSchemeError()

        try:
            return jwt.decode(  # type:ignore
                credentials.credentials,
                configuration.jwt_secret,
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


class Role(Enum):
    """The user role enumeration."""
    CUSTOMER = 0
    MERCHANT = 1


def get_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(HTTPBearer())
    ],
    configuration: Annotated[Configuration, Depends(get_configuration)],
) -> tuple[int, Role]:
    """
    Gets the user ID and role from the JWT token stored in the `Authorization`
    header.
    """
    if credentials.scheme != "Bearer":
        raise InvalidHeaderSchemeError()

    try:
        decoded = jwt.decode(  # type:ignore
            credentials.credentials,
            configuration.jwt_secret,
            algorithms=["HS256"],
        )

        if "customer_id" in decoded:
            return int(decoded["customer_id"]), Role.CUSTOMER
        elif "merchant_id" in decoded:
            return int(decoded["merchant_id"]), Role.MERCHANT

        raise InvalidSessionTokenError()

    except jwt.ExpiredSignatureError:
        raise ExpiredSessionError()

    except jwt.InvalidTokenError:
        raise InvalidSessionTokenError()

    except KeyError:
        raise InvalidSessionTokenError()
