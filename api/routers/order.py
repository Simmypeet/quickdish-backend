from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sse_starlette.sse import EventSourceResponse

from api.crud.order import (
    convert_to_schema,
    create_order,
    get_order_status,
    get_order_status_no_validation,
    get_order_with_validation,
    get_orders,
    get_order_queue,
    get_restaurant_queue,
    update_order_status,
    OrderEvent,
)
from api.dependencies.order import get_order_event
from api.dependencies.state import get_state
from api.errors import InvalidArgumentError
from api.schemas.order import (
    Order,
    OrderCreate,
    OrderItem,
    OrderStatus,
    OrderStatusFlag,
    OrderStatusUpdate,
    Queue,
)
from api.dependencies.id import Role, get_customer_id, get_user
from api.state import State

import asyncio


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
    status: str | None = None,
    state: State = Depends(get_state),
) -> list[Order]:
    try:
        id, role = user

        statuses = []

        if status is not None:
            split_status = status.split("|")
            statuses = [OrderStatusFlag[status] for status in split_status]

        return [
            await convert_to_schema(state, order)
            for order in await get_orders(
                state, id, role, restaurant_id, statuses
            )
        ]

    except KeyError as e:
        raise InvalidArgumentError(f"status flag {e} is not valid")


@router.get(
    "/{order_id}/status",
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
) -> OrderStatus:
    return await get_order_status(state, user[0], user[1], order_id)


@router.put(
    "/{order_id}/status",
    description="""
        Updates the status of the order. Customer can only update `SETTLED` when
        the order is `READY` and `CANCELLED` when the order is `ORDERED`.
        Merchant can update `PREPARING`, `READY` in sequential order, and
        `CANCELLED` when the order is `ORDERED` or `PREPARING`.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def update_order_status_api(
    order_id: int,
    status: OrderStatusUpdate,
    user: tuple[int, Role] = Depends(get_user),
    order_event: OrderEvent = Depends(get_order_event),
    state: State = Depends(get_state),
) -> str:
    await update_order_status(
        state, order_event, user[0], user[1], order_id, status
    )

    return "success"


@router.get(
    "/{order_id}/queues",
    description="Gets the queue of the given order",
)
async def get_order_queue_api(
    order_id: int,
    user: tuple[int, Role] = Depends(get_user),
    state: State = Depends(get_state),
) -> Queue:
    return await get_order_queue(state, user[0], user[1], order_id)


@router.get(
    "/queues",
    description="""
        Gets the queue of the restaurant that the customer must be waiting
    """,
)
async def get_restaurant_queue_api(
    restaurant_id: int, state: State = Depends(get_state)
) -> Queue:
    return await get_restaurant_queue(state, restaurant_id)


@router.get(
    "/{order_id}/events",
    description="""
        Returns a stream of events that are related to the order. The events are
        in the form of JSON objects. The stream is kept open until the order is
        settled, cancelled, or the connection is closed.
    """,
    dependencies=[Depends(HTTPBearer())],
    response_class=EventSourceResponse,
)
async def order_event_api(
    order_id: int,
    user: tuple[int, Role] = Depends(get_user),
    order_event: OrderEvent = Depends(get_order_event),
    state: State = Depends(get_state),
) -> EventSourceResponse:
    await order_event.register(order_id, user[0], user[1], state)

    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            notifications = await order_event.get_notifications(order_id)

            if notifications is None:
                break

            for notification in notifications:
                yield str(notification.model_dump_json())

            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())


@router.get(
    "/{order_id}",
    description="""
        Gets the order information of the given order ID.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def get_order_api(
    order_id: int,
    user: tuple[int, Role] = Depends(get_user),
    state: State = Depends(get_state),
) -> Order:
    order_model = await get_order_with_validation(
        state, user[0], user[1], order_id
    )
    status = await get_order_status_no_validation(state, order_model)

    return Order(
        id=order_model.id,
        restaurant_id=order_model.restaurant_id,
        customer_id=order_model.customer_id,
        items=[OrderItem.model_validate(item) for item in order_model.items],
        status=status,
        price_paid=order_model.price_paid,
        ordered_at=order_model.ordered_at,
    )
