"""add restaurant open/close status

Revision ID: 5a3419814f3a
Revises: c300412991f4
Create Date: 2024-10-18 19:02:57.734953

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5a3419814f3a"
down_revision: Union[str, None] = "c300412991f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "restaurants",
        sa.Column(
            "open", sa.Boolean(), nullable=False, server_default="false"
        ),
    )


def downgrade() -> None:
    op.drop_column("restaurants", "open")
