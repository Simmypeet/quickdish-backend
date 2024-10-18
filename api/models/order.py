from api.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.schemas.order import OrderCancelledBy, OrderStatusFlag

from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, Enum, PrimaryKeyConstraint


class OrderOption(Base):
    __tablename__ = "order_options"
    __table_args__ = (PrimaryKeyConstraint("order_item_id", "option_id"),)

    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id"))
    option_id: Mapped[int] = mapped_column(ForeignKey("options.id"))


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    menu_id: Mapped[int] = mapped_column(ForeignKey("menus.id"))
    quantity: Mapped[int]
    extra_requests: Mapped[str | None]

    options: Mapped[list[OrderOption]] = relationship(
        OrderOption, backref="order_item"
    )


class PreparingOrder(Base):
    __tablename__ = "preparing_orders"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    prepared_at: Mapped[int]


class SettledOrder(Base):
    __tablename__ = "settled_orders"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    settled_at: Mapped[int]


class ReadyOrder(Base):
    __tablename__ = "ready_orders"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    ready_at: Mapped[int]


class CancelledOrder(Base):
    __tablename__ = "cancelled_orders"

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    cancelled_time: Mapped[int]
    cancelled_by: Mapped[OrderCancelledBy] = mapped_column(
        Enum(OrderCancelledBy, name="order_cancelled_by")
    )
    reason: Mapped[str | None]


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[OrderStatusFlag] = mapped_column(
        Enum(OrderStatusFlag, name="order_status")
    )
    price_paid: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2, asdecimal=True)
    )
    ordered_at: Mapped[int]

    items: Mapped[list[OrderItem]] = relationship(OrderItem, backref="order")
