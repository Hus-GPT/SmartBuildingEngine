"""initial financial ledger

Revision ID: 0001_initial_ledger
Revises:
Create Date: 2026-09-05
"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial_ledger"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("building_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_accounts_building_id", "accounts", ["building_id"])
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("memo", sa.String(500), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(120), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "postings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "journal_entry_id", sa.Uuid(), sa.ForeignKey("journal_entries.id"), nullable=False
        ),
        sa.Column("account_id", sa.Uuid(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("side", sa.String(6), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.CheckConstraint("amount > 0", name="ck_posting_positive_amount"),
    )
    op.create_index("ix_postings_journal_entry_id", "postings", ["journal_entry_id"])
    op.create_index("ix_postings_account_id", "postings", ["account_id"])
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("actor", sa.String(120), nullable=False),
        sa.Column("aggregate_type", sa.String(100), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("details", sa.String(4000), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audit_events_aggregate_id", "audit_events", ["aggregate_id"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("postings")
    op.drop_table("journal_entries")
    op.drop_table("accounts")
