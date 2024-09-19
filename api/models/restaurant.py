from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from api.models import Base
from api.schemas.point import Point
from api.types.point import PointType


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"))
    image: Mapped[str]
    location: Mapped[Point] = mapped_column(PointType)
