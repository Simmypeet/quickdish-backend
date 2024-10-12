
from api.models import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from datetime import datetime


class RefreshToken(Base): 
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    token: Mapped[str]
    role: Mapped[str]
    expired_at: Mapped[datetime]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)