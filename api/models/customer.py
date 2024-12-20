from api.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from datetime import datetime
from api.models.restaurant import Restaurant, Menu


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    salt: Mapped[str]
    profile_pic: Mapped[str | None]
    userpage_pic: Mapped[str | None]


class CustomerReview(Base):
    __tablename__ = "customer_reviews"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    customer = relationship(Customer, backref="customer_reviews")

    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    restaurant = relationship(Restaurant, backref="customer_reviews")

    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"))
    menu = relationship(Menu, backref="menu")

    review: Mapped[str]
    tastiness: Mapped[int]
    hygiene: Mapped[int]
    quickness: Mapped[int]
    created_at: Mapped[datetime]


class FavoriteRestaurant(Base):
    __tablename__ = "favorite_restaurants"
    __table_args__ = (PrimaryKeyConstraint("restaurant_id", "customer_id"),)

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), nullable=False
    )
