from pydantic import BaseModel, ConfigDict

from api.schemas.point import Point


class RestaurantBase(BaseModel):
    name: str
    address: str
    location: Point


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    """
    The schema for public restaurant data.
    """

    id: int
    merchant_id: int

    model_config = ConfigDict(from_attributes=True)
