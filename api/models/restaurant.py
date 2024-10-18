from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import relationship, Mapped, mapped_column

from api.models import Base
from api.schemas.point import Point
from api.types.point import PointType


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    address: Mapped[str]
    merchant_id: Mapped[int] = mapped_column(ForeignKey("merchants.id"))
    image: Mapped[str | None]
    location: Mapped[Point] = mapped_column(PointType)
    open: Mapped[bool]


class Menu(Base):
    __tablename__ = "menus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2, asdecimal=True)
    )
    image: Mapped[str | None]
    estimated_prep_time: Mapped[int | None]


class Option(Base):
    __tablename__ = "options"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customization_id: Mapped[int] = mapped_column(
        ForeignKey("customizations.id")
    )
    name: Mapped[str]
    description: Mapped[str | None]
    extra_price: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=10, scale=2, asdecimal=True)
    )


class Customization(Base):
    __tablename__ = "customizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"))
    title: Mapped[str]
    description: Mapped[str | None]
    unique: Mapped[bool]
    required: Mapped[bool]

    options: Mapped[list[Option]] = relationship(
        "Option", backref="customization"
    )
