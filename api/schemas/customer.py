from pydantic import BaseModel


class CustomerBase(BaseModel):
    """The base schema for customer data."""

    first_name: str
    last_name: str
    username: str
    email: str


class CutomerRegister(CustomerBase):
    """The schema used to register a new customer."""

    password: str


class CustomerLogin(BaseModel):
    """The schema used to login a customer."""

    username: str
    password: str


class Customer(CustomerBase):
    """
    The schema for customer data. This schema contains all the data of the
    customer including the private information.
    """

    id: int
    hashed_password: str
    salt: str

    class Config:
        from_attributes = True


class AuthenticationResponse(BaseModel):
    """
    The response schema for authentication endpoints.

    The `jwt_token` is used to authenticate the customer in future requests.
    """

    jwt_token: str
    """The JWT token for the newly created customer. This token is used to 
    authenticate the customer in future requests."""


class ConflictingCustomerError(BaseModel):
    """The error schema for the customer registration endpoint."""

    error: str = "an account with the same username or email already exists"


class AuthenticationError(BaseModel):
    """The error schema for the customer authentication endpoints."""

    error: str
