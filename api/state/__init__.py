from dataclasses import dataclass
from sqlalchemy.orm import Session


@dataclass
class State:
    """Represents the state of within a single request context."""

    session: Session
    """
    The sqlalchemy session object used to interact with the database.
    """
