from pydantic import BaseModel, ConfigDict


class CanteenBase(BaseModel):
    name: str
    latitude: float
    longitude: float


class Canteen(CanteenBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
