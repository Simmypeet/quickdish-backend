from pydantic import BaseModel

from api.state import State
from api.models.customer import Customer
from api.schemas.customer import CustomerCreate

import jwt
import secrets
import string
import hashlib
import datetime


class CreateResponse(BaseModel):
    """The response model for the create_customer endpoint."""

    jwt_token: str
    """The JWT token for the newly created customer. This token is used to 
    authenticate the customer in future requests."""


class ConflictingUsernameError(BaseModel):
    """The error model for the create_customer endpoint."""

    error: str = "an account with the same username or email already exists"


async def create_customer(
    state: State, customer_create: CustomerCreate
) -> CreateResponse | ConflictingUsernameError:
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
        return ConflictingUsernameError()

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

    return CreateResponse(jwt_token=token)
