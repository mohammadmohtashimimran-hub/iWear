"""Store settings and low_stock_threshold

Revision ID: a1_store_low
Revises: 96904e6e8d8a
Create Date: Week 3 plan - vendor readiness

"""
from alembic import op
import sqlalchemy as sa

revision = "a1_store_low"
down_revision = "96904e6e8d8a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "store_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index(op.f("ix_store_settings_key"), "store_settings", ["key"], unique=True)

    with op.batch_alter_table("product_variants", schema=None) as batch_op:
        batch_op.add_column(sa.Column("low_stock_threshold", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("product_variants", schema=None) as batch_op:
        batch_op.drop_column("low_stock_threshold")
    op.drop_index(op.f("ix_store_settings_key"), table_name="store_settings")
    op.drop_table("store_settings")
