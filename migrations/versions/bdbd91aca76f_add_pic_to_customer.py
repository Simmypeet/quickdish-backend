"""add pic to customer

Revision ID: bdbd91aca76f
Revises: 5c4e328434e9
Create Date: 2024-11-17 03:12:08.780358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bdbd91aca76f'
down_revision: Union[str, None] = '5c4e328434e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customers', sa.Column('profile_pic', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('userpage_pic', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customers', 'profile_pic')
    op.drop_column('customers', 'userpage_pic')

    # ### end Alembic commands ###
