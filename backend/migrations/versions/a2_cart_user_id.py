"""Add user_id to carts table

Revision ID: a2_cart_user
Revises: a1_store_low
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa

revision = "a2_cart_user"
down_revision = "a1_store_low"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("carts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_carts_user_id", "users", ["user_id"], ["id"], ondelete="SET NULL")
        batch_op.create_index("ix_carts_user_id", ["user_id"])


def downgrade():
    with op.batch_alter_table("carts", schema=None) as batch_op:
        batch_op.drop_index("ix_carts_user_id")
        batch_op.drop_constraint("fk_carts_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
