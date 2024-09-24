"""initial

Revision ID: 2a108b266e87
Revises: 
Create Date: 2024-09-09 16:47:26.722080

"""

from typing import Sequence, Union

from alembic.op import create_table, drop_table
from sqlalchemy import Column, Integer, String


# revision identifiers, used by Alembic.
revision: str = "2a108b266e87"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    create_table(
        "customers",
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
    drop_table("customers")
