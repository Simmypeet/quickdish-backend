from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.crud.order import create_order
from api.dependencies.state import get_state
from api.schemas.order import OrderCreate
from api.dependencies.id import get_customer_id
from api.state import State


router = APIRouter(
    prefix="/orders",
    tags=["order"],
)


@router.post(
    "/",
    description="""
        Creates a new order.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def create_order_api(
    payload: OrderCreate,
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
) -> int:
    return await create_order(state, customer_id, payload)
