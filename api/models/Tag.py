from api.models import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from api.models.restaurant import Restaurant


class Tag(Base): 
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    
class RestaurantTag(Base): 
    __tablename__ = "restaurant_tags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"))
    tag = relationship(Tag, backref="tags")
    
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    restaurant = relationship(Restaurant, backref="restaurant_tags")
    
