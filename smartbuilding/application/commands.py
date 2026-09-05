from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateAccountCommand(BaseModel):
    building_id: UUID
    name: str = Field(min_length=1, max_length=120)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    actor: str = Field(default="system", min_length=1, max_length=120)
    confirmation: str | None = None


class TransferCommand(BaseModel):
    debit_account_id: UUID
    credit_account_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    memo: str = Field(min_length=1, max_length=500)
    actor: str = Field(default="system", min_length=1, max_length=120)
    confirmation: str | None = None


class CreatePropertyCommand(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    address_line_1: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    country_code: str = Field(min_length=2, max_length=2)
    actor: str = Field(default="system", min_length=1, max_length=120)
    confirmation: str | None = None


class CreateUnitCommand(BaseModel):
    property_id: UUID
    number: str = Field(min_length=1, max_length=50)
    actor: str = Field(default="system", min_length=1, max_length=120)
    confirmation: str | None = None


class CreateTenantCommand(BaseModel):
    unit_id: UUID
    full_name: str = Field(min_length=1, max_length=160)
    email: str = Field(min_length=3, max_length=254)
    actor: str = Field(default="system", min_length=1, max_length=120)
    confirmation: str | None = None
