from fastapi import Depends, FastAPI, Response
from fastapi.security import HTTPBearer

from api.dependency.customer import get_customer_id
from api.dependency.state import get_state
from api.schemas.customer import (
    AuthenticationError,
    AuthenticationResponse,
    ConflictingCustomerError,
    Customer,
    CustomerLogin,
    CutomerRegister,
)
from api.schemas.session import (
    ExpiredSessionError,
    InvalidHeaderSchemeError,
    InvalidSessionTokenError,
    SessionError,
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
    responses={
        409: {
            "model": ConflictingCustomerError,
            "description": "An account with the same username or email already exists.",
        },
        200: {"model": AuthenticationResponse},
    },
    description="""
        Registers a new user and returns a JWT token used for authentication.
    """,
)
async def customer_register_api(
    payload: CutomerRegister,
    response: Response,
    state: State = Depends(get_state),
) -> AuthenticationResponse | ConflictingCustomerError:
    result = await customer_register(state, payload)

    match result:
        case AuthenticationResponse():
            response.status_code = 200
        case ConflictingCustomerError():
            response.status_code = 409

    return result


@app.post(
    "/customer/login",
    responses={
        401: {
            "model": AuthenticationError,
            "description": "Invalid username or password.",
        },
        200: {"model": AuthenticationResponse},
    },
    description="Logins user and returns a JWT token used for authentication.",
)
async def customer_login_api(
    payload: CustomerLogin,
    response: Response,
    state: State = Depends(get_state),
) -> AuthenticationResponse | AuthenticationError:
    result = await customer_login(state, payload)

    match result:
        case AuthenticationResponse():
            response.status_code = 200
        case AuthenticationError():
            response.status_code = 401

    return result


@app.get(
    "/customer/",
    dependencies=[Depends(HTTPBearer())],
    description="""
        Get the customer information using the JWT token stored in the 
        `Authorization` header. This endpoint includes the customer's private
        information.
        """,
    responses={
        200: {"model": Customer},
        400: {
            "model": InvalidHeaderSchemeError,
            "description": "The `Authorization` header scheme is not `Bearer`.",
        },
        401: {
            "model": ExpiredSessionError | InvalidSessionTokenError,
            "description": "The JWT token has expired or the token is invalid",
        },
        404: {
            "model": None,
            "description": "The customer with the ID in the token is not found",
        },
    },
)
async def customer_get(
    response: Response,
    state: State = Depends(get_state),
    result: int | SessionError = Depends(get_customer_id),
) -> Customer | SessionError | None:
    match result:
        case int():
            customer = await get_customer(
                state,
                result,
            )

            if customer is None:
                response.status_code = 404

            return customer

        case _:
            match result:
                case InvalidHeaderSchemeError():
                    response.status_code = 400

                case ExpiredSessionError():
                    response.status_code = 401

                case InvalidSessionTokenError():
                    response.status_code = 401

            return result
