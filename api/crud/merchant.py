from api.configuration import Configuration
from api.errors import ConflictingError
from api.errors.authentication import AuthenticationError
from api.models.restaurant import Restaurant
from api.schemas.authentication import AuthenticationResponse
from api.state import State
from api.models.merchant import Merchant
from api.schemas.merchant import (
    MerchantLogin,
    MerchantRegister,
)

import hashlib
import datetime
import logging


async def register_merchant(
    state: State,
    configuration: Configuration,
    merchant_register: MerchantRegister,
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

    salt, hashed_password = configuration.generate_password(
        merchant_register.password
    )

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

    token = configuration.encode_jwt(
        {"merchant_id": new_merchant.id}, datetime.timedelta(days=5)
    )
    role = "merchant"

    return AuthenticationResponse(
        jwt_token=token, id=new_merchant.id, role=role  # type:ignore
    )


async def login_merchant(
    state: State, configuration: Configuration, merchant_login: MerchantLogin
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

    token = configuration.encode_jwt(
        {"merchant_id": merchant.id}, datetime.timedelta(days=5)
    )

    role = "merchant"
    return AuthenticationResponse(
        jwt_token=token, id=merchant.id, role=role  # type:ignore
    )


# async def get_merchant(state: State, merchant_id: int) -> Merchant | None:
#     """Get a merchant by their ID."""

#     try:
#         return (
#             state.session.query(Merchant)
#             .filter(Merchant.id == merchant_id)
#             .first()
#         )
#     catch(e):
#         loggin.error(e)


async def get_merchant(state: State, merchant_id: int) -> Merchant | None:
    """Get a merchant by their ID."""
    try:
        return (
            state.session.query(Merchant)
            .filter(Merchant.id == merchant_id)
            .first()
        )
    except Exception as e:  # Corrected syntax
        logging.error(f"Error fetching merchant with ID {merchant_id}: {e}")
        return None  # Return None explicitly in case of an error


async def get_restaurant_by_merchant_id(
    state: State, merchant_id: int
) -> list[Restaurant]:
    """Get a restaurant by its ID."""

    restaurant = (
        state.session.query(Restaurant)
        .filter(Restaurant.merchant_id == merchant_id)
        .all()
    )

    return restaurant
