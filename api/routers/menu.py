from fastapi.responses import FileResponse
from api.crud.menu import (
    create_menu,
    get_menu,
    get_menu_image,
    get_restaurant_menus,
    upload_menu_image,
)
from api.dependencies.state import get_state
from api.errors import NotFoundError
from api.schemas.menu import Menu, MenuCreate, PublicMenu
from api.dependencies.id import get_merchant_id
from api.state import State

from fastapi.security import HTTPBearer
from fastapi import APIRouter, Depends, UploadFile


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


@router.get(
    "/{menu_id}",
    description="""
        Get the menu details.
    """,
)
async def get_menu_api(
    menu_id: int, state: State = Depends(get_state)
) -> PublicMenu:
    return await get_menu(state, menu_id)


@router.get(
    "/",
    description="""
        Get list of menus in a restaurant.
    """,
)
async def get_restaurant_menus_api(
    restaurant_id: int, state: State = Depends(get_state)
) -> list[PublicMenu]:
    return [
        Menu.model_validate(menu)
        for menu in await get_restaurant_menus(state, restaurant_id)
    ]


@router.put(
    "/{menu_id}/image",
    description="""
        Update a menu.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def upload_menu_image_api(
    menu_id: int,
    image: UploadFile,
    state: State = Depends(get_state),
    merchant_id: int = Depends(get_merchant_id),
) -> str:
    await upload_menu_image(
        state,
        menu_id,
        image,
        merchant_id,
    )

    return "image updated"


@router.get(
    "/{menu_id}/image",
    description="""
        Get the image of a menu.
    """,
)
async def get_menu_image_api(
    menu_id: int, state: State = Depends(get_state)
) -> FileResponse:
    image = await get_menu_image(state, menu_id)

    match image:
        case None:
            raise NotFoundError(
                "image not found, the menu hasn't uploaded an image yet"
            )

        case image:
            return image
