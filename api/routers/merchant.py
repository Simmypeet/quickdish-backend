from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.configuration import Configuration
from api.crud.merchant import get_merchant, login_merchant, register_merchant
from api.dependencies.configuration import get_configuration
from api.dependencies.state import get_state
from api.dependencies.id import get_merchant_id
from api.schemas.authentication import AuthenticationResponse
from api.schemas.merchant import (
    Merchant,
    MerchantLogin,
    MerchantRegister,
)
from api.state import State


router = APIRouter(
    prefix="/merchants",
    tags=["merchant"],
)


@router.post(
    "/register",
    description="""
        Registers a new user and returns a JWT token used for authentication.
    """,
)
async def register_merchant_api(
    payload: MerchantRegister,
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
) -> AuthenticationResponse:
    return await register_merchant(state, configuration, payload)


@router.post(
    "/login",
    description="Logins user and returns a JWT token used for authentication.",
)
async def login_merchant_api(
    payload: MerchantLogin,
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
) -> AuthenticationResponse:
    return await login_merchant(state, configuration, payload)


@router.get(
    "/me",
    dependencies=[Depends(HTTPBearer())],
    description="""
        Get the public information of the currently authenticated user.
    """,
)
async def get_current_merchant_api(
    state: State = Depends(get_state),
    result: int = Depends(get_merchant_id),
) -> Merchant:
    return await get_merchant(state, result)


@router.get(
    "/{merchant_id}",
    description="""
        Get the public information of a user by their ID.
    """,
)
async def get_merchant_by_id_api(
    merchant_id: int,
    state: State = Depends(get_state),
) -> Merchant:
    return await get_merchant(state, merchant_id)
