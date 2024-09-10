from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from api.models import Base

import alembic.config

import dotenv
import os


class State:
    """The state of the FastAPI application. This class is used to store the
    application's configuration and dependencies."""

    __session: Session
    __jwt_secret: str

    def __init__(
        self, session: Session | None = None, jwt_secret: str | None = None
    ) -> None:
        """Initialize the state of the FastAPI application.

        :param session: The parameter is for testing pruposes only.
        :param jwt_secret: The jwt secret key used to sign and verify Pass
            `None` to use the JWT_SECRET environment variable.

        Raises:
            RuntimeError: if the DATABASE_URL or JWT_SECRET environment
                variables are not set.
        """
        if session:
            self.__session = session
        else:
            dotenv.load_dotenv()
            database_url = os.getenv("DATABASE_URL")

            if not database_url:
                raise RuntimeError(
                    "DATABASE_URL environment variable is not set"
                )

            engine = create_engine(database_url, connect_args={})

            # run migrations
            alembic.config.main(argv=["upgrade", "head"])  # type:ignore

            SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=engine
            )

            self.__session = SessionLocal()
            Base.metadata.create_all(bind=engine)

        if jwt_secret:
            self.__jwt_secret = jwt_secret
        else:
            dotenv.load_dotenv()
            jwt_secret = os.getenv("JWT_SECRET")

            if not jwt_secret:
                raise RuntimeError(
                    "JWT_SECRET environment variable is not set"
                )

            self.__jwt_secret = jwt_secret

    @property
    def session(self) -> Session:
        """The SQLAlchemy session object used to interact with the database."""
        return self.__session

    @property
    def jwt_secret(self) -> str:
        """The secret key used to sign and verify JWT tokens."""
        return self.__jwt_secret
