"""Added Tag & Restaurant tag table

Revision ID: ec50fc7cdbe7
Revises: 7ada867aef4c
Create Date: 2024-10-03 23:38:54.350892

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec50fc7cdbe7'
down_revision: Union[str, None] = '7ada867aef4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('restaurant_tags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('restaurant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['restaurant_id'], ['restaurants.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('restaurant_tags')
    op.drop_table('tags')
    # ### end Alembic commands ###
