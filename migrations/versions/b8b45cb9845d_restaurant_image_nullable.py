"""restaurant image nullable

Revision ID: b8b45cb9845d
Revises: f64df33c3518
Create Date: 2024-09-11 22:42:43.305124

"""

from typing import Sequence, Union


from alembic.op import alter_column
from sqlalchemy import String

# revision identifiers, used by Alembic.
revision: str = "b8b45cb9845d"
down_revision: Union[str, None] = "f64df33c3518"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    alter_column(
        "restaurants",
        "image",
        nullable=True,
        existing_type=String,
    )


def downgrade() -> None:
    alter_column(
        "restaurants",
        "image",
        nullable=False,
        existing_type=String,
    )
