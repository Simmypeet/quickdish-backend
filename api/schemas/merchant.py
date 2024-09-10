from pydantic import BaseModel

from api.schemas.point import Point


class MerchantBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str


class MerchantRegister(MerchantBase):
    password: str


class MerchantLogin(BaseModel):
    username: str
    password: str


class RestaurantBase(BaseModel):
    name: str
    address: str
    image: str
    location: Point


class Restaurant(RestaurantBase):
    id: int
    merchant_id: int

    class Config:
        from_attributes = True


class Merchant(MerchantBase):
    """
    The schema for merchant data. This schema contains all the data of the
    merchant including the private information.
    """

    id: int
    hashed_password: str
    salt: str
    restaurants: list[Restaurant]

    class Config:
        from_attributes = True


class ConflictingMerchantError(BaseModel):
    error: str = "an account with the same username or email already exists"
