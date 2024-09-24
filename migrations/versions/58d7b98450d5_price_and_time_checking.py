"""price and time checking

Revision ID: 58d7b98450d5
Revises: 32efaca7c7d5
Create Date: 2024-09-24 16:17:45.697736

"""

from typing import Sequence, Union

from alembic.op import create_check_constraint, drop_constraint


# revision identifiers, used by Alembic.
revision: str = "58d7b98450d5"
down_revision: Union[str, None] = "32efaca7c7d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # price can't be negative
    create_check_constraint(
        "menus_price_check",
        "menus",
        "price >= 0",
    )

    # estimated prep time can't be negative
    create_check_constraint(
        "menus_estimated_prep_time_check",
        "menus",
        "estimated_prep_time > 0",
    )

    # extra price can't be negative
    create_check_constraint(
        "options_extra_price_check",
        "options",
        "extra_price >= 0",
    )


def downgrade() -> None:
    drop_constraint("menus_price_check", "menus")
    drop_constraint("menus_estimated_prep_time_check", "menus")
    drop_constraint("options_extra_price_check", "options")
