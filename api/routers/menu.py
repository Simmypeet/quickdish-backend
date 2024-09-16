from fastapi import APIRouter, Depends
from fastapi.datastructures import State
from fastapi.security import HTTPBearer

from api.crud.menu import create_menu
from api.dependencies.state import get_state
from api.schemas.menu import MenuCreate
from api.dependencies.id import get_merchant_id


router = APIRouter(
    prefix="/menus",
    tags=["menu"],
)


@router.post(
    "/",
    description="""
        Create new menu for a restaurant.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def create_menu_api(
    restaurant_id: int,
    menu_create: MenuCreate,
    state: State = Depends(get_state),
    merchant_id: int = Depends(get_merchant_id),
) -> int:
    return await create_menu(
        state,
        restaurant_id,
        menu_create,
        merchant_id,
    )
