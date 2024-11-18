"""empty message

Revision ID: 173998d0ded4
Revises: 5a3419814f3a, bdbd91aca76f
Create Date: 2024-11-18 18:14:20.556135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '173998d0ded4'
down_revision: Union[str, None] = ('5a3419814f3a', 'bdbd91aca76f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
