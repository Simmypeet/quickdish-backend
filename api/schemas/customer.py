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


class Customer(CustomerBase):
    """The schema for public customer data."""

    id: int

    model_config = ConfigDict(from_attributes=True)
