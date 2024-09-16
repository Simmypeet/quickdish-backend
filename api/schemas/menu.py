from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class BaseMenu(BaseModel):
    name: str
    description: str
    price: Decimal
    estimated_prep_time: int | None


class MenuCreate(BaseMenu):
    pass


class Menu(BaseMenu):
    id: int
    restaurant_id: int

    model_config = ConfigDict(from_attributes=True)
