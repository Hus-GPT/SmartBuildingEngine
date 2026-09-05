from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: UUID
    building_id: UUID
    name: str
    currency: str
    created_at: datetime


class JournalEntryResponse(BaseModel):
    id: UUID
    memo: str
    occurred_at: datetime
    created_by: str


class HealthResponse(BaseModel):
    status: str
    service: str


class PropertyResponse(BaseModel):
    id: UUID
    name: str
    address_line_1: str
    city: str
    country_code: str
    created_at: datetime


class UnitResponse(BaseModel):
    id: UUID
    property_id: UUID
    number: str
    created_at: datetime


class TenantResponse(BaseModel):
    id: UUID
    unit_id: UUID
    full_name: str
    email: str
    created_at: datetime
