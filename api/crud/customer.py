from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import AuthenticationError
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

# import datetime
from datetime import datetime, timedelta


async def register_customer(
    state: State, customer_create: CustomerRegister
) -> AuthenticationResponse:
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

    salt, hashed_password = state.generate_password(customer_create.password)

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

    token = state.encode_jwt(
        {"customer_id": new_customer.id}, timedelta(days=5)
    )

    return AuthenticationResponse(
        jwt_token=token, id=new_customer.id  # type: ignore
    )


async def login_customer(
    state: State, customer_login: CustomerLogin
) -> AuthenticationResponse:
    """Authenticate a customer and return a JWT token."""
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

    token = state.encode_jwt({"customer_id": customer.id}, timedelta(days=5))

    return AuthenticationResponse(
        jwt_token=token, id=customer.id  # type: ignore
    )


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
        created_at=datetime.now(),
    )
    state.session.add(sql_review)
    state.session.flush()
    state.session.commit()

    return sql_review.id
