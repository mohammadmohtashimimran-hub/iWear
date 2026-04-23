"""Add countries and cities tables for checkout location selection."""
from alembic import op
import sqlalchemy as sa

revision = "a6_geo"
down_revision = "a5_ci_addons"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "countries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
    )
    op.create_table(
        "cities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("country_id", sa.Integer(), sa.ForeignKey("countries.id", ondelete="CASCADE"), nullable=False),
    )
    op.create_index("ix_cities_country_id", "cities", ["country_id"])


def downgrade():
    op.drop_index("ix_cities_country_id")
    op.drop_table("cities")
    op.drop_table("countries")
