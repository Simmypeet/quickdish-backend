from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str


class CustomerRegister(CustomerBase):
    password: str


class CustomerLogin(BaseModel):
    username: str
    password: str


class PublicCustomer(CustomerBase):
    """The schema for public customer data."""

    id: int

    pass


class PrivateCustomer(PublicCustomer):
    """The schema for customer data that includes private information."""

    pass


class Customer(PrivateCustomer):
    """
    The schema for customer that includes all the information about the
    customer. This schema should only be used internally.
    """

    hashed_password: str
    salt: str

    model_config = ConfigDict(from_attributes=True)
