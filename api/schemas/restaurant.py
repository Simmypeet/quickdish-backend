from decimal import Decimal
from pydantic import BaseModel, ConfigDict

from api.schemas.point import Point


class RestaurantBase(BaseModel):
    name: str
    address: str
    location: Point
    canteen_id: int

class RestaurantCreate(RestaurantBase):
    pass

class GetRestaurant(RestaurantBase):
    id: int
    merchant_id: int
    img: str


class Restaurant(RestaurantBase):
    """
    The schema for public restaurant data.
    """

    id: int
    merchant_id: int
    open: bool
    model_config = ConfigDict(from_attributes=True)


class BaseMenu(BaseModel):
    name: str
    description: str
    price: Decimal
    estimated_prep_time: int | None


class MenuCreate(BaseMenu):
    pass


class Menu(BaseMenu):
    """The schema for public menu data."""

    id: int
    restaurant_id: int

    model_config = ConfigDict(from_attributes=True)


class OptionBase(BaseModel):
    name: str
    description: str | None
    extra_price: Decimal | None


class OptionCreate(OptionBase):
    pass


class Option(OptionBase):
    customization_id: int
    id: int

    model_config = ConfigDict(from_attributes=True)


class CustomizationBase(BaseModel):
    title: str
    description: str | None
    unique: bool
    required: bool


class CustomizationCreate(CustomizationBase):
    """Used for creating a new customization for a menu item."""

    options: list[OptionCreate]


class Customization(CustomizationBase):
    """The schema for public customization data."""

    id: int
    menu_id: int
    options: list[Option]

    model_config = ConfigDict(from_attributes=True)
