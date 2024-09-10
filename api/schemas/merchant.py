from pydantic import BaseModel


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
    """
    The schema for merchant data. This schema contains all the data of the
    merchant including the private information.
    """

    id: int
    hashed_password: str
    salt: str

    class Config:
        from_attributes = True


class ConflictingMerchantError(BaseModel):
    error: str = "an account with the same username or email already exists"
