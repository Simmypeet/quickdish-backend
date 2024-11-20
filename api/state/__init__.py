from dataclasses import dataclass
from sqlalchemy.orm import Session


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ACCESS_TOKEN_EXPIRE_SECOND = 5
REFRESH_TOKEN_EXPIRE_SECOND = 10


@dataclass
class State:
    """Represents the state of within a single request context."""

    session: Session
    """
    The sqlalchemy session object used to interact with the database.
    """
