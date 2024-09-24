from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from enum import StrEnum, unique


@unique
class OrderCancelledBy(StrEnum):
    CUSTOMER = "CUSTOMER"
    MERCHANT = "MERCHANT"


@unique
class OrderStatus(StrEnum):
    ORDERED = "ORDERED"
    CANCELLED = "CANCELLED"
    PREPARING = "PREPARING"
    READY = "READY"
    SETTLED = "SETTLED"


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
