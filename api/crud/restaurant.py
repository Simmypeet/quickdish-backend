import os
from fastapi import UploadFile
from fastapi.responses import FileResponse
from api.crud.merchant import get_merchant
from api.errors import ConflictingError, FileContentTypeError, NotFoundError
from api.errors.authentication import UnauthorizedError
from api.errors.internal import InternalServerError
from api.models.restaurant import Restaurant
from api.schemas.restaurant import RestaurantCreate
from api.state import State


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
