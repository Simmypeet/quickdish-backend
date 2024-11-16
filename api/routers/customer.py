from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import HTTPBearer

from api.crud.customer import get_customer, login_customer, register_customer, get_customer_reviews, create_customer_review, refresh_access_token, update_customer
from api.dependencies.state import get_state
from api.dependencies.id import get_customer_id
from api.schemas.authentication import AuthenticationResponse
from api.schemas.customer import (
    CustomerLogin,
    CustomerRegister,
    Customer,
    CustomerReviewCreate, 
    CustomerReview as CustomerReviewSchema,
    CustomerUpdate
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
    state: State = Depends(get_state)
) -> AuthenticationResponse:
    return await register_customer(state, payload, response)

@router.post(
    "/login",
    description="Logins user and returns a JWT token used for authentication.",
)
async def login_customer_api(
    payload: CustomerLogin,
    response: Response,
    state: State = Depends(get_state),
) -> AuthenticationResponse:
    return await login_customer(state, payload, response)


@router.get("/refresh", description="Refresh the access token.")
async def refresh_token_api(
    request: Request, #not sure what payload should be 
    response: Response,
    state: State = Depends(get_state)
) -> AuthenticationResponse :
    refresh_token = request.cookies.get("refresh_token")
    print(refresh_token)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return await refresh_access_token(state, request)

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
    result = get_customer(state, result)
    if result == None:
        raise HTTPException(status_code=401, detail="Token expired")
    
    return await result

@router.post(
    "/update", 
    description="Update customer information"
)
async def update_customer_api(
    payload: CustomerUpdate,
    state: State = Depends(get_state), 
    customer_id: int = Depends(get_customer_id)
): 
    result = update_customer(state, customer_id, payload)
    print(payload)
    if result == None: 
        raise HTTPException(status_code=401, detail="Token expired")
    return await result


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
    "/customer/reviews",
    description="""
        Get user's reviews by their ID.
    """
)
async def get_customer_reviews_by_id_api(
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state)
) -> List[CustomerReviewSchema]:
    return await get_customer_reviews(state, customer_id)


@router.post(
    "/add_reviews",
    description="""
        Add a review for a restaurant.
    """
)

async def create_customer_review_api(
    payload: CustomerReviewCreate,
    customer_id: int = Depends(get_customer_id),
    state: State = Depends(get_state),
)  -> int:
    review_id = await create_customer_review(state, customer_id, payload)
    return review_id