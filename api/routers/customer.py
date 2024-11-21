from datetime import timedelta
from typing import List
from fastapi import APIRouter, Depends, Request, Response, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer

from api.configuration import REFRESH_TOKEN_EXPIRE_DAYS, Configuration
from api.crud.customer import (
    add_favorite_restaurant_ids,
    delete_favorite_restaurant_ids,
    get_customer,
    get_favorite_restaurant_ids,
    login_customer,
    refresh_access_token,
    register_customer,
    get_customer_reviews,
    create_customer_review,
    update_customer,
    upload_banner,
    upload_profile,
    get_profile_img,
    get_banner_img,
)
from api.dependencies.configuration import (
    get_configuration,
)
from api.dependencies.state import get_state
from api.dependencies.id import get_customer_id
from api.errors.authentication import UnauthorizedError
from api.schemas.authentication import AuthenticationResponse
from api.schemas.customer import (
    CustomerLogin,
    CustomerRegister,
    Customer,
    CustomerReviewCreate,
    CustomerReview as CustomerReviewSchema,
    CustomerUpdate,
)

from api.state import State

router = APIRouter(
    prefix="/customers",
    tags=["customer"],
)


@router.post(
    "/register",
    description="""
        Registers a new user and returns a JWT token used for authentication.
    """,
)
async def register_customer_api(
    payload: CustomerRegister,
    response: Response,
    configuration: Configuration = Depends(get_configuration),
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    authen_access, authen_refresh = await register_customer(
        state, configuration, payload
    )

    response.delete_cookie("refresh_token")
    response.set_cookie(
        key="refresh_token",
        value=authen_refresh,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=int(
            timedelta(REFRESH_TOKEN_EXPIRE_DAYS).total_seconds() * 1000
        ),
    )

    return authen_access


@router.post(
    "/login",
    description="Logins user and returns a JWT token used for authentication.",
)
async def login_customer_api(
    payload: CustomerLogin,
    response: Response,
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
) -> AuthenticationResponse:
    authen_access, authen_refresh = await login_customer(
        state, configuration, payload
    )

    response.delete_cookie("refresh_token")
    response.set_cookie(
        key="refresh_token",
        value=authen_refresh,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=int(
            timedelta(REFRESH_TOKEN_EXPIRE_DAYS).total_seconds() * 1000
        ),
    )

    return authen_access


@router.get("/refresh", description="Refresh the access token.")
async def refresh_token_api(
    request: Request,  # not sure what payload should be
    response: Response,
    configuration: Configuration = Depends(get_configuration),
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise UnauthorizedError("refresh token not found")

    authen_access, authen_refresh = await refresh_access_token(
        state, configuration, request
    )

    response.delete_cookie("refresh_token")
    response.set_cookie(
        key="refresh_token",
        value=authen_refresh,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=int(
            timedelta(REFRESH_TOKEN_EXPIRE_DAYS).total_seconds() * 1000
        ),
    )

    return authen_access


# @router.get("/refresh", description="Refresh the access token.")
# async def refresh_token_api(
#     request: Request, #not sure what payload should be
#     response: Response,
#     state: State = Depends(get_state)
# ) :
#     refresh_token = request.cookies.get("refresh_token")
#     print(refresh_token)
#     if not refresh_token:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     return await refresh_access_token(state, request)


@router.get(
    "/me",
    dependencies=[Depends(HTTPBearer())],
    description="""
        Get the public information of the currently authenticated user.
        """,
)
async def get_current_customer_api(
    state: State = Depends(get_state),
    result: int = Depends(get_customer_id),
) -> Customer:
    result = await get_customer(state, result)

    return result


@router.post("/update", description="Update customer information")
async def update_customer_api(
    payload: CustomerUpdate,
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
    customer_id: int = Depends(get_customer_id),
):
    result = await update_customer(configuration, state, customer_id, payload)
    return result


@router.get(
    "/favorite-restaurants",
    description="""
        Get the list of favorite restaurant ids of the customer
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def get_favorite_restaurant_ids_api(
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
) -> list[int]:
    return await get_favorite_restaurant_ids(state, customer_id)


@router.post(
    "/favorite-restaurants",
    description="""
        Add a restaurant to the user's favorite list.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def add_favorite_restaurant_ids_api(
    restaurant_ids: list[int],
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
) -> str:
    await add_favorite_restaurant_ids(state, customer_id, restaurant_ids)
    return "success"


@router.delete(
    "/favorite-restaurants",
    description="""
        Delete restaurants from the user's favorite list.
    """,
    dependencies=[Depends(HTTPBearer())],
)
async def delete_favorite_restaurant_ids_api(
    restaurant_ids: list[int],
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
) -> str:
    await delete_favorite_restaurant_ids(state, customer_id, restaurant_ids)
    return "success"


# customer review
@router.get(
    "/customer/reviews",
    description="""
        Get user's reviews by their ID.
    """,
)
async def get_customer_reviews_by_id_api(
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
) -> List[CustomerReviewSchema]:
    return await get_customer_reviews(state, customer_id)


@router.post(
    "/add_reviews",
    description="""
        Add a review for a restaurant.
    """,
)
async def create_customer_review_api(
    payload: CustomerReviewCreate,
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
) -> int:
    review_id = await create_customer_review(state, customer_id, payload)
    return review_id


@router.post(
    "/upload_profile",
    description="""
        Upload user profile pic
    """,
)
async def upload_profile_api(
    image: UploadFile,
    customer_id: int = Depends(get_customer_id),
    configuration: Configuration = Depends(get_configuration),
    state: State = Depends(get_state),
) -> str:
    await upload_profile(configuration, image, customer_id, state)

    return "success"


@router.post(
    "/upload_banner",
    description="""
        Upload user banner pic
    """,
)
async def upload_banner_api(
    image: UploadFile,
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
    configuration: Configuration = Depends(get_configuration),
) -> str:
    await upload_banner(configuration, image, customer_id, state)

    return "success"


@router.get(
    "/{customer_id}",
    description="""
        Get the public information of a user by their ID.
    """,
)
async def get_customer_by_id_api(
    customer_id: int,
    state: State = Depends(get_state),
) -> Customer:
    return await get_customer(state, customer_id)


@router.get(
    "/{customer_id}/get_profile_img",
    description="""
        Get user profile pic
    """,
    responses={
        204: {
            "description": "the customer does not have profile image",
            "content": {"application/json": {}},
        },
        200: {
            "description": "The profile image",
            "content": {
                "image/*": {},
            },
        },
    },
    response_model=None,
    response_class=Response,
)
async def get_profile_img_api(
    response: Response,
    customer_id: int,
    state: State = Depends(get_state),
) -> FileResponse | None:

    image = await get_profile_img(state, customer_id)
    match image:
        case None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        case image:
            return image


@router.get(
    "/{customer_id}/get_banner_img",
    description="""
        Get user profile pic
    """,
    responses={
        204: {
            "description": "the customer does not have banner image",
            "content": {"application/json": {}},
        },
        200: {
            "description": "The banner image",
            "content": {
                "image/*": {},
            },
        },
    },
    response_model=None,
    response_class=Response,
)
async def get_banner_img_api(
    response: Response,
    customer_id: int,
    state: State = Depends(get_state),
) -> FileResponse | None:
    image = await get_banner_img(state, customer_id)
    match image:
        case None:
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        case image:
            return image
