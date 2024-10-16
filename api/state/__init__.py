from dataclasses import dataclass
from sqlalchemy.orm import Session

ACCESS_TOKEN_EXPIRE_MINUTES = 1  
REFRESH_TOKEN_EXPIRE_DAYS = 7 

@dataclass
class State:
    """Represents the state of within a single request context."""

    session: Session
    """
    The sqlalchemy session object used to interact with the database.
    """
