from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, Numeric, String, UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Account(SQLModel, table=True):
    __tablename__ = "accounts"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    building_id: UUID = Field(index=True)
    name: str = Field(sa_column=Column(String(120), nullable=False))
    currency: str = Field(default="USD", sa_column=Column(String(3), nullable=False))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entries"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    memo: str = Field(sa_column=Column(String(500), nullable=False))
    occurred_at: datetime = Field(default_factory=utc_now, nullable=False)
    created_by: str = Field(sa_column=Column(String(120), nullable=False))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Posting(SQLModel, table=True):
    __tablename__ = "postings"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_posting_positive_amount"),)
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    journal_entry_id: UUID = Field(foreign_key="journal_entries.id", index=True)
    account_id: UUID = Field(foreign_key="accounts.id", index=True)
    side: str = Field(sa_column=Column(String(6), nullable=False))
    amount: Decimal = Field(sa_column=Column(Numeric(18, 2), nullable=False))
    currency: str = Field(sa_column=Column(String(3), nullable=False))


class AuditEvent(SQLModel, table=True):
    __tablename__ = "audit_events"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    action: str = Field(sa_column=Column(String(100), nullable=False))
    actor: str = Field(sa_column=Column(String(120), nullable=False))
    aggregate_type: str = Field(sa_column=Column(String(100), nullable=False))
    aggregate_id: UUID = Field(index=True)
    details: str = Field(default="{}", sa_column=Column(String(4000), nullable=False))
    occurred_at: datetime = Field(default_factory=utc_now, nullable=False)


class Property(SQLModel, table=True):
    __tablename__ = "properties"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(sa_column=Column(String(160), nullable=False))
    address_line_1: str = Field(sa_column=Column(String(200), nullable=False))
    city: str = Field(sa_column=Column(String(100), nullable=False))
    country_code: str = Field(sa_column=Column(String(2), nullable=False))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Unit(SQLModel, table=True):
    __tablename__ = "units"
    __table_args__ = (
        CheckConstraint("length(number) > 0", name="ck_unit_number_not_empty"),
        UniqueConstraint("property_id", "number", name="uq_units_property_number"),
    )
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    property_id: UUID = Field(foreign_key="properties.id", index=True)
    number: str = Field(sa_column=Column(String(50), nullable=False))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)


class Tenant(SQLModel, table=True):
    __tablename__ = "tenants"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    unit_id: UUID = Field(foreign_key="units.id", index=True)
    full_name: str = Field(sa_column=Column(String(160), nullable=False))
    email: str = Field(index=True, sa_column=Column(String(254), nullable=False, unique=True))
    created_at: datetime = Field(default_factory=utc_now, nullable=False)
