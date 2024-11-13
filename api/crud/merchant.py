from api.errors import ConflictingError
from api.errors.authentication import AuthenticationError
from api.schemas.authentication import AuthenticationResponse
from api.state import State
from api.models.merchant import Merchant
from api.schemas.merchant import (
    MerchantLogin,
    MerchantRegister,
)

import hashlib
import datetime


async def register_merchant(
    state: State, merchant_register: MerchantRegister
) -> AuthenticationResponse:
    """Create a new merchant in the database."""
    try: 
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
            {"merchant_id": new_merchant.id}
        )
        role = "merchant"

        return AuthenticationResponse(
            jwt_token=token, id=new_merchant.id, role=role  # type:ignore
        )
    except Exception as e:
        print(e)
        return None


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
        {"merchant_id": merchant.id}
    )

    role = "merchant"
    return AuthenticationResponse(
        jwt_token=token, id=merchant.id, role= role  # type:ignore
    )


async def get_merchant(state: State, merchant_id: int) -> Merchant | None:
    """Get a merchant by their ID."""
    return (
        state.session.query(Merchant)
        .filter(Merchant.id == merchant_id)
        .first()
    )
    
