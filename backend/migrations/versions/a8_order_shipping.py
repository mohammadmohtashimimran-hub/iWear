"""Add shipping_address, shipping_country_id, shipping_city_id to orders."""
from alembic import op
import sqlalchemy as sa

revision = "a8_ship"
down_revision = "a7_order_uid"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.add_column(sa.Column("shipping_address", sa.String(512), nullable=True))
        batch_op.add_column(sa.Column("shipping_country_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("shipping_city_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_orders_ship_country", "countries", ["shipping_country_id"], ["id"], ondelete="SET NULL")
        batch_op.create_foreign_key("fk_orders_ship_city", "cities", ["shipping_city_id"], ["id"], ondelete="SET NULL")


def downgrade():
    with op.batch_alter_table("orders", schema=None) as batch_op:
        batch_op.drop_constraint("fk_orders_ship_city", type_="foreignkey")
        batch_op.drop_constraint("fk_orders_ship_country", type_="foreignkey")
        batch_op.drop_column("shipping_city_id")
        batch_op.drop_column("shipping_country_id")
        batch_op.drop_column("shipping_address")
