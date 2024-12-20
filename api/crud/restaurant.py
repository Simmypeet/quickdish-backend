from fastapi import UploadFile
from fastapi.responses import FileResponse

from api.configuration import Configuration
from api.crud.merchant import get_merchant
from api.errors import ConflictingError, InvalidArgumentError, NotFoundError
from api.errors.authentication import UnauthorizedError
from api.models.restaurant import Customization, Option, Restaurant
from api.models.restaurant import Menu
from api.schemas.restaurant import (
    CustomizationCreate,
    MenuCreate,
    RestaurantCreate,
)
from api.state import State
from api.schemas.customer import CustomerReview as CustomerReviewSchema
from api.models.customer import CustomerReview

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
        open=False,
        canteen_id=restaurant_create.canteen_id,
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


async def open_restaurant(
    state: State, restaurant_id: int, merchant_id: int
) -> None:
    """Open a restaurant."""
    restaurant = await get_restaurant(state, restaurant_id)

    if restaurant.merchant_id != merchant_id:
        raise UnauthorizedError("merchant does not own this restaurant")

    if restaurant.open:
        return

    restaurant.open = True
    state.session.commit()


async def close_restaurant(
    state: State, restaurant_id: int, merchant_id: int
) -> None:
    """Close a restaurant."""
    restaurant = await get_restaurant(state, restaurant_id)

    if restaurant.merchant_id != merchant_id:
        raise UnauthorizedError("merchant does not own this restaurant")

    if not restaurant.open:
        return

    restaurant.open = False
    state.session.commit()


async def upload_restaurant_image(
    state: State,
    configuration: Configuration,
    restaurant_id: int,
    image: UploadFile,
    merchant_id: int,
) -> str:
    """Upload an image for the restaurant."""
    restaurant = await get_restaurant(state, restaurant_id)

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own this restaurant")

    # Save the image
    image_directory = os.path.join(
        configuration.application_data_path, "restaurants", str(restaurant_id)
    )

    image_path = await configuration.upload_image(image, image_directory)
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


async def create_menu(
    state: State,
    restaurant_id: int,
    menu: MenuCreate,
    merchant_id: int,
) -> int:
    """Create a new menu for a restaurant."""
    # check if the price is valid
    if menu.price < 0:
        raise InvalidArgumentError("price can't be negative")

    if menu.estimated_prep_time is not None and menu.estimated_prep_time < 0:
        raise InvalidArgumentError("estimated prep time can't be negative")

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


async def update_menu(state: State, menu_id: int, menu: MenuCreate) -> int:
    existing_menu = (
        state.session.query(Menu).filter(Menu.id == menu_id).first()
    )
    if not existing_menu:
        raise NotFoundError("menu not found")

    existing_menu.name = menu.name
    existing_menu.description = menu.description
    existing_menu.price = menu.price
    existing_menu.estimated_prep_time = menu.estimated_prep_time

    state.session.commit()
    return existing_menu


async def get_restaurant_menus(
    state: State,
    restaurant_id: int,
) -> list[Menu]:
    """Get all menus for a restaurant."""
    # check if the restaurant exists
    menus = (
        state.session.query(Menu)
        .filter(Menu.restaurant_id == restaurant_id)
        .all()
    )

    return menus


async def upload_menu_image(
    state: State,
    configuration: Configuration,
    menu_id: int,
    image: UploadFile,
    merchant_id: int,
) -> str:
    """Upload an image for the restaurant."""
    menu = await get_menu(state, menu_id)
    restaurant = await get_restaurant(state, menu.restaurant_id)  # type:ignore

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own the restaurant")

    image_directory = os.path.join(
        configuration.application_data_path, "menus", str(menu_id)
    )

    image_path = await configuration.upload_image(image, image_directory)

    menu.image = image_path  # type:ignore
    state.session.commit()

    return image_path


async def get_menu_image(state: State, menu_id: int) -> FileResponse | None:
    menu = state.session.query(Menu).filter(Menu.id == menu_id).first()

    if not menu:
        raise NotFoundError("menu not found")

    if not menu.image:  # type:ignore
        return None

    return FileResponse(menu.image)  # type:ignore


async def create_customization(
    state: State,
    menu_id: int,
    customization: CustomizationCreate,
    merchant_id: int,
) -> int:
    """Create a new customization for a menu."""
    # check if the menu exists
    restaurant = (
        state.session.query(Restaurant)
        .filter((Menu.id == menu_id) & (Restaurant.id == Menu.restaurant_id))
        .first()
    )

    if not restaurant:
        raise NotFoundError("menu not found")

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own the restaurant")

    # check if the option with the same name in this customization exists
    found_option: set[str] = set()
    for option in customization.options:
        if option.extra_price is not None and option.extra_price < 0:
            raise InvalidArgumentError("extra price can't be negative")

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

    customizations = (
        state.session.query(Customization)
        .filter(Customization.menu_id == menu_id)
        .all()
    )
    return customizations


async def get_restaurant_reviews(
    restaurant_id: int, state: State
) -> list[CustomerReviewSchema]:

    reviews = (
        state.session.query(CustomerReview)
        .filter(CustomerReview.restaurant_id == restaurant_id)
        .all()
    )

    return [CustomerReviewSchema.model_validate(review) for review in reviews]


async def search_restaurant(query: str, limit: int, state: State) -> list[int]:
    if limit < 1:
        raise InvalidArgumentError("limit must be greater than 0")

    restaurants = (
        state.session.query(Restaurant)
        .filter(
            Restaurant.name.ilike(f"%{query}%")
            | Restaurant.address.ilike(f"% {query}%")
        )
        .limit(limit)
        .all()
    )

    return [restaurant.id for restaurant in restaurants]
