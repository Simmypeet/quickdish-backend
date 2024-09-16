from fastapi.datastructures import State

from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import UnauthorizedError
from api.models.restaurant import Restaurant
from api.models.menu import Menu
from api.schemas.menu import MenuCreate


async def create_menu(
    state: State,
    restaurant_id: int,
    menu: MenuCreate,
    merchant_id: int,
) -> int:
    """Create a new menu for a restaurant."""
    # check if the restaurant exists
    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise NotFoundError("restaurant not found")

    # check if the merchant owns the restaurant
    if restaurant.merchant_id != merchant_id:
        raise UnauthorizedError("merchant does not own the restaurant")

    # check if the menu with the same name in this restaurant exists
    existing_menu = (
        state.session.query(Menu)
        .filter(
            (Menu.name == menu.name) & (Menu.restaurant_id == restaurant_id)
        )
        .first()
    )

    if existing_menu:
        raise ConflictingError(
            "a menu with the same name already exists in this restaurant"
        )

    new_menu = Menu(
        name=menu.name,
        description=menu.description,
        price=menu.price,
        estimated_prep_time=menu.estimated_prep_time,
        restaurant_id=restaurant_id,
    )

    state.session.add(new_menu)
    state.session.commit()

    state.session.refresh(new_menu)

    return new_menu.id  # type:ignore
