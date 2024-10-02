from decimal import Decimal
from threading import Lock

from sqlalchemy import ColumnElement, false, or_
from api.crud.restaurant import get_restaurant
from api.dependencies.id import Role
from api.errors import InvalidArgumentError, NotFoundError
from api.errors.authentication import UnauthorizedError
from api.errors.internal import InternalServerError
from api.models.order import (
    CancelledOrder,
    Order,
    OrderItem,
    OrderOption,
    PreparingOrder,
    ReadyOrder,
    SettledOrder,
)
from api.models.restaurant import Menu, Option, Customization, Restaurant
from api.schemas.order import (
    CancelledOrderUpdate,
    OrderCancelledBy,
    OrderCreate,
    OrderNotification,
    OrderStatusFlag,
    OrderStatus,
    OrderItem as OrderItemSchema,
    Order as OrderSchema,
    CancelledOrder as CancelledOrderSchema,
    OrderStatusUpdate,
    OrderedOrder as OrderedOrderSchema,
    PreparingOrderUpdate,
    Queue,
    QueueChangeNotification,
    ReadyOrder as ReadyOrderSchema,
    ReadyOrderUpdate,
    SettledOrder as SettledOrderSchema,
    PreparingOrder as PreparingOrderSchema,
    SettledOrderUpdate,
    StatusChangeNotification,
)
from api.state import State

import time


class OrderEvent:
    """
    A class used for managing order notifications.
    """

    __notifications_by_order_id: dict[Order, list[OrderNotification]]
    __state: State
    __mutex: Lock

    def __init__(self, state: State) -> None:
        self.__notifications_by_order_id = {}
        self.__state = state
        self.__mutex = Lock()

    def register(self, order: Order) -> bool:
        """
        Registers the order so that it will recieve further notifications.

        Raises:
            InvalidArgumentError: if the `order` status is `SETTLED` or
                `CANCELLED`.

        Returns:
            bool: `True` if the `order` hasn't been registered before; `False`,
                otherwise.
        """

        with self.__mutex:
            if (
                order.status == OrderStatusFlag.SETTLED
                or order.status == OrderStatusFlag.CANCELLED
            ):
                raise InvalidArgumentError(
                    "the order is already settled or cancelled"
                )

            if order not in self.__notifications_by_order_id:
                self.__notifications_by_order_id[order] = []
                return True

            return False

    async def order_status_change(self, order: Order):
        """
        Creates a status change notification for the particular order (if
        registered). This as well creates a queue change notification for other
        orders in the same restaurant.
        """

        with self.__mutex:
            if order in self.__notifications_by_order_id:
                self.__notifications_by_order_id[order].append(
                    StatusChangeNotification(
                        order_id=order.id,
                        status=await get_order_status_no_validation(
                            self.__state, order
                        ),
                    )
                )

            if (
                order.status != OrderStatusFlag.SETTLED
                and order.status != OrderStatusFlag.CANCELLED
            ):
                return

            for other_order in self.__notifications_by_order_id:
                if other_order == order:
                    continue

                if other_order.restaurant_id != order.restaurant_id:
                    continue

                notification = QueueChangeNotification(
                    order_id=other_order.id,
                    queue=await get_order_queue_no_validation(
                        self.__state, other_order
                    ),
                )

                self.__notifications_by_order_id[other_order].append(
                    notification
                )

    async def get_notifications(
        self, order: Order
    ) -> list[OrderNotification] | None:
        """Gets the notifications for the particular order.

        Args:
            order (Order): The order to get notifications for.

        Returns:
            Returns `None` if the order isn't registered or there won't be any
            notifications. Returns a list notifications if has one; otherwise,
            an empty list is returned.

            The empty list is returned meaning the order is still registered
            but there are no notifications for it.
        """

        with self.__mutex:
            if order not in self.__notifications_by_order_id:
                return None

            notifications = self.__notifications_by_order_id[order]

            if (
                order.status == OrderStatusFlag.SETTLED
                or order.status == OrderStatusFlag.CANCELLED
            ):
                del self.__notifications_by_order_id[order]
            else:
                self.__notifications_by_order_id[order] = []

            return notifications


