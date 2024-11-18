from api.schemas.order import OrderStatus, Queue

from enum import StrEnum, unique
from typing import Literal
from pydantic import BaseModel


@unique
class NotificationFlag(StrEnum):
    """
    Enumeration of all kinds of notification that the user can recieve
    """

    ORDER_STATUS_CHANGE = "ORDER_STATUS_CHANGE"
    ORDER_QUEUE_CHANGE = "ORDER_QUEUE_CHANGE"


class OrderStatusChangeNotification(BaseModel):
    """
    Notification for order status change. This notification will be sent for
    both customer and merchant
    """

    type: Literal[NotificationFlag.ORDER_STATUS_CHANGE] = (
        NotificationFlag.ORDER_STATUS_CHANGE
    )

    order_id: int
    status: OrderStatus


class OrderQueueChangeNotification(BaseModel):
    """
    Notification for queue change for their ongoing order. This notification
    will be sent for the customer that has ongoing orders (ORDERED and
    PREPARING).
    """

    type: Literal[NotificationFlag.ORDER_QUEUE_CHANGE] = (
        NotificationFlag.ORDER_QUEUE_CHANGE
    )

    order_id: int
    queue: Queue


Notification = OrderStatusChangeNotification | OrderQueueChangeNotification
"""
Union of all possible notifications
"""
