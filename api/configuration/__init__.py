from typing import Any, Callable

from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.errors import FileContentTypeError
from api.errors.internal import InternalServerError
from api.models import Base
from platformdirs import user_data_dir

import alembic.config

import os
import dotenv
import datetime
import jwt
import string
import secrets
import hashlib

ACCESS_TOKEN_EXPIRE_MINUTES: int = 1
REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class Configuration:
    """
    The configuration of the FastAPI application. This class is used to store
    the application's configuration and dependencies.
    """

    __session_maker: Callable[[], Session]

    __jwt_secret: str
    __application_data_path: str

    def __init__(
        self,
        session_maker: Callable[[], Session] | None = None,
        jwt_secret: str | None = None,
        application_data_path: str | None = None,
    ) -> None:
        """Initialize the configuration of the FastAPI application.

        These parameters are used to configure the application. In production,
        should leave the parameters as `None` to use the environment variables.
        The parameters are for testing purposes only.

        :param session_maker: The function that returns a new SQLAlchemy \
            session. If `None` the configuration will look for `DATABASE_URL` \
            in the environment variables and creates a session maker from it.
        :param jwt_secret: The jwt secret key used to sign and verify Pass \
            `None` to use the JWT_SECRET environment variable.
        :param application_data_path: The path to the application data folder. \
            If `None`, the state will look for `APPLICATION_DATA_PATH` in the \
            environment variables. If not found, the state will use a \
            directory `quickdish` in user data directory. The state will \
            ensure that the directory exists and is writable.

        Raises:
            RuntimeError: if the DATABASE_URL or JWT_SECRET environment
                variables are not set.
        """

        if session_maker:
            self.__session_maker = session_maker
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

            self.__session_maker = sessionmaker(
                autocommit=False, autoflush=False, bind=engine
            )

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

        if application_data_path:
            self.__application_data_path = application_data_path
        else:
            path_from_env = os.getenv("APPLICATION_DATA_PATH")

            if path_from_env:
                self.__application_data_path = path_from_env
            else:
                path: str = user_data_dir("quickdish", "quickdish")
                self.__application_data_path = path

        if not os.path.exists(self.__application_data_path):
            os.makedirs(self.__application_data_path, exist_ok=True)

            if not os.path.exists(self.__application_data_path):
                raise RuntimeError(
                    f"Could not create application data folder at "
                    f"{self.__application_data_path}"
                )

        if not os.path.isdir(self.__application_data_path):
            raise RuntimeError(
                f"{self.__application_data_path} is not a directory"
            )

        # check if it's writable
        if not os.access(self.__application_data_path, os.W_OK):
            raise RuntimeError(
                f"{self.__application_data_path} is not writable"
            )

    def create_session(self) -> Session:
        """Create a new SQLAlchemy session.

        This function shouldn't be used directly within the CRUD functions.
        Instead, use the `State` via `get_state` dependency.

        :return: A new SQLAlchemy session.
        """

        return self.__session_maker()

    @property
    def jwt_secret(self) -> str:
        """Get the JWT secret key.

        :return: The JWT secret key.
        """

        return self.__jwt_secret

    @property
    def application_data_path(self) -> str:
        """Get the application data path.

        :return: The application data path.
        """

        return self.__application_data_path

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

    async def upload_image(
        self, image: UploadFile, directory_path: str
    ) -> str:
        """Upload an image to the application data folder.

        :param image: The image to upload.
        :param path: The directory path to save the image.

        Returns:
            The path to the uploaded image.
        """

        image_directory = os.path.join(
            self.application_data_path, directory_path
        )

        try:
            os.makedirs(image_directory, exist_ok=True)
        except OSError as e:
            raise InternalServerError(
                f"could not create image directory at {image_directory}: {e}"
            )

        if not os.path.isdir(image_directory):
            raise InternalServerError(
                f"{image_directory} is not a directory or not exists"
            )

        if not image.filename:
            raise InternalServerError("image filename is empty")

        if not image.content_type:
            raise FileContentTypeError("unknown file content type")

        if not image.content_type.startswith("image/"):
            raise FileContentTypeError("file is not an image")

        image_extension = os.path.splitext(image.filename)[1]

        image_path = os.path.join(image_directory, f"image{image_extension}")

        if not os.access(image_directory, os.W_OK):
            raise InternalServerError(f"{image_directory} is not writable")

        try:
            with open(image_path, "wb") as f:
                f.write(await image.read())

        except Exception as e:
            raise InternalServerError(
                f"could not save image at `{image_path}`: {e}"
            )

        return image_path

    def create_refresh_token(self, payload: dict[str, Any]) -> str:
        """Create a refresh token."""
        exp_time = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        payload["exp"] = exp_time
        return jwt.encode(  # type:ignore
            payload, self.jwt_secret, algorithm="HS256"
        )
