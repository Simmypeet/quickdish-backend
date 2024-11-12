"""Add foreign key constraint to canteen_id in restaurants table

Revision ID: 5c4e328434e9
Revises: b710d492be6d
Create Date: 2024-11-12 14:50:16.383374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c4e328434e9'
down_revision: Union[str, None] = 'b710d492be6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('restaurants', sa.Column('canteen_id', sa.Integer, sa.ForeignKey('canteens.id'), nullable=False))


def downgrade() -> None:
    op.drop_column('restaurants', 'canteen_id')

