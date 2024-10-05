from typing import Generator
from fastapi import Depends
from api.configuration import Configuration
from api.dependencies.configuration import get_configuration
from api.state import State


def get_state(
    configuration: Configuration = Depends(get_configuration),
) -> Generator[State, None, None]:
    session = configuration.create_session()

    try:
        yield State(session=session)
    finally:
        session.close()
