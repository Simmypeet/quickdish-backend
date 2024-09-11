from fastapi import Depends, FastAPI, Response
from fastapi.security import HTTPBearer

from api.crud.merchant import (
    create_restaurant,
    get_merchant,
    login_merchant,
    register_merchant,
)
from api.dependency.id import get_customer_id, get_merchant_id
from api.dependency.state import get_state
from api.schemas.authentication import AuthenticationResponse
from api.schemas.customer import (
    Customer,
    CustomerLogin,
    CutomerRegister,
)
from api.schemas.merchant import (
    Merchant,
    MerchantLogin,
    MerchantRegister,
    RestaurantCreate,
    Restaurant,
)
from api.state import State
from api.crud.customer import (
    register_customer,
    login_customer,
    get_customer,
)

app = FastAPI()


@app.post(
    "/customer/register",
    description="""
        Registers a new user and returns a JWT token used for authentication.
    """,
    tags=["customer"],
)
async def register_customer_api(
    payload: CutomerRegister,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await register_customer(state, payload)


@app.post(
    "/customer/login",
    description="Logins user and returns a JWT token used for authentication.",
    tags=["customer"],
)
async def login_customer_api(
    payload: CustomerLogin,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await login_customer(state, payload)


@app.get(
    "/customer/",
    dependencies=[Depends(HTTPBearer())],
    description="""
        Get the customer information using the JWT token stored in the 
        `Authorization` header. This endpoint includes the customer's private
        information.
        """,
    tags=["customer"],
)
async def get_customer_api(
    state: State = Depends(get_state),
    result: int = Depends(get_customer_id),
) -> Customer:
    return await get_customer(
        state,
        result,
    )


@app.post(
    "/merchant/register",
    description="""
        Registers a new user and returns a JWT token used for authentication.
    """,
    tags=["merchant"],
)
async def register_merchant_api(
    payload: MerchantRegister,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await register_merchant(state, payload)


@app.post(
    "/merchant/login",
    description="Logins user and returns a JWT token used for authentication.",
    tags=["merchant"],
)
async def login_merchant_api(
    payload: MerchantLogin,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await login_merchant(state, payload)


@app.get(
    "/merchant/",
    dependencies=[Depends(HTTPBearer())],
    description="""
        Get the merchant information using the JWT token stored in the 
        `Authorization` header. This endpoint includes the merchant's private
        information.
        """,
    tags=["merchant"],
)
async def get_merchant_api(
    state: State = Depends(get_state),
    result: int = Depends(get_merchant_id),
) -> Merchant:
    return await get_merchant(
        state,
        result,
    )


@app.post(
    "/merchant/restaurant",
    dependencies=[Depends(HTTPBearer())],
    tags=["merchant", "restaurant"],
)
async def create_restaurant_api(
    restaurant: RestaurantCreate,
    state: State = Depends(get_state),
    result: int = Depends(get_merchant_id),
) -> int:
    return await create_restaurant(
        state,
        result,
        restaurant,
    )


@app.get(
    "/merchant/restaurant/{restaurant_id}",
    dependencies=[Depends(HTTPBearer())],
    tags=["merchant", "restaurant"],
)
async def get_restaurant(
    state: State = Depends(get_state),
    result: int = Depends(get_merchant_id),
) -> Restaurant:
    return await get_restaurant(state, result)
