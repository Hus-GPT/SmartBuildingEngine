"""Transport-neutral MCP tool adapter. Wire these tools into an MCP server of choice."""

from typing import Any
from uuid import UUID

from sqlmodel import Session

from smartbuilding.application.commands import (
    CreateAccountCommand,
    CreatePropertyCommand,
    CreateTenantCommand,
    CreateUnitCommand,
    TransferCommand,
)
from smartbuilding.application.ledger_service import LedgerService
from smartbuilding.application.property_service import PropertyService
from smartbuilding.domain.policy import Operation

TOOLS: dict[str, Operation] = {
    "list_accounts": Operation.READ,
    "create_account": Operation.WRITE,
    "transfer_funds": Operation.WRITE,
    "list_properties": Operation.READ,
    "create_property": Operation.WRITE,
    "list_units": Operation.READ,
    "create_unit": Operation.WRITE,
    "search_tenants": Operation.READ,
    "create_tenant": Operation.WRITE,
}


def invoke_tool(name: str, arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    """Invoke a tool; write tools must include confirmation=CONFIRM_WRITE."""
    service = LedgerService(session)
    property_service = PropertyService(session)
    if name == "list_accounts":
        accounts = service.accounts(UUID(str(arguments["building_id"])))
        return {
            "accounts": [
                {"id": str(a.id), "name": a.name, "currency": a.currency} for a in accounts
            ]
        }
    if name == "create_account":
        account = service.create_account(CreateAccountCommand.model_validate(arguments))
        return {"id": str(account.id), "name": account.name}
    if name == "transfer_funds":
        entry = service.transfer(TransferCommand.model_validate(arguments))
        return {"id": str(entry.id), "memo": entry.memo}
    if name == "list_properties":
        return {
            "properties": [{"id": str(p.id), "name": p.name} for p in property_service.properties()]
        }
    if name == "create_property":
        property_ = property_service.create_property(
            CreatePropertyCommand.model_validate(arguments)
        )
        return {"id": str(property_.id), "name": property_.name}
    if name == "list_units":
        units = property_service.units(UUID(str(arguments["property_id"])))
        return {"units": [{"id": str(u.id), "number": u.number} for u in units]}
    if name == "create_unit":
        unit = property_service.create_unit(CreateUnitCommand.model_validate(arguments))
        return {"id": str(unit.id), "number": unit.number}
    if name == "search_tenants":
        tenants = property_service.tenants(arguments.get("query"))
        return {"tenants": [{"id": str(t.id), "full_name": t.full_name} for t in tenants]}
    if name == "create_tenant":
        tenant = property_service.create_tenant(CreateTenantCommand.model_validate(arguments))
        return {"id": str(tenant.id), "full_name": tenant.full_name}
    raise ValueError(f"unknown MCP tool: {name}")
