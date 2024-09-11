from fastapi import HTTPException


class ConflictingError(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=409, detail={"error": msg})


class NotFoundError(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=404, detail={"error": msg})