async def create_order(
    state: State, customer_id: int, payload: OrderCreate
) -> int:
    """Creates a new order placed by a customer."""

    # check if the restaurant exists
    restaurant = await get_restaurant(state, payload.restaurant_id)
    price_paid = Decimal(0)
    ordered_at = int(time.time())

    for order in payload.items:
        # check if the menu exists in the restaurant
        menu = (
            state.session.query(Menu).filter(Menu.id == order.menu_id).first()
        )

        if not menu:
            raise NotFoundError("menu with id {order.menu_id} not found")

        # check if the menu is actually in the same restaurant
        if menu.restaurant_id != restaurant.id:
            raise InvalidArgumentError(
                f"menu with id {order.menu_id} is not in restaurant with id {restaurant.id}"
            )

        if order.quantity < 1:
            raise InvalidArgumentError(
                f"menu with id {order.menu_id} must have a quantity of at least 1"
            )

        price_paid += Decimal(menu.price)

        seen_customizations = list[int]()

        # check if the option ids are a part of the menu
        for option_create in order.options:
            option_id = option_create.option_id

            result = (
                state.session.query(Option, Customization)
                .filter(
                    (Option.id == option_id)
                    & (Customization.id == Option.customization_id)
                )
                .first()
            )

            if result is None:
                raise NotFoundError(
                    f"the option with id {option_id} not found"
                )

            option = result[0]
            customization = result[1]

            if customization.menu_id != menu.id:
                raise InvalidArgumentError(
                    f"the option with id {option_id} is not in menu with id {menu.id}"
                )

            seen_customizations.append(customization.id)

            if option.extra_price is not None:
                price_paid += Decimal(option.extra_price)

        # check if all the required customizations are present
        required_menu_customizations = (
            state.session.query(Customization)
            .filter(
                (Customization.menu_id == menu.id) & (Customization.required)
            )
            .all()
        )

        for required_customization in required_menu_customizations:
            if required_customization.id not in seen_customizations:
                raise InvalidArgumentError(
                    f"menu with id {menu.id} requires customization with id {required_customization.id}"
                )

        # check if the unique customizations are actually unique
        unique_customizations = (
            state.session.query(Customization)
            .filter(
                (Customization.menu_id == menu.id) & (Customization.unique)
            )
            .all()
        )

        for unique_customization in unique_customizations:
            # the number of customizations with the same id must be at most 1
            if seen_customizations.count(unique_customization.id) > 1:
                raise InvalidArgumentError(
                    f"menu with id {menu.id} requires customization with id {unique_customization.id} to be unique"
                )

    sql_order = Order(
        customer_id=customer_id,
        restaurant_id=restaurant.id,
        ordered_at=ordered_at,
        price_paid=price_paid,
        status=str(OrderStatusFlag.ORDERED),
    )

    state.session.add(sql_order)
    state.session.flush()

    state.session.refresh(sql_order)

    for order in payload.items:
        order_item = OrderItem(
            order_id=sql_order.id,
            menu_id=order.menu_id,
            quantity=order.quantity,
            extra_requests=order.extra_requests,
        )
        state.session.add(order_item)
        state.session.commit()

        state.session.refresh(order_item)

        for option in order.options:
            state.session.add(
                OrderOption(
                    order_item_id=order_item.id, option_id=option.option_id
                )
            )
            state.session.commit()

    return sql_order.id


