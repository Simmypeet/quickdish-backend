from fastapi import HTTPException


class InvalidHeaderSchemeError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=400,
            detail={
                "error": "expected 'Bearer' scheme in the 'Authorization' header"
            },
        )


class ExpiredSessionError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail={
                "error": "session has expired; re-authenticate to continue using the service"
            },
        )


class InvalidSessionTokenError(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail={
                "error": "invalid session token; cannot authenticate the user with the given token"
            },
        )
