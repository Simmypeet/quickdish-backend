from fastapi import UploadFile
from fastapi.responses import FileResponse

from api.crud.restaurant import get_restaurant
from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import UnauthorizedError
from api.models.restaurant import Restaurant
from api.models.menu import Menu
from api.schemas.menu import MenuCreate
from api.state import State

import os


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
    if restaurant.merchant_id != merchant_id:  # type:ignore
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


async def get_menu(state: State, menu_id: int) -> Menu:
    """Get a menu by its ID."""
    menu = state.session.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise NotFoundError("menu not found")

    return menu


async def get_restaurant_menus(
    state: State,
    restaurant_id: int,
) -> list[Menu]:
    """Get all menus for a restaurant."""
    # check if the restaurant exists
    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise NotFoundError("restaurant not found")

    menus = (
        state.session.query(Menu)
        .filter(Menu.restaurant_id == restaurant_id)
        .all()
    )

    return menus


async def upload_menu_image(
    state: State, menu_id: int, image: UploadFile, merchant_id: int
) -> str:
    """Upload an image for the restaurant."""
    menu = await get_menu(state, menu_id)
    restaurant = await get_restaurant(state, menu.restaurant_id)  # type:ignore

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own the restaurant")

    image_directory = os.path.join(
        state.application_data_path, "menus", str(menu_id)
    )

    image_path = await state.upload_image(image, image_directory)

    menu.image = image_path  # type:ignore
    state.session.commit()

    return image_path


async def get_menu_image(state: State, menu_id: int) -> FileResponse | None:
    menu = state.session.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise NotFoundError("restaurant not found")

    if not menu.image:  # type:ignore
        return None

    return FileResponse(menu.image)  # type:ignore
