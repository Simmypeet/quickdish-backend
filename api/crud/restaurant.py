import os
from fastapi import UploadFile
from api.crud.merchant import get_merchant
from api.errors import ConflictingError, NotFoundError
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


async def get_restaurant(
    state: State, restaurant_id: int, merchant_id: int
) -> Restaurant:
    """Get a restaurant by its ID."""

    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise NotFoundError("restaurant not found")

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own this restaurant")

    return restaurant


async def upload_restaurant_image(
    state: State, restaurant_id: int, image: UploadFile, merchant_id: int
) -> str:
    """Upload an image for the restaurant."""
    restaurant = await get_restaurant(state, restaurant_id, merchant_id)

    # Save the image
    image_directory = os.path.join(
        state.application_data_path, "restaurants", str(restaurant_id)
    )

    try:
        os.makedirs(image_directory, exist_ok=True)
    except OSError as e:
        raise InternalServerError(
            f"could not create image directory at {image_directory}: {e}"
        )

    if not os.path.isdir(image_directory):
        raise InternalServerError(
            f"{image_directory} is not a directory or not exists"
        )

    if not image.filename:
        raise InternalServerError("image filename is empty")

    image_extension = os.path.splitext(image.filename)[1]

    image_path = os.path.join(image_directory, f"image{image_extension}")

    if not os.access(image_directory, os.W_OK):
        raise InternalServerError(f"{image_directory} is not writable")

    try:
        with open(image_path, "wb") as f:
            f.write(await image.read())

    except Exception as e:
        raise InternalServerError(
            f"could not save image at `{image_path}`: {e}"
        )

    restaurant.image = image_path  # type:ignore
    state.session.commit()

    return image_path
