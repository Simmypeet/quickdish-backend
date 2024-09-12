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


class PublicMerchant(MerchantBase):
    """The schema for public merchant data."""

    id: int


class PrivateMerchant(PublicMerchant):
    """The schema for merchant data that includes private information."""

    pass


class Merchant(PrivateMerchant):
    """
    The schema for merchant that includes all the information about the
    merchant. This schema should only be used internally.
    """

    hashed_password: str
    salt: str

    model_config = ConfigDict(from_attributes=True)
