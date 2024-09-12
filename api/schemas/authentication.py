from pydantic import BaseModel


class AuthenticationResponse(BaseModel):
    """
    A response model for successful authentication.

    The response contains the JWT token that the client can use to authenticate
    themselves in the future.
    """

    jwt_token: str
    id: int
