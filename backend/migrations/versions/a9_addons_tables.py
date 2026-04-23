"""Create addons and addon_options tables (catalog add-ons)."""

from alembic import op
import sqlalchemy as sa

revision = "a9_addons"
down_revision = "a8_ship"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "addons",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=True),
        sa.Column("requires_image", sa.Boolean(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["product_categories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "addon_options",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("addon_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["addon_id"], ["addons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("addon_options")
    op.drop_table("addons")
