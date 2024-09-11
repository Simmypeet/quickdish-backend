from api.errors import ConflictingError, NotFoundError
from api.errors.authentication import AuthenticationError
from api.schemas.authentication import AuthenticationResponse
from api.state import State
from api.models.customer import Customer
from api.schemas.customer import (
    CustomerLogin,
    CutomerRegister,
)

import hashlib
import datetime


async def customer_register(
    state: State, customer_create: CutomerRegister
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
        {"customer_id": new_customer.id}, datetime.timedelta(days=5)
    )

    return AuthenticationResponse(jwt_token=token)


async def customer_login(
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

    token = state.encode_jwt(
        {"customer_id": customer.id}, datetime.timedelta(days=5)
    )

    return AuthenticationResponse(jwt_token=token)


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
