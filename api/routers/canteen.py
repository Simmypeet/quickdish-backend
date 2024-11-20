from typing import List
from fastapi import (
    APIRouter,
    Depends,
    Response,
    UploadFile,
    File,
    status,
)
from fastapi.responses import FileResponse

from api.configuration import Configuration
from api.crud.canteen import (
    get_canteen_by_id,
    get_nearest_canteens,
    add_canteen,
    get_restaurants_in_canteen,
    update_canteen_img,
    get_canteen_img,
    get_nearest_restaurants,
    get_canteen_by_restaurant_id,
)

from api.dependencies.configuration import get_configuration
from api.dependencies.state import get_state

from api.schemas.restaurant import Restaurant
from api.schemas.canteen import Canteen, CanteenBase


from api.state import State

router = APIRouter(
    prefix="/canteens",
    tags=["canteen"],
)


@router.get(
    "/",
    description="""
        Get all canteens ranked by distance.
    """,
)
async def get_canteens_api(
    user_lat: float,
    user_long: float,
    state: State = Depends(get_state),
) -> List[Canteen]:
    return [
        Canteen.model_validate(canteen)
        for canteen in await get_nearest_canteens(state, user_lat, user_long)
    ]



@router.post(
    "/add_canteen",
    description="""
        Create canteen
    """,
)
async def add_canteen_api(
    payload: CanteenBase,
    state: State = Depends(get_state),
) -> Canteen:
    return await add_canteen(state, payload)


@router.get(
    "/canteen/restaurants",
    description="""
        Get restaurants of the nearest canteen
    """,
)
async def get_nearest_restaurants_api(
    user_lat: float,
    user_long: float,
    state: State = Depends(get_state),
) -> List[Restaurant]:
    return [
        Restaurant.model_validate(restaurant)
        for restaurant in await get_nearest_restaurants(
            state, user_lat, user_long
        )
    ]


@router.get(
    "/restaurants/{restaurant_id}",
    description="""
            Get canteen by restaurant id
        """,
)
async def get_canteen_by_restaurant_id_api(
    restaurant_id: int, state: State = Depends(get_state)
) -> CanteenBase:
    return await get_canteen_by_restaurant_id(state, restaurant_id)


@router.get(
    "/{canteen_id}",
    description="""
        Get the information of a canteen by id
    """,
)
async def get_canteen_by_id_api(
    canteen_id: int, state: State = Depends(get_state)
) -> Canteen:
    return await get_canteen_by_id(state, canteen_id)


@router.get(
    "/{canteen_id}/restaurants",
    description="""
        Get a list of restaurant ids in this canteen
    """,
)
async def get_restaurants_in_canteen_api(
    canteen_id: int, state: State = Depends(get_state)
) -> List[int]:
    return await get_restaurants_in_canteen(state, canteen_id)


@router.put(
    "/{canteen_id}/img",
    description="""
        upload canteen img
    """,
)
async def update_canteen_img_api(
    canteen_id: int,
    image: UploadFile = File(...),
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
) -> str:
    await update_canteen_img(configuration, state, canteen_id, image)

    return "success"


@router.get(
    "/{canteen_id}/img",
    description="""
        Get canteen by id
    """,
    response_model=None,
    response_class=Response,
)
async def get_canteen_img_api(
    canteen_id: int,
    response: Response,
    state: State = Depends(get_state),
) -> FileResponse | None:
    image = await get_canteen_img(state, canteen_id)

    match image:
        case None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        case image:
            return image
