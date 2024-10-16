from fastapi import APIRouter, Depends, Response, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer

from api.configuration import Configuration
from api.crud.restaurant import (
    create_customization,
    create_menu,
    create_restaurant,
    get_menu,
    get_menu_customizations,
    get_menu_image,
    get_restaurant,
    get_restaurant_menus,
    search_restaurant,
    upload_menu_image,
    upload_restaurant_image,
    get_restaurant_image,
    get_restaurant_reviews,
)
from api.dependencies.configuration import get_configuration
from api.dependencies.state import get_state
from api.dependencies.id import get_merchant_id
from api.schemas.restaurant import (
    CustomizationCreate,
    Menu,
    MenuCreate,
    Customization,
    Restaurant,
    RestaurantCreate,
)
from api.schemas.customer import CustomerReview as CustomerReviewSchema
from api.state import State


router = APIRouter(
    prefix="/restaurants",
    tags=["restaurant"],
)


@router.post(
    "/",
    description="""
        Create a new restaurant for the merchant. This endpoint requires the
        merchant to be authenticated.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def create_restaurant_api(
    restaurant: RestaurantCreate,
    state: State = Depends(get_state),
    result: int = Depends(get_merchant_id),
) -> int:
    return await create_restaurant(
        state,
        result,
        restaurant,
    )


@router.get(
    "/search",
    description="Get a list of restaurants from search query.",
)
async def search_restaurants_api(
    query: str,
    limit: int = 10,
    state: State = Depends(get_state),
) -> list[int]:
    return await search_restaurant(query, limit, state)


@router.get(
    "/{restaurant_id}",
    description="Get the restaurant details.",
)
async def get_restaurant_api(
    restaurant_id: int,
    state: State = Depends(get_state),
) -> Restaurant:
    return await get_restaurant(state, restaurant_id)


@router.put(
    "/{restaurant_id}/image",
    description="""
        Upload an image for the restaurant. This endpoint requires the
        merchant to be authenticated
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def upload_restaurant_image_api(
    restaurant_id: int,
    image: UploadFile,
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
    result: int = Depends(get_merchant_id),
) -> str:
    await upload_restaurant_image(
        state,
        configuration,
        restaurant_id,
        image,
        result,
    )

    return "image uploaded"


@router.get(
    "/{restaurant_id}/image",
    description="Get the image of the restaurant.",
    responses={
        204: {
            "description": "the resaurant does not have an image",
            "content": {"application/json": {}},
        },
        200: {
            "description": "The image of the restaurant",
            "content": {
                "image/*": {},
            },
        },
    },
    response_model=None,
    response_class=Response,
)
async def get_restuarnat_image_api(
    restaurant_id: int,
    response: Response,
    state: State = Depends(get_state),
) -> FileResponse | None:
    image = await get_restaurant_image(state, restaurant_id)

    match image:
        case None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None

        case image:
            return image


@router.get(
    "/menus/{menu_id}",
    description="""
        Get the menu details.
    """,
)
async def get_menu_api(
    menu_id: int, state: State = Depends(get_state)
) -> Menu:
    return await get_menu(state, menu_id)


@router.post(
    "/{restaurant_id}/menus",
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
    "/{restaurant_id}/menus",
    description="""
        Get list of menus in a restaurant.
    """,
)
async def get_restaurant_menus_api(
    restaurant_id: int, state: State = Depends(get_state)
) -> list[Menu]:
    return [
        Menu.model_validate(menu)
        for menu in await get_restaurant_menus(state, restaurant_id)
    ]


@router.put(
    "/menus/{menu_id}/image",
    description="""
        Update a menu.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def upload_menu_image_api(
    menu_id: int,
    image: UploadFile,
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
    merchant_id: int = Depends(get_merchant_id),
) -> str:
    await upload_menu_image(
        state,
        configuration,
        menu_id,
        image,
        merchant_id,
    )

    return "image updated"


@router.get(
    "/menus/{menu_id}/image",
    responses={
        204: {
            "description": "the menu does not have an image",
            "content": {"application/json": {}},
        },
        200: {
            "description": "The image of the menu",
            "content": {
                "image/*": {},
            },
        },
    },
    response_model=None,
    response_class=Response,
)
async def get_menu_image_api(
    menu_id: int, response: Response, state: State = Depends(get_state)
) -> FileResponse | None:
    image = await get_menu_image(state, menu_id)

    match image:
        case None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None

        case image:
            return image


@router.post(
    "/menus/{menu_id}/customizations",
    description="""
        Create a new customization for a menu.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def create_customization_api(
    menu_id: int,
    customization: CustomizationCreate,
    state: State = Depends(get_state),
    merchant_id: int = Depends(get_merchant_id),
) -> int:
    return await create_customization(
        state,
        menu_id,
        customization,
        merchant_id,
    )


@router.get(
    "/menus/{menu_id}/customizations",
    description="""
        Get list of customizations for a menu.
    """,
)
async def get_menu_customizations_api(
    menu_id: int, state: State = Depends(get_state)
) -> list[Customization]:
    return [
        Customization.model_validate(customization)
        for customization in await get_menu_customizations(state, menu_id)
    ]


@router.get(
    "/reviews/{restaurant_id}",
    description="""Get the reviews of a restaurant by their ID.""",
)
async def get_restaurant_reviews_by_id_api(
    restaurant_id: int, state: State = Depends(get_state)
) -> list[CustomerReviewSchema]:
    return await get_restaurant_reviews(restaurant_id, state)
