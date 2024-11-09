from pydantic import BaseModel, ConfigDict

class Tag(BaseModel):
    title: str
    
class RestaurantTagCreate(BaseModel):
    tag_id: int
    restaurant_id: int
    

class RestaurantTag(RestaurantTagCreate):
    model_config = ConfigDict(from_attributes=True) #map attributes from ORM model to Pydantic model 
    
    
    


