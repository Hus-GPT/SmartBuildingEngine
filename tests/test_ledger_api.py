from uuid import uuid4

from sqlmodel import select

from smartbuilding.infrastructure.models import AuditEvent, Posting

CONFIRM = "CONFIRM_WRITE"


def create_account(client, building_id, name, confirmation=CONFIRM):
    return client.post(
        "/accounts",
        json={
            "building_id": str(building_id),
            "name": name,
            "currency": "USD",
            "actor": "aria",
            "confirmation": confirmation,
        },
    )


def test_writes_require_explicit_confirmation(client):
    response = create_account(client, uuid4(), "Operating", confirmation=None)
    assert response.status_code == 409
    assert "confirmation" in response.json()["detail"]


def test_transfer_is_balanced_and_audited(client, session):
    building_id = uuid4()
    debit = create_account(client, building_id, "Cash").json()
    credit = create_account(client, building_id, "Utilities").json()
    response = client.post(
        "/ledger/transfers",
        json={
            "debit_account_id": debit["id"],
            "credit_account_id": credit["id"],
            "amount": "49.95",
            "memo": "September utility bill",
            "actor": "aria",
            "confirmation": CONFIRM,
        },
    )
    assert response.status_code == 201
    postings = session.exec(select(Posting)).all()
    assert len(postings) == 2
    assert sum(p.amount for p in postings if p.side == "DEBIT") == sum(
        p.amount for p in postings if p.side == "CREDIT"
    )
    audits = session.exec(select(AuditEvent)).all()
    assert {audit.action for audit in audits} == {"account.created", "ledger.transferred"}


def test_transfer_rejects_different_currencies(client):
    building_id = uuid4()
    debit = create_account(client, building_id, "Cash").json()
    credit = client.post(
        "/accounts",
        json={
            "building_id": str(building_id),
            "name": "Euro",
            "currency": "EUR",
            "confirmation": CONFIRM,
        },
    ).json()
    response = client.post(
        "/ledger/transfers",
        json={
            "debit_account_id": debit["id"],
            "credit_account_id": credit["id"],
            "amount": "1.00",
            "memo": "invalid",
            "confirmation": CONFIRM,
        },
    )
    assert response.status_code == 422
