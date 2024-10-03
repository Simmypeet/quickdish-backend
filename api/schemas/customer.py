from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class CustomerBase(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str

class CustomerRegister(CustomerBase):
    password: str

class CustomerLogin(BaseModel):
    username: str
    password: str


class Customer(CustomerBase):
    """The schema for public customer data."""
    id: int
    model_config = ConfigDict(from_attributes=True)

#customer review
class CustomerReviewBase(BaseModel): 
    restaurant_id: int
    menu_id: int
    
class CustomerReviewCreate(CustomerReviewBase):
    review: str
    tastiness: int
    hygiene: int
    quickness: int
    
class CustomerReview(CustomerReviewBase):
    # id: Optional[int]
    id: Optional[int]
    customer_id: int
    review: str
    tastiness: int
    hygiene: int
    quickness: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)