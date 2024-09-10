from api.state import State
from api.models.merchant import Merchant
from api.schemas.authentication import (
    AuthenticationResponse,
    AuthenticationError,
)
from api.schemas.merchant import (
    ConflictingMerchantError,
    MerchantLogin,
    MerchantRegister,
)

import hashlib
import datetime


async def merchant_register(
    state: State, merchant_register: MerchantRegister
) -> AuthenticationResponse | ConflictingMerchantError:
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
        return ConflictingMerchantError()

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


async def merchant_login(
    state: State, merchant_login: MerchantLogin
) -> AuthenticationResponse | AuthenticationError:
    """Authenticate a merchant and return a JWT token."""
    merchant = (
        state.session.query(Merchant)
        .filter(Merchant.username == merchant_login.username)
        .first()
    )

    if not merchant:
        return AuthenticationError()

    salted_password = merchant_login.password + merchant.salt
    hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    if hashsed_password != merchant.hashed_password:
        return AuthenticationError()

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
