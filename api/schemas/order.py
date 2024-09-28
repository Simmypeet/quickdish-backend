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


class OrderedOrderBase(BaseModel):
    type: Literal[OrderStatusFlag.ORDERED] = OrderStatusFlag.ORDERED


class OrderedOrder(OrderedOrderBase):
    pass


class CancelledOrderBase(BaseModel):
    type: Literal[OrderStatusFlag.CANCELLED] = OrderStatusFlag.CANCELLED
    reason: str | None


class CancelledOrderUpdate(CancelledOrderBase):
    pass


class CancelledOrder(CancelledOrderBase):
    cancelled_by: OrderCancelledBy
    cancelled_time: int


class PreparingOrderBase(BaseModel):
    type: Literal[OrderStatusFlag.PREPARING] = OrderStatusFlag.PREPARING


class PreparingOrderUpdate(PreparingOrderBase):
    pass


class PreparingOrder(PreparingOrderBase):
    prepared_at: int


class ReadyOrderBase(BaseModel):
    type: Literal[OrderStatusFlag.READY] = OrderStatusFlag.READY


class ReadyOrderUpdate(ReadyOrderBase):
    pass


class ReadyOrder(ReadyOrderBase):
    ready_at: int


class SettledOrderBase(BaseModel):
    type: Literal[OrderStatusFlag.SETTLED] = OrderStatusFlag.SETTLED


class SettledOrderUpdate(SettledOrderBase):
    pass


class SettledOrder(SettledOrderBase):
    settled_at: int


OrderStatus = (
    OrderedOrder | CancelledOrder | PreparingOrder | ReadyOrder | SettledOrder
)

OrderStatusUpdate = (
    CancelledOrderUpdate
    | PreparingOrderUpdate
    | ReadyOrderUpdate
    | SettledOrderUpdate
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
