from pydantic import BaseModel


class Point(BaseModel):
    lat: float
    lng: float
