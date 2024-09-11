from pydantic import BaseModel, ConfigDict

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
    location: Point


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int
    merchant_id: int

    model_config = ConfigDict(from_attributes=True)


class Merchant(MerchantBase):
    """
    The schema for merchant data. This schema contains all the data of the
    merchant including the private information.
    """

    id: int
    hashed_password: str
    salt: str

    model_config = ConfigDict(from_attributes=True)
