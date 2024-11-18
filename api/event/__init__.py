from typing import Generator
from fastapi import Request
from api.dependencies.id import Role
from api.schemas.event import Notification

from dataclasses import dataclass
from threading import Lock


@dataclass(
    frozen=True,
    eq=True,
    order=True,
)
class User:
    """Represents a user where the notifications can be sent to."""

    user_id: int
    """The user ID of the listener."""

    role: Role
    """The role of the listener."""


class Listener:
    """Represents a listener to the event."""

    __request: Request
    __notifications: list[Notification]
    __mutex: Lock
    __user: User

    def __init__(self, user: User, request: Request) -> None:
        self.__request = request
        self.__notifications = []
        self.__mutex = Lock()
        self.__user = user

    async def is_disconnected(self) -> bool:
        """
        Returns True if the connection is disconnected.
        """

        return await self.__request.is_disconnected()

    def add_notification(self, notification: Notification) -> None:
        """
        Adds a notification to the listener.
        """

        with self.__mutex:
            self.__notifications.append(notification)

    def __await__(self) -> Generator[None, None, Notification | None]:
        while True:
            is_disconnected = yield from self.is_disconnected().__await__()

            # if the connection is disconnected, return None.
            if is_disconnected:
                return None

            with self.__mutex:
                if self.__notifications:
                    return self.__notifications.pop(0)

            # return the control to the event loop.
            yield

    @property
    def user(self) -> User:
        return self.__user


class Event:
    __listeners_by_user: dict[User, list[Listener]]
    __mutex: Lock

    def __init__(self) -> None:
        self.__listeners_by_user = {}
        self.__mutex = Lock()

    def listens(self, user: User, request: Request) -> Listener:
        """
        Creates a new listener for the user.
        """

        with self.__mutex:
            connections = self.__listeners_by_user.setdefault(user, [])
            connection = Listener(user, request)
            connections.append(connection)

            return connection

    def remove_listener(self, connection: Listener) -> None:
        """
        Removes the connection from the event.
        """

        with self.__mutex:
            connections = self.__listeners_by_user.get(connection.user)

            if connections is None:
                return

            connections.remove(connection)

    async def add_notification(
        self, user: User, notification: Notification
    ) -> None:
        """
        Adds a notification to the user.
        """

        with self.__mutex:
            connections = self.__listeners_by_user.get(user)

            if connections is None:
                return

            removing: list[Listener] = []

            for connection in connections:
                if await connection.is_disconnected():
                    removing.append(connection)
                else:
                    connection.add_notification(notification)

            for connection in removing:
                connections.remove(connection)
