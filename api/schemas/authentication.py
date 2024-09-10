from pydantic import BaseModel


class AuthenticationResponse(BaseModel):
    """
    The response schema for authentication endpoints.

    The `jwt_token` is used to authenticate the customer/merchant in future
    requests.
    """

    jwt_token: str


class AuthenticationError(BaseModel):
    error: str = "username or password is incorrect"
