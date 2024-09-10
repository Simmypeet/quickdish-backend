from fastapi import Depends, FastAPI, Response
from api.schemas.customer import CustomerLogin
from api.dependency.state import get_state
from api.state import State
from api.crud.customer import (
    AuthenticationResponse,
    ConflictingCustomerError,
    CutomerRegister,
    AuthenticationError,
    customer_register,
    customer_login,
)

app = FastAPI()


@app.post(
    "/customer/register",
    responses={
        409: {"model": ConflictingCustomerError},
        200: {"model": AuthenticationResponse},
    },
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
        401: {"model": AuthenticationError},
        200: {"model": AuthenticationResponse},
    },
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
