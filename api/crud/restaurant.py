from fastapi import UploadFile
from fastapi.responses import FileResponse

from api.crud.merchant import get_merchant
from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import UnauthorizedError
from api.models.restaurant import Customization, Option, Restaurant
from api.schemas.restaurant import (
    CustomizationCreate,
    RestaurantCreate,
)
from api.state import State

import os

async def create_restaurant(
    state: State, merchant_id: int, restaurant_create: RestaurantCreate
) -> int:
    # Checks if there's a restaurant with the same name
    existing_restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.name == restaurant_create.name)
        .first()
    )

    if existing_restaurant:
        raise ConflictingError(
            "a restaurant with the same name already exists"
        )

    # Check if the merchant exists
    merchant = await get_merchant(state, merchant_id)
    if not merchant:
        raise NotFoundError("merchant not found")

    new_restaurant = Restaurant(
        name=restaurant_create.name,
        address=restaurant_create.address,
        location=restaurant_create.location,
        merchant_id=merchant_id,
    )

    state.session.add(new_restaurant)
    state.session.commit()

    state.session.refresh(new_restaurant)

    return new_restaurant.id  # type:ignore


async def get_restaurant(state: State, restaurant_id: int) -> Restaurant:
    """Get a restaurant by its ID."""

    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise NotFoundError("restaurant not found")

    return restaurant


async def upload_restaurant_image(
    state: State, restaurant_id: int, image: UploadFile, merchant_id: int
) -> str:
    """Upload an image for the restaurant."""
    restaurant = await get_restaurant(state, restaurant_id)

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own this restaurant")

    # Save the image
    image_directory = os.path.join(
        state.application_data_path, "restaurants", str(restaurant_id)
    )

    image_path = await state.upload_image(image, image_directory)
    restaurant.image = image_path  # type:ignore

    state.session.commit()

    return image_path


async def get_restaurant_image(
    state: State, restaurant_id: int
) -> FileResponse | None:
    """
    Get the image of the restaurant. Returns None if the restaurant hasn't
    uploaded an image yet.
    """

    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise NotFoundError("restaurant not found")

    if not restaurant.image:  # type:ignore
        return None

    return FileResponse(restaurant.image)  # type:ignore










async def create_customization(
    state: State,
    menu_id: int,
    customization: CustomizationCreate,
    merchant_id: int,
) -> int:
    """Create a new customization for a menu."""
    # check if the menu exists
    menu = state.session.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise NotFoundError("menu not found")

    # check if the merchant owns the restaurant
    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == menu.restaurant_id)
        .first()
    )

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own the restaurant")

    # check if the option with the same name in this customization exists
    found_option: set[str] = set()
    for option in customization.options:
        if option.name in found_option:
            raise ConflictingError(
                f"an option {option.name} found more than once in the customization"
            )

        found_option.add(option.name)

    # check if the customization with the same title in this menu exists
    existing_customization = (
        state.session.query(Customization)
        .filter(
            (Customization.title == customization.title)
            & (Customization.menu_id == menu_id)
        )
        .first()
    )

    if existing_customization:
        raise ConflictingError(
            "a customization with the same title already exists in this menu"
        )

    new_customization = Customization(
        menu_id=menu_id,
        title=customization.title,
        description=customization.description,
        unique=customization.unique,
        required=customization.required,
    )

    state.session.add(new_customization)
    state.session.commit()

    state.session.refresh(new_customization)

    id = new_customization.id

    for option in customization.options:
        state.session.add(
            Option(
                customization_id=id,
                name=option.name,
                description=option.description,
                extra_price=option.extra_price,
            )
        )

    state.session.commit()

    return id


async def get_menu_customizations(
    state: State,
    menu_id: int,
) -> list[Customization]:
    """Get all customizations for a menu."""
    # check if the menu exists
    menu = state.session.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise NotFoundError("menu not found")

    customizations = (
        state.session.query(Customization)
        .filter(Customization.menu_id == menu_id)
        .all()
    )

    return customizations
