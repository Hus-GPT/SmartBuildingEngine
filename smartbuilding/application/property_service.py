from uuid import UUID

from sqlmodel import Session

from smartbuilding.application.commands import (
    CreatePropertyCommand,
    CreateTenantCommand,
    CreateUnitCommand,
)
from smartbuilding.domain.errors import DomainError
from smartbuilding.domain.policy import Operation, require_write_confirmation
from smartbuilding.infrastructure.models import Property, Tenant, Unit
from smartbuilding.infrastructure.repositories import PropertyRepository


class PropertyService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = PropertyRepository(session)

    def create_property(self, command: CreatePropertyCommand) -> Property:
        require_write_confirmation(Operation.WRITE, command.confirmation)
        property_ = Property(
            name=command.name,
            address_line_1=command.address_line_1,
            city=command.city,
            country_code=command.country_code.upper(),
        )
        self.repo.add_property(property_)
        self.repo.add_audit(
            "property.created", command.actor, "property", property_.id, name=property_.name
        )
        self.session.commit()
        self.session.refresh(property_)
        return property_

    def create_unit(self, command: CreateUnitCommand) -> Unit:
        require_write_confirmation(Operation.WRITE, command.confirmation)
        self.repo.property(command.property_id)
        if self.repo.unit_with_number(command.property_id, command.number):
            raise DomainError("unit number already exists for this property")
        unit = Unit(property_id=command.property_id, number=command.number)
        self.repo.add_unit(unit)
        self.repo.add_audit(
            "unit.created",
            command.actor,
            "unit",
            unit.id,
            property_id=unit.property_id,
            number=unit.number,
        )
        self.session.commit()
        self.session.refresh(unit)
        return unit

    def create_tenant(self, command: CreateTenantCommand) -> Tenant:
        require_write_confirmation(Operation.WRITE, command.confirmation)
        self.repo.unit(command.unit_id)
        email = command.email.strip().lower()
        if self.repo.tenant_with_email(email):
            raise DomainError("tenant email is already in use")
        tenant = Tenant(unit_id=command.unit_id, full_name=command.full_name, email=email)
        self.repo.add_tenant(tenant)
        self.repo.add_audit(
            "tenant.created",
            command.actor,
            "tenant",
            tenant.id,
            unit_id=tenant.unit_id,
            email=tenant.email,
        )
        self.session.commit()
        self.session.refresh(tenant)
        return tenant

    def properties(self) -> list[Property]:
        return self.repo.list_properties()

    def units(self, property_id: UUID) -> list[Unit]:
        self.repo.property(property_id)
        return self.repo.list_units(property_id)

    def tenants(self, query: str | None = None) -> list[Tenant]:
        return self.repo.search_tenants(query)
