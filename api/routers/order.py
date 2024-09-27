from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.crud.order import convert_to_schema, create_order, get_orders
from api.dependencies.state import get_state
from api.schemas.order import (
    CancelledOrder,
    Order,
    OrderCreate,
    OrderStatusFlag,
    OrderedOrder,
    PreparingOrder,
    ReadyOrder,
    SettledOrder,
)
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
    status: OrderStatusFlag | None = None,
    state: State = Depends(get_state),
) -> list[Order]:
    id, role = user

    return [
        await convert_to_schema(state, order)
        for order in await get_orders(state, id, role, restaurant_id, status)
    ]


@router.get(
    "/orders/{order_id}/status",
    description="""
        Gets the status information of the current order. The API returns a 
        JSON with a key named "type" that indicates the status of the order. The
        "type" cooresponds to the "*Status" schemas.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def get_order_status_api(
    order_id: int,
    user: tuple[int, Role] = Depends(get_user),
    state: State = Depends(get_state),
) -> (
    OrderedOrder | CancelledOrder | PreparingOrder | ReadyOrder | SettledOrder
):
    raise NotImplementedError()
