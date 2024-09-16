from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from api.models import Base


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(
        Numeric(precision=10, scale=2, asdecimal=True), nullable=False
    )
    image = Column(String, nullable=True)
    estimated_prep_time = Column(Integer, nullable=True)
