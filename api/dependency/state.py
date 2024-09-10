# State dependency
from api.state import State


_state: None | State = None


def get_state():
    """Use this dependency to get the `State` object"""

    global _state

    try:
        if _state is None:
            _state = State()

        yield _state
    finally:
        if _state is not None:
            _state.session.flush()
            _state.session.close()
