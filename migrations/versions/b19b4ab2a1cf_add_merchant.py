"""add merchant

Revision ID: b19b4ab2a1cf
Revises: 2a108b266e87
Create Date: 2024-09-10 23:27:57.966629

"""

from typing import Sequence, Union


from alembic.op import create_table, drop_table
from sqlalchemy import Column, Integer, String

# revision identifiers, used by Alembic.
revision: str = "b19b4ab2a1cf"
down_revision: Union[str, None] = "2a108b266e87"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    create_table(
        "merchants",
        Column(
            "id", Integer, primary_key=True, nullable=False, autoincrement=True
        ),
        Column("first_name", String, nullable=False),
        Column("last_name", String, nullable=False),
        Column("username", String, unique=True, nullable=False),
        Column("email", String, unique=True, nullable=False),
        Column("hashed_password", String, nullable=False),
        Column("salt", String, nullable=False),
    )


def downgrade() -> None:
    drop_table("merchants")
