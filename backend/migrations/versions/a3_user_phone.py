"""Add phone to users table

Revision ID: a3_user_phone
Revises: a2_cart_user
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa

revision = "a3_user_phone"
down_revision = "a2_cart_user"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("phone", sa.String(32), nullable=True))


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("phone")
