"""create customization

Revision ID: 32efaca7c7d5
Revises: e4eac57c5afc
Create Date: 2024-09-18 01:41:51.113492

"""

from typing import Sequence, Union

from alembic.op import create_table, drop_table
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String


# revision identifiers, used by Alembic.
revision: str = "32efaca7c7d5"
down_revision: Union[str, None] = "e4eac57c5afc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    create_table(
        "customizations",
        Column(
            "id", Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        Column("menu_id", Integer, ForeignKey("menus.id"), nullable=False),
        Column("title", String, nullable=False),
        Column("description", String, nullable=True),
        Column("unique", Boolean, nullable=False),
        Column("required", Boolean, nullable=False),
    )

    create_table(
        "options",
        Column(
            "id", Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        Column(
            "customization_id",
            Integer,
            ForeignKey("customizations.id"),
            nullable=False,
        ),
        Column("name", String, nullable=False),
        Column("description", String, nullable=True),
        Column(
            "extra_price",
            Numeric(precision=10, scale=2, asdecimal=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    drop_table("options")
    drop_table("customizations")
