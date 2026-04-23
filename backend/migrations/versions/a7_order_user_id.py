"""Add user_id to orders table to link orders to authenticated users."""
from alembic import op
import sqlalchemy as sa

revision = "a7_order_uid"
down_revision = "a6_geo"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_orders_user_id", "users", ["user_id"], ["id"], ondelete="SET NULL")
        batch_op.create_index("ix_orders_user_id", ["user_id"])


def downgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_index("ix_orders_user_id")
        batch_op.drop_constraint("fk_orders_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")
