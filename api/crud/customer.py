from pydantic import BaseModel

from api.state import State
from api.models.customer import Customer
from api.schemas.customer import CustomerLogin, CutomerRegister

import jwt
import secrets
import string
import hashlib
import datetime


class AuthenticationResponse(BaseModel):
    """The response model for authentication endpoints.

    The `jwt_token` is used to authenticate the customer in future requests.
    """

    jwt_token: str
    """The JWT token for the newly created customer. This token is used to 
    authenticate the customer in future requests."""


class ConflictingCustomerError(BaseModel):
    """The error model for the customer registration endpoint."""

    error: str = "an account with the same username or email already exists"


class AuthenticationError(BaseModel):
    """The error model for the customer authentication endpoints."""

    error: str


async def customer_register(
    state: State, customer_create: CutomerRegister
) -> AuthenticationResponse | ConflictingCustomerError:
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
        return ConflictingCustomerError()

    characters = string.ascii_letters + string.digits
    salt = "".join(secrets.choice(characters) for _ in range(16))

    salted_password = customer_create.password + salt
    hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    new_customer = Customer(
        first_name=customer_create.first_name,
        last_name=customer_create.last_name,
        username=customer_create.username,
        email=customer_create.email,
        hashed_password=hashsed_password,
        salt=salt,
    )

    state.session.add(new_customer)
    state.session.commit()

    state.session.refresh(new_customer)

    exp_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=5)

    token = jwt.encode(  # type:ignore
        {"customer_id": new_customer.id, "exp": exp_time},
        state.jwt_secret,
        algorithm="HS256",
    )

    return AuthenticationResponse(jwt_token=token)


async def customer_login(
    state: State, customer_login: CustomerLogin
) -> AuthenticationResponse | AuthenticationError:
    """Authenticate a customer and return a JWT token."""
    customer = (
        state.session.query(Customer)
        .filter(Customer.username == customer_login.username)
        .first()
    )

    if not customer:
        return AuthenticationError(error="username or password is incorrect")

    salted_password = customer_login.password + customer.salt
    hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

    if hashsed_password != customer.hashed_password:
        return AuthenticationError(error="username or password is incorrect")

    exp_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=5)

    token = jwt.encode(  # type:ignore
        {"customer_id": customer.id, "exp": exp_time},
        state.jwt_secret,
        algorithm="HS256",
    )

    return AuthenticationResponse(jwt_token=token)
