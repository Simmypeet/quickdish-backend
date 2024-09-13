from fastapi import HTTPException


class InternalServerError(HTTPException):
    """
    An error occurred which is likely due to a bug in the server logic.
    """

    def __init__(self, message: str) -> None:
        super().__init__(status_code=500, detail={"error": message})
