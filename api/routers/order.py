from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.crud.order import create_order, get_orders
from api.dependencies.state import get_state
from api.schemas.order import Order, OrderCreate, OrderStatus
from api.dependencies.id import Role, get_customer_id, get_user
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


@router.get(
    "/",
    description="""
        Gets all orders for the customer or merchant based on the JWT token.
        If authenticated as a customer, the customer's orders are returned.
        If authenticated as a merchant, the orders of all restaurants owned by 
        the merchant are returned.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def get_orders_api(
    user: tuple[int, Role] = Depends(get_user),
    restaurant_id: int | None = None,
    status: OrderStatus | None = None,
    state: State = Depends(get_state),
) -> list[Order]:
    id, role = user

    return [
        order
        for order in await get_orders(state, id, role, restaurant_id, status)
    ]
