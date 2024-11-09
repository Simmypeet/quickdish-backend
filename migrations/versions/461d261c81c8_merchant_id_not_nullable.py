"""merchant id not nullable

Revision ID: 461d261c81c8
Revises: ec50fc7cdbe7
Create Date: 2024-10-07 15:40:33.624754

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "461d261c81c8"
down_revision: Union[str, None] = "ec50fc7cdbe7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "restaurants",
        "merchant_id",
        existing_type=sa.INTEGER(),
        existing_nullable=True,
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "restaurants",
        "merchant_id",
        existing_type=sa.INTEGER(),
        existing_nullable=False,
        nullable=True,
    )
