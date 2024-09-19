from pydantic import BaseModel, ConfigDict


class MerchantBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str


class MerchantRegister(MerchantBase):
    password: str


class MerchantLogin(BaseModel):
    username: str
    password: str


class Merchant(MerchantBase):
    """The schema for public merchant data."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class Restaurant(MerchantBase):
    """The schema for public merchant data."""

    id: int

    model_config = ConfigDict(from_attributes=True)
