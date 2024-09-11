from fastapi import HTTPException


class AuthenticationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=401, detail={"error": message})


class UnauthorizedError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=403, detail={"error": message})
