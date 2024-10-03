from typing import List
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from api.crud.customer import get_customer, login_customer, register_customer, get_customer_reviews, create_customer_review
from api.dependencies.state import get_state
from api.dependencies.id import get_customer_id
from api.schemas.authentication import AuthenticationResponse
from api.schemas.customer import (
    CustomerLogin,
    CustomerRegister,
    Customer,
    CustomerReviewCreate, 
    CustomerReview as CustomerReviewSchema
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
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await register_customer(state, payload)


@router.post(
    "/login",
    description="Logins user and returns a JWT token used for authentication.",
)
async def login_customer_api(
    payload: CustomerLogin,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await login_customer(state, payload)


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
    return await get_customer(state, result)


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


#customer review
@router.get(
    "/reviews/{customer_id}",
    description="""
        Get user's reviews by their ID.
    """
)
async def get_customer_reviews_by_id_api(
    customer_id: int,
    state: State = Depends(get_state)
) -> List[CustomerReviewSchema]:
    return await get_customer_reviews(state, customer_id)


@router.post(
    "/add_reviews",
    description="""
        Add a review for a restaurant.
    """
)
# async def create_customer_review_api(
#     payload: CustomerReviewCreate,
#     customer_id: int = Depends(get_customer_id),
#     state: State = Depends(get_state),
# ) -> int:
#     return await create_customer_review(state, customer_id, payload)
async def create_customer_review_api(
    payload: CustomerReviewCreate,
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
)  -> int:
    review_id = await create_customer_review(state, customer_id, payload)
    # Fetch the newly created review to return it
    # created_review = await state.session.get(CustomerReview, review_id)
    return review_id