import logging
from api.configuration import REFRESH_TOKEN_EXPIRE_DAYS, Configuration
from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import AuthenticationError
from api.models.RefreshToken import RefreshToken
from api.models.restaurant import Restaurant
from api.schemas.authentication import AuthenticationResponse
from api.state import State
from api.models.customer import Customer, CustomerReview, FavoriteRestaurant
from api.schemas.customer import (
    CustomerLogin,
    CustomerRegister,
    CustomerReview as CustomerReviewSchema,
    CustomerReviewCreate,
)

from typing import List
import hashlib
from fastapi import HTTPException, Request

from datetime import timedelta
import datetime


async def register_customer(
    state: State,
    configuration: Configuration,
    customer_create: CustomerRegister,
) -> tuple[AuthenticationResponse, str]:
    """Create a new customer in the database."""

    # Check if a customer with the same username or email already exists
    existing_customer = (
        state.session.query(Customer)
        .filter(
            (Customer.username == customer_create.username)
            | (Customer.email == customer_create.email),
        )
        .first()
    )

    if existing_customer:
        raise ConflictingError(
            "an account with the same username or email already exists"
        )

    salt, hashed_password = configuration.generate_password(
        customer_create.password
    )

    new_customer = Customer(
        first_name=customer_create.first_name,
        last_name=customer_create.last_name,
        username=customer_create.username,
        email=customer_create.email,
        hashed_password=hashed_password,
        salt=salt,
    )

    state.session.add(new_customer)
    state.session.commit()

    state.session.refresh(new_customer)

    token = configuration.encode_jwt(
        {"customer_id": new_customer.id}, timedelta(minutes=5)
    )

    refresh_token = configuration.create_refresh_token(
        {"customer_id": new_customer.id}
    )

    # store refresh token in database
    stored_refresh_token = RefreshToken(
        customer_id=new_customer.id,
        role="user",
        token=refresh_token,
        expired_at=datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    # add refresh token to database if not exists, if already exists, update the token
    state.session.add(stored_refresh_token)
    state.session.commit()

    # set refresh token in HTTP-only cookie
    # response.set_cookie(
    #     key="refresh_token",
    #     value=refresh_token,
    #     httponly=True,
    #     secure=True,
    #     samesite="lax",
    #     max_age=timedelta(REFRESH_TOKEN_EXPIRE_DAYS),
    # )

    return (
        AuthenticationResponse(
            jwt_token=token, id=new_customer.id  # type: ignore
        ),
        refresh_token,
    )


async def login_customer(
    state: State,
    configuration: Configuration,
    customer_login: CustomerLogin,
) -> tuple[AuthenticationResponse, str]:
    """Authenticate a customer and return a JWT token."""
    try:
        customer = (
            state.session.query(Customer)
            .filter(Customer.username == customer_login.username)
            .first()
        )

        if not customer:
            raise AuthenticationError("invalid username or password")

        salted_password = customer_login.password + customer.salt
        hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        if hashsed_password != customer.hashed_password:
            raise AuthenticationError("invalid username or password")

        token = configuration.encode_jwt(
            {"customer_id": customer.id}, timedelta(minutes=5)
        )
        refresh_token = configuration.create_refresh_token(
            {"customer_id": customer.id}
        )

        # store refresh token in database
        add_or_update_refresh_token(state, "user", customer.id, refresh_token)

        # response.delete_cookie(
        #     key="refresh_token"
        # )

        # response.set_cookie(
        #     key="refresh_token",
        #     value=refresh_token,
        #     domain="localhost",
        #     path="/",
        #     httponly=False, #type HTTP-only cookie
        #     secure=False, #change to True in production: works only on HTTPS
        #     samesite="None", #Strict = cross-site cookies are not sent on cross-site requests, Lax = cookies are sent on top-level navigations and will be sent along with GET requests initiated by third party website
        #     max_age= timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        # )

        role = "user"

        return (
            AuthenticationResponse(
                role=role, jwt_token=token, id=customer.id  # type: ignore
            ),
            refresh_token,
        )
    except Exception as e:
        logging.error("Error logging in customer: %s", e)
        raise AuthenticationError("invalid username or password")


async def refresh_access_token(
    state: State, configuration: Configuration, request: Request
) -> tuple[AuthenticationResponse, str]:
    # print("refresh token: ", response)
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    refresh_token_pair = (
        state.session.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )

    if not refresh_token_pair:
        raise AuthenticationError("invalid token")

    customer_id = refresh_token_pair.customer_id
    customer = (
        state.session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise HTTPException(status_code=402, detail="Invalid token")

    if refresh_token_pair.expired_at < datetime.datetime.now():
        raise HTTPException(status_code=403, detail="Token expired")

    payload = configuration.encode_jwt(
        {"customer_id": customer_id}, timedelta(5)
    )

    return (
        AuthenticationResponse(jwt_token=payload, id=customer_id),
        refresh_token,
    )


def add_or_update_refresh_token(
    state: State,
    role: str,
    customer_id: int,
    refresh_token: str,
) -> None:
    existing_refresh_token = (
        state.session.query(RefreshToken)
        .filter(RefreshToken.customer_id == customer_id)
        .first()
    )

    if existing_refresh_token:
        existing_refresh_token.token = refresh_token
        existing_refresh_token.expired_at = (
            datetime.datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
    else:
        new_refresh_token = RefreshToken(
            customer_id=customer_id,
            role=role,
            token=refresh_token,
            expired_at=datetime.datetime.now()
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        state.session.add(new_refresh_token)

    state.session.commit()


async def get_customer(state: State, customer_id: int) -> Customer:
    """Get a customer by their ID."""
    result = (
        state.session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if result is None:
        raise NotFoundError("customer with the ID in the token is not found")

    return result


async def get_favorite_restaurant_ids(
    state: State, customer_id: int
) -> list[int]:
    customer = (
        state.session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise NotFoundError("customer not found")

    results = (
        state.session.query(FavoriteRestaurant)
        .filter(FavoriteRestaurant.customer_id == customer_id)
        .all()
    )

    return [result.restaurant_id for result in results]


async def delete_favorite_restaurant_ids(
    state: State,
    customer_id: int,
    restaurant_ids: list[int],
) -> None:
    customer = (
        state.session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise NotFoundError("customer not found")

    seen: set[int] = set()
    removing_restaurants: list[FavoriteRestaurant] = []
    for restaurant_id in restaurant_ids:
        if restaurant_id in seen:
            raise ConflictingError(
                f"restaurant id {restaurant_id} is duplicated in the request"
            )

        removing_restaurant = (
            state.session.query(FavoriteRestaurant)
            .filter(
                (FavoriteRestaurant.customer_id == customer_id)
                & (FavoriteRestaurant.restaurant_id == restaurant_id)
            )
            .first()
        )

        if not removing_restaurant:
            raise NotFoundError(
                f"restaurant id {restaurant_id} not found in the favorite list"
            )

        removing_restaurants.append(removing_restaurant)

        seen.add(restaurant_id)

    for restaurant in removing_restaurants:
        state.session.delete(restaurant)

    state.session.commit()


async def add_favorite_restaurant_ids(
    state: State,
    customer_id: int,
    restaurant_ids: list[int],
) -> None:
    customer = (
        state.session.query(Customer)
        .filter(Customer.id == customer_id)
        .first()
    )

    if not customer:
        raise NotFoundError("customer not found")

    seen: set[int] = set()

    for restaurant_id in restaurant_ids:
        existing_favorite = (
            state.session.query(FavoriteRestaurant)
            .filter(
                (FavoriteRestaurant.customer_id == customer_id)
                & (FavoriteRestaurant.restaurant_id == restaurant_id)
            )
            .first()
        )

        if restaurant_id in seen:
            raise ConflictingError(
                f"restaurant id {restaurant_id} is duplicated in the request"
            )

        seen.add(restaurant_id)

        if existing_favorite:
            raise ConflictingError(
                f"restaurant id {restaurant_id} already exists in the favorite list"
            )

        restaurant = (
            state.session.query(Restaurant)
            .filter(Restaurant.id == restaurant_id)
            .first()
        )

        if not restaurant:
            raise NotFoundError(f"restaurant id {restaurant_id} not found")

    for restaurant_id in restaurant_ids:
        new_favorite = FavoriteRestaurant(
            customer_id=customer_id, restaurant_id=restaurant_id
        )
        state.session.add(new_favorite)

    state.session.commit()


# customer review
async def get_customer_reviews(
    state: State, customer_id: int
) -> List[CustomerReviewSchema]:
    """Get a customer's reviews by their ID."""
    results = (
        state.session.query(CustomerReview)
        .filter(CustomerReview.customer_id == customer_id)
        .all()
    )  # result = list of sql alchemy model so needed to be converted to list of pydantic model

    return [CustomerReviewSchema.model_validate(review) for review in results]


async def create_customer_review(
    state: State, customerID: int, reviewDetail: CustomerReviewCreate
) -> int:
    sql_review = CustomerReview(
        customer_id=customerID,
        restaurant_id=reviewDetail.restaurant_id,
        menu_id=reviewDetail.menu_id,
        review=reviewDetail.review,
        tastiness=reviewDetail.tastiness,
        hygiene=reviewDetail.hygiene,
        quickness=reviewDetail.quickness,
        created_at=datetime.datetime.now(),
    )
    state.session.add(sql_review)
    state.session.flush()
    state.session.commit()

    return sql_review.id
