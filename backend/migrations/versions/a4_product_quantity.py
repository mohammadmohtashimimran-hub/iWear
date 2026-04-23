"""Add quantity to products table

Revision ID: a4_product_qty
Revises: a3_user_phone
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa

revision = "a4_product_qty"
down_revision = "a3_user_phone"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("quantity")
