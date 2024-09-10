from fastapi import Depends, FastAPI, Response
from api.state import State
from api.crud.customer import (
    CreateResponse,
    CustomerCreate,
    ConflictingUsernameError,
    create_customer,
)


app = FastAPI()


# State dependency
def get_state():
    state = State()
    try:
        yield state
    finally:
        state.session.close()


@app.post(
    "/customers/",
    responses={
        409: {"model": ConflictingUsernameError},
        200: {"model": CreateResponse},
    },
)
async def post_customer(
    customer_create: CustomerCreate,
    response: Response,
    state: State = Depends(get_state),
) -> CreateResponse | ConflictingUsernameError:
    result = await create_customer(state, customer_create)

    match result:
        case CreateResponse():
            response.status_code = 200
        case ConflictingUsernameError():
            response.status_code = 409

    return result
