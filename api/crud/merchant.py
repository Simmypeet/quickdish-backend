import os
from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import AuthenticationError, UnauthorizedError
from api.schemas.authentication import AuthenticationResponse
from api.state import State
from api.models.merchant import Merchant, Restaurant
from api.schemas.merchant import (
    MerchantLogin,
    MerchantRegister,
    RestaurantCreate,
)

import hashlib
import datetime


async def register_merchant(
    state: State, merchant_register: MerchantRegister
) -> AuthenticationResponse:
    """Create a new merchant in the database."""

    # Check if a merchant with the same username or email already exists
    existing_merchant = (
        state.session.query(Merchant)
        .filter(
            (Merchant.username == merchant_register.username)
            | (Merchant.email == merchant_register.email),
        )
        .first()
    )

    if existing_merchant:
        raise ConflictingError(
            "an account with the same username or email already exists"
        )

    salt, hashed_password = state.generate_password(merchant_register.password)

    new_merchant = Merchant(
        first_name=merchant_register.first_name,
        last_name=merchant_register.last_name,
        username=merchant_register.username,
        email=merchant_register.email,
        hashed_password=hashed_password,
        salt=salt,
    )

    state.session.add(new_merchant)
    state.session.commit()

    state.session.refresh(new_merchant)

    token = state.encode_jwt(
        {"merchant_id": new_merchant.id}, datetime.timedelta(days=5)
    )

    return AuthenticationResponse(jwt_token=token)


async def login_merchant(
    state: State, merchant_login: MerchantLogin
) -> AuthenticationResponse:
    """Authenticate a merchant and return a JWT token."""
    merchant = (
        state.session.query(Merchant)
        .filter(Merchant.username == merchant_login.username)
        .first()
    )

    if not merchant:
        raise AuthenticationError("invalid username or password")

    salted_password = merchant_login.password + merchant.salt
    hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    if hashsed_password != merchant.hashed_password:
        raise AuthenticationError("invalid username or password")

    token = state.encode_jwt(
        {"merchant_id": merchant.id}, datetime.timedelta(days=5)
    )

    return AuthenticationResponse(jwt_token=token)


async def get_merchant(state: State, merchant_id: int) -> Merchant | None:
    """Get a merchant by their ID."""
    return (
        state.session.query(Merchant)
        .filter(Merchant.id == merchant_id)
        .first()
    )


async def create_restaurant(
    state: State, merchant_id: int, restaurant_create: RestaurantCreate
) -> int:
    # Checks if there's a restaurant with the same name
    existing_restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.name == restaurant_create.name)
        .first()
    )

    if existing_restaurant:
        raise ConflictingError(
            "a restaurant with the same name already exists"
        )

    # Check if the merchant exists
    merchant = await get_merchant(state, merchant_id)
    if not merchant:
        raise NotFoundError("merchant not found")

    default_image = os.getcwd() + "/api/assets/default_restaurant.jpeg"

    new_restaurant = Restaurant(
        name=restaurant_create.name,
        address=restaurant_create.address,
        location=restaurant_create.location,
        merchant_id=merchant_id,
        image=default_image,
    )

    state.session.add(new_restaurant)
    state.session.commit()

    state.session.refresh(new_restaurant)

    return new_restaurant.id  # type:ignore


async def get_restaurant(
    state: State, restaurant_id: int, merchant_id: int
) -> Restaurant:
    """Get a restaurant by its ID."""

    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.id == restaurant_id)
        .first()
    )

    if not restaurant:
        raise NotFoundError("restaurant not found")

    if restaurant.merchant_id != merchant_id:  # type:ignore
        raise UnauthorizedError("merchant does not own this restaurant")

    return restaurant
