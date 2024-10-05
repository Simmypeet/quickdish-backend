"""add favorite

Revision ID: 4d198063ad02
Revises: 7ada867aef4c
Create Date: 2024-10-05 18:30:36.981213

"""

from typing import Sequence, Union

from alembic.op import (
    create_table,
    drop_table,
    create_primary_key,
)
from sqlalchemy import Column, ForeignKey, Integer


# revision identifiers, used by Alembic.
revision: str = "76ea71cdc5d3"
down_revision: Union[str, None] = "7ada867aef4c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    create_table(
        "favorite_restaurants",
        Column(
            "restaurant_id",
            Integer,
            ForeignKey("restaurants.id"),
            nullable=False,
        ),
        Column(
            "customer_id", Integer, ForeignKey("customers.id"), nullable=False
        ),
    )

    create_primary_key(
        "favorite_restaurants_pk",
        "favorite_restaurants",
        ["restaurant_id", "customer_id"],
    )


def downgrade() -> None:
    drop_table("favorite_restaurants")
