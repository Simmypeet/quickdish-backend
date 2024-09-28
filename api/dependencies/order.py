from api.crud.order import OrderEvent
from api.dependencies.state import get_state
from api.state import State

from fastapi import Depends


_order_event: None | OrderEvent = None


def get_order_event(
    state: State = Depends(get_state),
) -> OrderEvent:
    """Use this dependency to get the `OrderEvent` object"""

    global _order_event

    if _order_event is None:
        _order_event = OrderEvent(state)

    return _order_event
