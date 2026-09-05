from uuid import UUID

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlmodel import Session

from smartbuilding.api.schemas import (
    AccountResponse,
    HealthResponse,
    JournalEntryResponse,
    PropertyResponse,
    TenantResponse,
    UnitResponse,
)
from smartbuilding.application.commands import (
    CreateAccountCommand,
    CreatePropertyCommand,
    CreateTenantCommand,
    CreateUnitCommand,
    TransferCommand,
)
from smartbuilding.application.ledger_service import LedgerService
from smartbuilding.application.property_service import PropertyService
from smartbuilding.domain.errors import ConfirmationRequiredError, DomainError, NotFoundError
from smartbuilding.infrastructure.database import get_session

app = FastAPI(title="SmartBuildingManager", version="2.0.0")


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    status = (
        404
        if isinstance(exc, NotFoundError)
        else 409
        if isinstance(exc, ConfirmationRequiredError)
        else 422
    )
    return JSONResponse(status_code=status, content={"detail": str(exc)})


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="smartbuilding-manager")


@app.get("/buildings/{building_id}/accounts", response_model=list[AccountResponse])
def list_accounts(
    building_id: UUID, session: Session = Depends(get_session)
) -> list[AccountResponse]:
    return LedgerService(session).accounts(building_id)


@app.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(
    command: CreateAccountCommand, session: Session = Depends(get_session)
) -> AccountResponse:
    return LedgerService(session).create_account(command)


@app.post("/ledger/transfers", response_model=JournalEntryResponse, status_code=201)
def transfer(
    command: TransferCommand, session: Session = Depends(get_session)
) -> JournalEntryResponse:
    return LedgerService(session).transfer(command)


@app.get("/properties", response_model=list[PropertyResponse])
def list_properties(session: Session = Depends(get_session)) -> list[PropertyResponse]:
    return PropertyService(session).properties()


@app.post("/properties", response_model=PropertyResponse, status_code=201)
def create_property(
    command: CreatePropertyCommand, session: Session = Depends(get_session)
) -> PropertyResponse:
    return PropertyService(session).create_property(command)


@app.get("/properties/{property_id}/units", response_model=list[UnitResponse])
def list_units(property_id: UUID, session: Session = Depends(get_session)) -> list[UnitResponse]:
    return PropertyService(session).units(property_id)


@app.post("/units", response_model=UnitResponse, status_code=201)
def create_unit(
    command: CreateUnitCommand, session: Session = Depends(get_session)
) -> UnitResponse:
    return PropertyService(session).create_unit(command)


@app.get("/tenants", response_model=list[TenantResponse])
def search_tenants(
    query: str | None = None, session: Session = Depends(get_session)
) -> list[TenantResponse]:
    return PropertyService(session).tenants(query)


@app.post("/tenants", response_model=TenantResponse, status_code=201)
def create_tenant(
    command: CreateTenantCommand, session: Session = Depends(get_session)
) -> TenantResponse:
    return PropertyService(session).create_tenant(command)
