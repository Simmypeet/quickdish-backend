from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class BaseMenu(BaseModel):
    name: str
    description: str
    price: Decimal
    estimated_prep_time: int | None


class MenuCreate(BaseMenu):
    pass


class PublicMenu(BaseMenu):
    """The schema for public menu data."""

    id: int
    restaurant_id: int


class Menu(PublicMenu):
    """
    The schema for menu that includes all the information about the menu.
    This schema should only be used internally.
    """

    image: str | None

    model_config = ConfigDict(from_attributes=True)
