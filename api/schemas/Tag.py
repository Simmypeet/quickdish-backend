from pydantic import BaseModel

class Tag(BaseModel):
    title: str
    
class RestaurantTagCreate(BaseModel):
    tag_id: int
    restaurant_id: int

class RestaurantTag(RestaurantTagCreate):
    pass
    
    
    


