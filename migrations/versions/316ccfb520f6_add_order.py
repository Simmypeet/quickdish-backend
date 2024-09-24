"""add order

Revision ID: 316ccfb520f6
Revises: 58d7b98450d5
Create Date: 2024-09-24 16:37:35.241202

"""

from typing import Sequence, Union

from alembic.op import (
    create_table,
    create_check_constraint,
    drop_table,
    create_primary_key,
    get_bind,
)
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects import postgresql  # type: ignore


# revision identifiers, used by Alembic.
revision: str = "316ccfb520f6"
down_revision: Union[str, None] = "58d7b98450d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

order_status = postgresql.ENUM(
    "ORDERED",
    "PREPARING",
    "SETTLED",
    "READY",
    "CANCELLED",
    name="order_status",
)

order_cancelled_by = postgresql.ENUM(
    "CUSTOMER", "MERCHANT", name="order_cancelled_by"
)


def upgrade() -> None:
    create_table(
        "orders",
        Column(
            "id", Integer, primary_key=True, autoincrement=True, nullable=False
        ),
        Column(
            "restaurant_id",
            Integer,
            ForeignKey("restaurants.id"),
            nullable=False,
        ),
        Column(
            "customer_id", Integer, ForeignKey("customers.id"), nullable=False
        ),
        Column("status", order_status, nullable=False),  # type: ignore
        Column(
            "price_paid",
            Numeric(precision=10, scale=2, asdecimal=True),
            nullable=False,
        ),
        Column("ordered_at", BigInteger, nullable=False),
    )

    create_table(
        "order_items",
        Column(
            "id", Integer, primary_key=True, autoincrement=True, nullable=False
        ),
        Column("order_id", Integer, ForeignKey("orders.id"), nullable=False),
        Column("menu_id", Integer, ForeignKey("menus.id"), nullable=False),
        Column("quantity", Integer, nullable=False),
        Column("extra_requests", String, nullable=True),
    )

    create_table(
        "order_options",
        Column(
            "order_item_id",
            Integer,
            ForeignKey("order_items.id"),
            nullable=False,
        ),
        Column("option_id", Integer, ForeignKey("options.id"), nullable=False),
    )

    create_primary_key(
        "order_options_pk", "order_options", ["order_item_id", "option_id"]
    )

    # price paid can't be negative
    create_check_constraint(
        "orders_price_paid_check",
        "orders",
        "price_paid >= 0",
    )

    # quantity must be greater than 0
    create_check_constraint(
        "order_items_quantity_check",
        "order_items",
        "quantity > 0",
    )

    create_table(
        "preparing_orders",
        Column(
            "order_id",
            Integer,
            ForeignKey("orders.id"),
            primary_key=True,
        ),
        Column("prepared_at", BigInteger, nullable=False),
    )

    create_table(
        "settled_orders",
        Column(
            "order_id",
            Integer,
            ForeignKey("orders.id"),
            primary_key=True,
        ),
        Column("settled_at", BigInteger, nullable=False),
    )

    create_table(
        "ready_orders",
        Column(
            "order_id",
            Integer,
            ForeignKey("orders.id"),
            primary_key=True,
        ),
        Column("ready_at", BigInteger, nullable=False),
    )

    create_table(
        "cancelled_orders",
        Column(
            "order_id",
            Integer,
            ForeignKey("orders.id"),
            primary_key=True,
        ),
        Column("cancelled_time", BigInteger, nullable=False),
        Column(
            "cancelled_by", order_cancelled_by, nullable=False
        ),  # type:ignore
        Column("reason", String, nullable=True),
    )


def downgrade() -> None:
    drop_table("order_options")
    drop_table("order_items")
    drop_table("cancelled_orders")
    drop_table("ready_orders")
    drop_table("settled_orders")
    drop_table("preparing_orders")
    drop_table("orders")

    order_status.drop(get_bind())  # type: ignore
    order_cancelled_by.drop(get_bind())  # type:ignore
