from sqlalchemy import Column, ForeignKey, Integer, String
from api.models import Base
from api.types.point import PointType


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    image = Column(String, nullable=False)
    location = Column(PointType, nullable=False)
