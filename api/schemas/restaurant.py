from pydantic import BaseModel, ConfigDict

from api.schemas.point import Point


class RestaurantBase(BaseModel):
    name: str
    address: str
    location: Point


class RestaurantCreate(RestaurantBase):
    pass


class PublicRestaurant(RestaurantBase):
    """
    The schema for public restaurant data.
    """

    id: int
    merchant_id: int


class Restaurant(PublicRestaurant):
    """
    The schema for restaurant that includes all the information about the
    restaurant. This schema should only be used internally.
    """
    image: str

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
