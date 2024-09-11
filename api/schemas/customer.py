from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str


class CutomerRegister(CustomerBase):
    password: str


class CustomerLogin(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)
