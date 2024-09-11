from fastapi import Depends, FastAPI, Response
from fastapi.security import HTTPBearer

from api.crud.merchant import (
    create_restaurant,
    get_merchant,
    merchant_login,
    merchant_register,
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
    customer_register,
    customer_login,
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
async def customer_register_api(
    payload: CutomerRegister,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await customer_register(state, payload)


@app.post(
    "/customer/login",
    description="Logins user and returns a JWT token used for authentication.",
    tags=["customer"],
)
async def customer_login_api(
    payload: CustomerLogin,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await customer_login(state, payload)


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
async def customer_get(
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
async def merchant_register_id(
    payload: MerchantRegister,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await merchant_register(state, payload)


@app.post(
    "/merchant/login",
    description="Logins user and returns a JWT token used for authentication.",
    tags=["merchant"],
)
async def merchant_login_api(
    payload: MerchantLogin,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await merchant_login(state, payload)


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
async def merchant_get(
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
async def restaurant_create(
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
    responses={
        200: {"model": int},
    },
    dependencies=[Depends(HTTPBearer())],
    tags=["merchant", "restaurant"],
)
async def restaurant_get(
    response: Response,
    state: State = Depends(get_state),
    result: int = Depends(get_merchant_id),
) -> Restaurant:
    raise NotImplementedError()
