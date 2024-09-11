from api.models import Base

from sqlalchemy import Column, ForeignKey, Integer, String

from api.types.point import PointType


class Merchant(Base):  # type:ignore
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    salt = Column(String, nullable=False)


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    image = Column(String, nullable=False)
    location = Column(PointType, nullable=False)
