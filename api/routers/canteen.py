from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Response, UploadFile, File, status
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse

from api.crud.canteen import get_nearest_canteens, add_canteen, update_canteen_img, get_canteen_img, get_nearest_restaurants, get_canteen_by_restaurant_id
#, get_nearest_restaurants
from api.dependencies.state import get_state
from api.dependencies.id import get_customer_id
from api.schemas.authentication import AuthenticationResponse
from api.models.canteen import Canteen
from api.models.restaurant import Restaurant
from api.schemas.restaurant import RestaurantBase,GetRestaurant
from api.schemas.canteen import (
    CanteenBase,
    GetCanteen
)

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
    result: int = Depends(get_customer_id)
) -> List[GetCanteen]:
    return await get_nearest_canteens(state, user_lat, user_long)

@router.post(
    "/add_canteen",
    description="""
        Create canteen
    """
)
async def add_canteen_api(
    payload: CanteenBase,
    state: State = Depends(get_state),
    result: int = Depends(get_customer_id)
) -> CanteenBase:
    return await add_canteen(state, payload)

@router.put(
    "/{canteen_id}/img",
    description="""
        upload canteen img
    """
)
async def update_canteen_img_api(
    canteen_id: int,
    image: UploadFile = File(...),
    state: State = Depends(get_state),
) -> str:
    return await update_canteen_img(state, canteen_id, image)

@router.get(
    "/{canteen_id}/img",
    description="""
        Get canteen by id
    """
)
async def get_canteen_img_api(
    canteen_id : int, 
    response: Response, 
    state: State = Depends(get_state),
    result: int = Depends(get_customer_id)
) -> FileResponse:
    image = await get_canteen_img(state, canteen_id)

    match image: 
        case None: 
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        case image:
            return image
        
@router.get(
        "/restaurants/{restaurant_id}",
        description="""
            Get canteen by restaurant id
        """ 
)
async def get_canteen_by_restaurant_id_api(
    restaurant_id: int, 
    state: State = Depends(get_state)) -> CanteenBase:
    return await get_canteen_by_restaurant_id(state, restaurant_id)

        

@router.get(
    "/canteen/restaurants",
    description="""
        Get restaurants of the nearest canteen
    """
)
async def get_nearest_restaurants_api(
    user_lat: float,
    user_long: float,
    state: State = Depends(get_state),
    result: int = Depends(get_customer_id)
) -> List[GetRestaurant]:
    return await get_nearest_restaurants(state, user_lat, user_long)


