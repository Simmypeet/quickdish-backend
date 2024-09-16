from typing import Any
from fastapi import UploadFile
import platformdirs
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from api.errors import FileContentTypeError
from api.errors.internal import InternalServerError
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
    __application_data_path: str

    def __init__(
        self,
        session: Session | None = None,
        jwt_secret: str | None = None,
        application_data_path: str | None = None,
    ) -> None:
        """Initialize the state of the FastAPI application.

        :param session: The parameter is for testing pruposes only.
        :param jwt_secret: The jwt secret key used to sign and verify Pass
            `None` to use the JWT_SECRET environment variable.
        :param application_data_path: The path to the application data folder.

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

        if application_data_path:
            self.__application_data_path = application_data_path
        else:
            path: str = platformdirs.user_data_dir("quickdish", "quickdish")
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

    @property
    def application_data_path(self) -> str:
        """The path to the application data folder."""
        return self.__application_data_path

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
