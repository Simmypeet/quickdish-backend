"""add restaurant

Revision ID: f64df33c3518
Revises: b19b4ab2a1cf
Create Date: 2024-09-11 00:34:02.965475

"""

from typing import Sequence, Union

from alembic.op import create_table, drop_table
from sqlalchemy import Column, ForeignKey, Integer, String

from api.types.point import PointType

# revision identifiers, used by Alembic.
revision: str = "f64df33c3518"
down_revision: Union[str, None] = "b19b4ab2a1cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    create_table(
        "restaurants",
        Column(
            "id", Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        Column("name", String, unique=True, nullable=False),
        Column("address", String, nullable=False),
        Column(
            "merchant_id",
            Integer,
            ForeignKey("merchants.id"),
        ),
        Column("image", String, nullable=False),
        Column("location", PointType, nullable=False),
    )


def downgrade() -> None:
    drop_table("restaurants")
