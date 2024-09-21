"""create menu

Revision ID: e4eac57c5afc
Revises: b8b45cb9845d
Create Date: 2024-09-16 15:58:59.864785

"""

from typing import Sequence, Union

from alembic.op import create_table, drop_table
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String


# revision identifiers, used by Alembic.
revision: str = "e4eac57c5afc"
down_revision: Union[str, None] = "b8b45cb9845d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    create_table(
        "menus",
        Column(
            "id", Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        Column("restaurant_id", Integer, ForeignKey("restaurants.id")),
        Column("name", String, nullable=False),
        Column("description", String, nullable=False),
        Column(
            "price",
            Numeric(precision=10, scale=2, asdecimal=True),
            nullable=False,
        ),
        Column("image", String, nullable=True),
        Column("estimated_prep_time", Integer, nullable=True),
    )


def downgrade() -> None:
    drop_table("menus")
