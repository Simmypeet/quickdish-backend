from decimal import Decimal
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

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


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(
        Numeric(precision=10, scale=2, asdecimal=True), nullable=False
    )
    image = Column(String, nullable=True)
    estimated_prep_time = Column(Integer, nullable=True)


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
