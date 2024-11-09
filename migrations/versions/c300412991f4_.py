"""empty message

Revision ID: c300412991f4
Revises: 76ea71cdc5d3, d9237eb37a98
Create Date: 2024-10-16 16:14:29.258369

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c300412991f4"
down_revision: Union[tuple[str, ...], None] = ("76ea71cdc5d3", "d9237eb37a98")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "restaurants", "image", existing_type=sa.VARCHAR(), nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "restaurants", "image", existing_type=sa.VARCHAR(), nullable=False
    )
