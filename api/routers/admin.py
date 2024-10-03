#need admin token to access these routes

from fastapi import APIRouter, Depends
from api.dependencies.state import get_state
from api.state import State
from api.crud.admin import create_tag, create_restaurant_tag
from api.schemas.Tag import RestaurantTagCreate as RestaurantTagCreateSchema

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.post(
    "/create_tag", 
    description="Creates a new tag for restaurant.",
)
async def create_tag_api(
    title: str, 
    state : State = Depends(get_state),
) -> int : 
    return await create_tag(state, title)


@router.post(
    "/create_restaurant_tag", 
    description="Creates a tag for restaurant from existed tags.",
)
async def create_restaurant_tag_api(
    payload: RestaurantTagCreateSchema, 
    state : State = Depends(get_state),
) -> int : 
    return await create_restaurant_tag(state, payload)