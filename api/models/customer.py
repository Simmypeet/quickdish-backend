from api.models import Base

from sqlalchemy.orm import Mapped, mapped_column


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    salt: Mapped[str]
