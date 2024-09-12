from fastapi import APIRouter, Depends, UploadFile
from fastapi.security import HTTPBearer

from api.crud.restaurant import create_restaurant, upload_restaurant_image
from api.dependencies.state import get_state
from api.dependencies.id import get_merchant_id
from api.schemas.restaurant import RestaurantCreate
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
    result: int = Depends(get_merchant_id),
) -> str:
    await upload_restaurant_image(
        state,
        restaurant_id,
        image,
        result,
    )

    return "image uploaded"
