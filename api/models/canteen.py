from api.models import Base
from sqlalchemy.orm import Mapped, mapped_column


class Canteen(Base):
    __tablename__ = "canteens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    img: Mapped[str]
    latitude: Mapped[float]
    longitude: Mapped[float]
