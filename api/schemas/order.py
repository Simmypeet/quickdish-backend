from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict
from enum import StrEnum, unique


@unique
class OrderCancelledBy(StrEnum):
    CUSTOMER = "CUSTOMER"
    MERCHANT = "MERCHANT"


@unique
class OrderStatusFlag(StrEnum):
    ORDERED = "ORDERED"
    CANCELLED = "CANCELLED"
    PREPARING = "PREPARING"
    READY = "READY"
    SETTLED = "SETTLED"


class OrderedOrder(BaseModel):
    type: Literal[OrderStatusFlag.ORDERED] = OrderStatusFlag.ORDERED


class CancelledOrder(BaseModel):
    type: Literal[OrderStatusFlag.CANCELLED] = OrderStatusFlag.CANCELLED
    cancelled_by: OrderCancelledBy
    cancelled_time: int
    reason: str | None


class PreparingOrder(BaseModel):
    type: Literal[OrderStatusFlag.PREPARING] = OrderStatusFlag.PREPARING
    prepared_at: int


class ReadyOrder(BaseModel):
    type: Literal[OrderStatusFlag.READY] = OrderStatusFlag.READY
    ready_at: int


class SettledOrder(BaseModel):
    type: Literal[OrderStatusFlag.SETTLED] = OrderStatusFlag.SETTLED
    settled_at: int


OrderStatus = (
    OrderedOrder | CancelledOrder | PreparingOrder | ReadyOrder | SettledOrder
)


class OrderItemOptionBase(BaseModel):
    option_id: int


class OrderItemOptionCreate(OrderItemOptionBase):
    pass


class OrderItemOption(OrderItemOptionBase):
    order_item_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderItemBase(BaseModel):
    menu_id: int
    quantity: int
    extra_requests: str | None


class OrderItemCreate(OrderItemBase):
    options: list[OrderItemOptionCreate]


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    options: list[OrderItemOption]

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    restaurant_id: int


class OrderCreate(OrderBase):
    items: list[OrderItemCreate]


class Order(OrderBase):
    id: int
    customer_id: int
    items: list[OrderItem]
    status: OrderStatus
    price_paid: Decimal
    ordered_at: int

    model_config = ConfigDict(from_attributes=True)
