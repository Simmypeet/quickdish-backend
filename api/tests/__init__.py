from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from api.models import Base
from api.state import State

import alembic.config

_test_state: State | None = None


DATABASE_URL = "sqlite://"
"""Database URL for the in-memory SQLite database."""

JWT = "easyjwt"
"""The JWT secret key used to sign and verify JWT tokens."""


def override_get_state() -> State:
    """Use this function to override the `get_state` dependency in the FastAPI
    application. The overidden state will use the in-memory SQLite database
    for testing purposes.
    """
    global _test_state

    if _test_state is None:

        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

        # specify the db_path x argument
        alembic.config.main(
            argv=[
                "--raiseerr",
                "-x",
                f"db_path={DATABASE_URL}",
                "upgrade",
                "head",
            ]
        )

        TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        _test_state = State(TestingSessionLocal(), JWT)

        Base.metadata.create_all(bind=engine)

    return _test_state