async def get_order_status_no_validation(
    state: State, order: Order
) -> OrderStatus:
    match order.status:
        case OrderStatusFlag.ORDERED:
            return OrderedOrderSchema()

        case OrderStatusFlag.CANCELLED:
            cancelled_query = (
                state.session.query(CancelledOrder)
                .filter(CancelledOrder.order_id == order.id)
                .first()
            )

            if not cancelled_query:
                # this should never happen
                raise InternalServerError("can't find the cancelled order")

            return CancelledOrderSchema(
                cancelled_by=cancelled_query.cancelled_by,
                cancelled_time=cancelled_query.cancelled_time,
                reason=cancelled_query.reason,
            )

        case OrderStatusFlag.PREPARING:
            preparing_query = (
                state.session.query(PreparingOrder)
                .filter(PreparingOrder.order_id == order.id)
                .first()
            )

            if not preparing_query:
                # this should never happen
                raise InternalServerError("can't find the preparing order")

            return PreparingOrderSchema(
                prepared_at=preparing_query.prepared_at
            )

        case OrderStatusFlag.READY:
            ready_query = (
                state.session.query(ReadyOrder)
                .filter(ReadyOrder.order_id == order.id)
                .first()
            )

            if not ready_query:
                # this should never happen
                raise InternalServerError("can't find the ready order")

            return ReadyOrderSchema(ready_at=ready_query.ready_at)

        case OrderStatusFlag.SETTLED:
            settled_query = (
                state.session.query(SettledOrder)
                .filter(SettledOrder.order_id == order.id)
                .first()
            )

            if not settled_query:
                # this should never happen
                raise InternalServerError("can't find the settled order")

            return SettledOrderSchema(settled_at=settled_query.settled_at)


async def convert_to_schema(
    state: State,
    order: Order,
) -> OrderSchema:
    status = await get_order_status_no_validation(state, order)

    return OrderSchema(
        id=order.id,
        restaurant_id=order.restaurant_id,
        customer_id=order.customer_id,
        status=status,
        ordered_at=order.ordered_at,
        price_paid=order.price_paid,
        items=[OrderItemSchema.model_validate(item) for item in order.items],
    )


async def get_orders(
    state: State,
    user_id: int,
    role: Role,
    restaurant_id_filter: int | None,
    status_filter: list[OrderStatusFlag],
) -> list[Order]:
    status_filter_query: list[ColumnElement[bool]] = []
    for status in status_filter:
        status_filter_query.append(Order.status == status)

    match role:
        case Role.CUSTOMER:

            return (
                state.session.query(Order)
                .filter(
                    (Order.customer_id == user_id)
                    & (
                        or_(false(), *status_filter_query)
                        if len(status_filter_query) != 0
                        else True
                    )
                    & (
                        Order.restaurant_id == restaurant_id_filter
                        if restaurant_id_filter is not None
                        else True
                    )
                )
                .all()
            )

        case Role.MERCHANT:
            return (
                state.session.query(Order)
                .filter(
                    (Restaurant.merchant_id == user_id)
                    & (Order.restaurant_id == Restaurant.id)
                    & (
                        or_(false(), *status_filter_query)
                        if len(status_filter_query) != 0
                        else True
                    )
                    & (
                        Order.restaurant_id == restaurant_id_filter
                        if restaurant_id_filter is not None
                        else True
                    )
                )
                .all()
            )


async def get_order_with_validation(
    state: State,
    user_id: int,
    role: Role,
    order_id: int,
) -> Order:
    order = state.session.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise NotFoundError("order with id {order_id} not found")

    match role:
        case Role.CUSTOMER:
            if order.customer_id != user_id:
                raise UnauthorizedError("customer does not own the order")

        case Role.MERCHANT:
            result = (
                state.session.query(Restaurant)
                .filter(
                    (Restaurant.merchant_id == user_id)
                    & (Restaurant.id == order.restaurant_id)
                )
                .first()
            )

            if not result:
                raise UnauthorizedError("merchant does not own the order")

    return order


async def get_order_status(
    state: State, user_id: int, role: Role, order_id: int
) -> OrderStatus:
    order = await get_order_with_validation(state, user_id, role, order_id)

    return await get_order_status_no_validation(state, order)


