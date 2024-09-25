from decimal import Decimal
from api.crud.restaurant import get_restaurant
from api.errors import InvalidArgumentError, NotFoundError
from api.models.order import Order, OrderItem, OrderOption
from api.models.restaurant import Menu, Option, Customization
from api.schemas.order import OrderCreate, OrderStatus
from api.state import State

import time


async def create_order(
    state: State, customer_id: int, payload: OrderCreate
) -> int:
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
        status=str(OrderStatus.ORDERED),
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
