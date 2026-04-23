"""Add PKR price columns for dual-currency support.

Revision ID: b1_pkr_prices
Revises: a9_addons
"""
from alembic import op
import sqlalchemy as sa

revision = "b1_pkr_prices"
down_revision = "a9_addons"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("products") as batch_op:
        batch_op.add_column(sa.Column("price_pkr", sa.Numeric(12, 2), nullable=True))

    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.add_column(sa.Column("unit_price_pkr", sa.Numeric(12, 2), nullable=True))

    with op.batch_alter_table("addon_options") as batch_op:
        batch_op.add_column(sa.Column("price_pkr", sa.Numeric(12, 2), nullable=True))


def downgrade():
    with op.batch_alter_table("addon_options") as batch_op:
        batch_op.drop_column("price_pkr")

    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.drop_column("unit_price_pkr")

    with op.batch_alter_table("products") as batch_op:
        batch_op.drop_column("price_pkr")
