from pydantic import BaseModel


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

    class Config:
        from_attributes = True
