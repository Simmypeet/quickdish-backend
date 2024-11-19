from api.configuration import Configuration
from api.models.canteen import Canteen
from api.models.restaurant import Restaurant
from api.state import State
from api.schemas.canteen import CanteenBase
from fastapi.responses import FileResponse
from api.errors import NotFoundError

from typing import List
from fastapi import HTTPException, UploadFile
import math
import os
import logging


logger = logging.getLogger(__name__)


async def get_nearest_canteens(
    state: State, user_lat: float, user_long: float
) -> List[Canteen]:
    canteens = state.session.query(Canteen).all()
    distance = [
        (
            c,
            await calc_distance(c.latitude, c.longitude, user_lat, user_long),
        )
        for c in canteens
    ]
    sorted_distance = sorted(distance, key=lambda x: x[1])

    ranks = [val[0] for val in sorted_distance]

    return ranks


async def add_canteen(state: State, payload: CanteenBase) -> Canteen:
    try:
        new_canteen = Canteen(
            name=payload.name,
            img="",
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        state.session.add(new_canteen)
        state.session.commit()
        state.session.refresh(new_canteen)
        return new_canteen
    except Exception as e:
        logger.error(f"Error adding canteen: {e}")
        state.session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def get_nearest_restaurants(
    state: State, user_lat: float, user_long: float
) -> List[Restaurant]:
    ranked_canteens = await get_nearest_canteens(state, user_lat, user_long)

    if len(ranked_canteens) == 0:
        # no canteens found
        return []

    id = ranked_canteens[0].id
    return state.session.query(Restaurant).filter_by(canteen_id=id).all()


async def calc_distance(
    canteen_lat: float, canteen_long: float, user_lat: float, user_long: float
) -> float:
    # Convert latitude and longitude from degrees to radians
    canteen_lat_rad = math.radians(canteen_lat)
    canteen_long_rad = math.radians(canteen_long)
    user_lat_rad = math.radians(user_lat)
    user_long_rad = math.radians(user_long)

    # Haversine formula
    dlat = user_lat_rad - canteen_lat_rad
    dlon = user_long_rad - canteen_long_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(canteen_lat_rad)
        * math.cos(user_lat_rad)
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of Earth in kilometers
    radius_of_earth_km = 6371.0
    # Distance in kilometers
    distance = radius_of_earth_km * c
    return distance


async def update_canteen_img(
    configuration: Configuration,
    state: State,
    canteen_id: int,
    image: UploadFile,
) -> str:
    canteen = state.session.query(Canteen).filter_by(id=canteen_id).first()

    if not canteen:
        raise NotFoundError("Canteen not found")

    image_dir = os.path.join(
        configuration.application_data_path, "canteens", str(canteen_id)
    )
    image_path = await configuration.upload_image(image, image_dir)
    canteen.img = image_path
    state.session.commit()

    return image_path


async def get_canteen_img(
    state: State, canteen_id: int
) -> FileResponse | None:
    canteen = state.session.query(Canteen).filter_by(id=canteen_id).first()
    if not canteen:
        raise NotFoundError("Canteen not found")
    if canteen.img == "":
        return None
    return FileResponse(canteen.img)


async def get_canteen_by_restaurant_id(
    state: State, restaurant_id: int
) -> CanteenBase:
    restaurant = (
        state.session.query(Restaurant).filter_by(id=restaurant_id).first()
    )
    if not restaurant:
        raise NotFoundError("Restaurant not found")

    canteen = (
        state.session.query(Canteen)
        .filter_by(id=restaurant.canteen_id)
        .first()
    )
    return canteen


async def get_restaurants_in_canteen(
    state: State, canteen_id: int
) -> List[int]:
    canteen = state.session.query(Canteen).filter_by(id=canteen_id).first()
    if not canteen:
        raise NotFoundError("Canteen not found")

    return [
        restaurant.id
        for restaurant in state.session.query(Restaurant)
        .filter_by(canteen_id=canteen_id)
        .all()
    ]
