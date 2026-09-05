"""add property, unit, and tenant aggregates

Revision ID: 0002_property_unit_tenant
Revises: 0001_initial_ledger
Create Date: 2026-09-05
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_property_unit_tenant"
down_revision = "0001_initial_ledger"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "properties",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("address_line_1", sa.String(200), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country_code", sa.String(2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "units",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("property_id", sa.Uuid(), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("length(number) > 0", name="ck_unit_number_not_empty"),
        sa.UniqueConstraint("property_id", "number", name="uq_units_property_number"),
    )
    op.create_index("ix_units_property_id", "units", ["property_id"])
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("unit_id", sa.Uuid(), sa.ForeignKey("units.id"), nullable=False),
        sa.Column("full_name", sa.String(160), nullable=False),
        sa.Column("email", sa.String(254), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_tenants_unit_id", "tenants", ["unit_id"])
    op.create_index("ix_tenants_email", "tenants", ["email"])


def downgrade() -> None:
    op.drop_table("tenants")
    op.drop_table("units")
    op.drop_table("properties")
