from api.event import Event

_event: None | Event = None


def get_event() -> Event:
    global _event

    if _event is None:
        _event = Event()

    return _event
