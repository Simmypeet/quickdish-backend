from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from api.models import Base

import alembic.config

import dotenv
import os
import datetime
import jwt
import string
import secrets
import hashlib


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

    def encode_jwt(
        self, payload: dict[str, Any], token_duration: datetime.timedelta
    ) -> str:
        """Encode a payload into a JWT token.

        :param payload: The payload to encode.
        :param token_duration: The duration of the token to be valid.
        """
        exp_time = (
            datetime.datetime.now(datetime.timezone.utc) + token_duration
        )

        payload["exp"] = exp_time

        return jwt.encode(  # type:ignore
            payload,
            self.jwt_secret,
            algorithm="HS256",
        )

    def generate_password(self, plain_password: str) -> tuple[str, str]:
        """Generate a salted and hashed password.

        :param plain_password: The password to hash.

        Returns:
            A tuple containing the salt and hashed password respectively.
        """

        characters = string.ascii_letters + string.digits
        salt = "".join(secrets.choice(characters) for _ in range(16))

        salted_password = plain_password + salt
        hashsed_password = hashlib.sha256(salted_password.encode()).hexdigest()

        return salt, hashsed_password
