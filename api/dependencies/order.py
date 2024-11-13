from api.crud.order import OrderEvent


_order_event: None | OrderEvent = None


def get_order_event() -> OrderEvent:
    """Use this dependency to get the `OrderEvent` object"""

    global _order_event

    if _order_event is None:
        _order_event = OrderEvent()

    return _order_event
