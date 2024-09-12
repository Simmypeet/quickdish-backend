from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.crud.customer import get_customer, login_customer, register_customer
from api.dependencies.state import get_state
from api.dependencies.id import get_customer_id
from api.schemas.authentication import AuthenticationResponse
from api.schemas.customer import (
    CustomerLogin,
    CustomerRegister,
    PublicCustomer,
)
from api.state import State


router = APIRouter(
    prefix="/customers",
    tags=["customer"],
)


@router.post(
    "/register",
    description="""
        Registers a new user and returns a JWT token used for authentication.
    """,
)
async def register_customer_api(
    payload: CustomerRegister,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await register_customer(state, payload)


@router.post(
    "/login",
    description="Logins user and returns a JWT token used for authentication.",
)
async def login_customer_api(
    payload: CustomerLogin,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await login_customer(state, payload)


@router.get(
    "/me",
    dependencies=[Depends(HTTPBearer())],
    description="""
        Get the public information of the currently authenticated user.
        """,
)
async def get_current_customer_api(
    state: State = Depends(get_state),
    result: int = Depends(get_customer_id),
) -> PublicCustomer:
    return await get_customer(state, result)


@router.get(
    "/{customer_id}",
    description="""
        Get the public information of a user by their ID.
    """,
)
async def get_customer_by_id_api(
    customer_id: int,
    state: State = Depends(get_state),
) -> PublicCustomer:
    return await get_customer(state, customer_id)
