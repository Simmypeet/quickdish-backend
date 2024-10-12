"""add refresh token table

Revision ID: eff27fb6e049
Revises: 461d261c81c8
Create Date: 2024-10-13 01:42:10.999455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eff27fb6e049'
down_revision: Union[str, None] = '461d261c81c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