async def update_order_status(
    state: State,
    order_event: OrderEvent,
    user_id: int,
    role: Role,
    order_id: int,
    status: OrderStatusUpdate,
) -> None:
    order = await get_order_with_validation(state, user_id, role, order_id)

    match role, order.status, status:
        # still can cancel the order
        case Role.CUSTOMER, OrderStatusFlag.ORDERED, CancelledOrderUpdate():
            state.session.add(
                CancelledOrder(
                    order_id=order.id,
                    cancelled_time=int(time.time()),
                    cancelled_by=OrderCancelledBy.CUSTOMER,
                    reason=status.reason,
                )
            )
            order.status = OrderStatusFlag.CANCELLED

            state.session.commit()
            await order_event.order_status_change(order)

        case Role.CUSTOMER, OrderStatusFlag.READY, SettledOrderUpdate():
            state.session.add(
                SettledOrder(order_id=order.id, settled_at=int(time.time()))
            )
            order.status = OrderStatusFlag.SETTLED

            state.session.commit()
            await order_event.order_status_change(order)

        case Role.CUSTOMER, _, CancelledOrderUpdate():
            raise InvalidArgumentError("order can't be cancelled anymore")

        case Role.CUSTOMER, _, SettledOrderUpdate():
            raise InvalidArgumentError(
                "order can only be settled when it's ready"
            )

        case Role.CUSTOMER, _, _:
            raise InvalidArgumentError(
                "only cancellation or settled are allowed"
            )

        case Role.MERCHANT, OrderStatusFlag.ORDERED, PreparingOrderUpdate():
            state.session.add(
                PreparingOrder(order_id=order.id, prepared_at=int(time.time()))
            )
            order.status = OrderStatusFlag.PREPARING

            state.session.commit()
            await order_event.order_status_change(order)

        case Role.MERCHANT, _, PreparingOrderUpdate():
            raise InvalidArgumentError("order can be prepared only once")

        case Role.MERCHANT, OrderStatusFlag.PREPARING, ReadyOrderUpdate():
            state.session.add(
                ReadyOrder(order_id=order.id, ready_at=int(time.time()))
            )
            order.status = OrderStatusFlag.READY

            state.session.commit()
            await order_event.order_status_change(order)

        case Role.MERCHANT, _, ReadyOrderUpdate():
            raise InvalidArgumentError(
                "order can be ready after it's prepared"
            )

        case (
            Role.MERCHANT,
            (OrderStatusFlag.PREPARING | OrderStatusFlag.ORDERED),
            CancelledOrderUpdate(),
        ):
            state.session.add(
                CancelledOrder(
                    order_id=order.id,
                    cancelled_time=int(time.time()),
                    cancelled_by=OrderCancelledBy.MERCHANT,
                    reason=status.reason,
                )
            )
            order.status = OrderStatusFlag.CANCELLED

            state.session.commit()
            await order_event.order_status_change(order)

        case (Role.MERCHANT, _, CancelledOrderUpdate()):
            raise InvalidArgumentError("order can't be cancelled anymore")

        case Role.MERCHANT, _, SettledOrderUpdate():
            raise InvalidArgumentError("order can't be settled by merchant")


async def get_order_queue(
    state: State, user_id: int, role: Role, order_id: int
) -> Queue:
    order = await get_order_with_validation(state, user_id, role, order_id)

    return await get_order_queue_no_validation(state, order)


async def get_restaurant_queue(
    state: State,
    restaurant_id: int,
) -> Queue:
    orders = (
        state.session.query(Order)
        .filter(
            (Order.restaurant_id == restaurant_id)
            & (
                (Order.status == OrderStatusFlag.ORDERED)
                | (Order.status == OrderStatusFlag.PREPARING)
            )
        )
        .all()
    )

    return __calculate_queue_from_prior_orders(state, orders)


def __calculate_queue_from_prior_orders(
    state: State, prior_orders: list[Order]
) -> Queue:
    estimated_time = 0

    for prior_order in prior_orders:
        for order_item in prior_order.items:
            menu = (
                state.session.query(Menu)
                .filter(Menu.id == order_item.menu_id)
                .first()
            )

            if not menu:
                raise InternalServerError(
                    "can't find the menu for the order item"
                )

            estimated_time += (
                menu.estimated_prep_time if menu.estimated_prep_time else 1
            ) * order_item.quantity

    return Queue(queue_count=len(prior_orders), estimated_time=estimated_time)


async def get_order_queue_no_validation(state: State, order: Order) -> Queue:
    prior_orders = (
        state.session.query(Order)
        .filter(
            (Order.restaurant_id == order.restaurant_id)
            & (Order.ordered_at <= order.ordered_at)
            & (Order.id < order.id)
            & (
                (Order.status == OrderStatusFlag.ORDERED)
                | (Order.status == OrderStatusFlag.PREPARING)
            )
        )
        .all()
    )

    return __calculate_queue_from_prior_orders(state, prior_orders)
