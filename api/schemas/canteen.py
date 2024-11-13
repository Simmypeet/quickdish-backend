from pydantic import BaseModel

class CanteenBase(BaseModel):
    name: str
    latitude: float
    longitude: float

class GetCanteen(CanteenBase):
    id : int
    img : str
