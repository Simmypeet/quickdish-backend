from pydantic import BaseModel

class CanteenBase(BaseModel):
    name: str
    latitude: float
    longitude: float
