"""Add cart_item_addons table for per-item addon tracking."""
from alembic import op
import sqlalchemy as sa

revision = "a5_ci_addons"
down_revision = "a4_product_qty"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cart_item_addons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_item_id", sa.Integer(), sa.ForeignKey("cart_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("addon_option_id", sa.Integer(), sa.ForeignKey("addon_options.id", ondelete="CASCADE"), nullable=False),
        sa.Column("image_url", sa.String(512), nullable=True),
    )
    op.create_index("ix_cart_item_addons_cart_item_id", "cart_item_addons", ["cart_item_id"])


def downgrade():
    op.drop_index("ix_cart_item_addons_cart_item_id")
    op.drop_table("cart_item_addons")
