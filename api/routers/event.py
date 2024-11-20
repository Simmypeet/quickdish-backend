from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Request

from sse_starlette import EventSourceResponse

from api.dependencies.id import Role, get_user
from api.dependencies.event import get_event

from api.event import Event, User, Listener


router = APIRouter(
    prefix="/events",
    tags=["event"],
)


async def event_generator(
    event: Event,
    listener: Listener,
) -> AsyncGenerator[str, None]:
    while True:
        notification = await listener

        if notification is None:
            break

        yield str(notification.model_dump_json())

    event.remove_listener(listener)


@router.get(
    "/",
    description="""
        Returns a Seerver-Sent-Event (SSE) for the user. All notifications 
        related to the user will be sent through this endpoint. The sent
        noficiation will be in JSON format. The schemas of the notifications
        are named in `*Notification` patterns e.g. 
        `OrderStatusChangeNotification`, `OrderQueueChangeNotification`.
    """,
    response_class=EventSourceResponse,
)
def get_events_api(
    request: Request,
    user: tuple[int, Role] = Depends(get_user),
    event: Event = Depends(get_event),
) -> EventSourceResponse:
    connection = event.listens(User(user_id=user[0], role=user[1]), request)

    return EventSourceResponse(event_generator(event, connection))
