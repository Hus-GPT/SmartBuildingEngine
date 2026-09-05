import json
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session, select

from smartbuilding.domain.errors import NotFoundError
from smartbuilding.infrastructure.models import (
    Account,
    AuditEvent,
    JournalEntry,
    Posting,
    Property,
    Tenant,
    Unit,
)


class LedgerRepository:
    def __init__(self, session: Session):
        self.session = session

    def account(self, account_id: UUID) -> Account:
        account = self.session.get(Account, account_id)
        if not account:
            raise NotFoundError(f"account {account_id} was not found")
        return account

    def list_accounts(self, building_id: UUID) -> list[Account]:
        return list(self.session.exec(select(Account).where(Account.building_id == building_id)))

    def add_account(self, account: Account) -> Account:
        self.session.add(account)
        return account

    def add_journal_entry(self, entry: JournalEntry, postings: list[Posting]) -> None:
        self.session.add(entry)
        self.session.add_all(postings)

    def add_audit(
        self, action: str, actor: str, aggregate_type: str, aggregate_id: UUID, **details: object
    ) -> None:
        self.session.add(
            AuditEvent(
                action=action,
                actor=actor,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                details=json.dumps(details, default=str),
            )
        )

    def balance(self, account_id: UUID) -> Decimal:
        postings = self.session.exec(select(Posting).where(Posting.account_id == account_id)).all()
        return sum((p.amount if p.side == "DEBIT" else -p.amount for p in postings), Decimal("0"))


class PropertyRepository:
    def __init__(self, session: Session):
        self.session = session

    def property(self, property_id: UUID) -> Property:
        property_ = self.session.get(Property, property_id)
        if not property_:
            raise NotFoundError(f"property {property_id} was not found")
        return property_

    def unit(self, unit_id: UUID) -> Unit:
        unit = self.session.get(Unit, unit_id)
        if not unit:
            raise NotFoundError(f"unit {unit_id} was not found")
        return unit

    def add_property(self, property_: Property) -> None:
        self.session.add(property_)

    def add_unit(self, unit: Unit) -> None:
        self.session.add(unit)

    def add_tenant(self, tenant: Tenant) -> None:
        self.session.add(tenant)

    def unit_with_number(self, property_id: UUID, number: str) -> Unit | None:
        return self.session.exec(
            select(Unit).where(Unit.property_id == property_id, Unit.number == number)
        ).first()

    def tenant_with_email(self, email: str) -> Tenant | None:
        return self.session.exec(select(Tenant).where(Tenant.email == email)).first()

    def add_audit(
        self, action: str, actor: str, aggregate_type: str, aggregate_id: UUID, **details: object
    ) -> None:
        self.session.add(
            AuditEvent(
                action=action,
                actor=actor,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                details=json.dumps(details, default=str),
            )
        )

    def list_properties(self) -> list[Property]:
        return list(self.session.exec(select(Property).order_by(Property.name)))

    def list_units(self, property_id: UUID) -> list[Unit]:
        return list(
            self.session.exec(
                select(Unit).where(Unit.property_id == property_id).order_by(Unit.number)
            )
        )

    def search_tenants(self, query: str | None = None) -> list[Tenant]:
        statement = select(Tenant)
        if query:
            needle = f"%{query.strip()}%"
            statement = statement.where(Tenant.full_name.ilike(needle) | Tenant.email.ilike(needle))
        return list(self.session.exec(statement.order_by(Tenant.full_name)))
