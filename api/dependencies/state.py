# State dependency
from api.state import State


_state: None | State = None


def get_state() -> State:
    """Use this dependency to get the `State` object"""

    global _state

    if _state is None:
        _state = State()

    return _state
