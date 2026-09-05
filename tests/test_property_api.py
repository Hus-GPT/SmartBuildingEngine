from uuid import uuid4

from sqlmodel import select

from smartbuilding.infrastructure.models import AuditEvent

CONFIRM = "CONFIRM_WRITE"


def create_property(client, confirmation=CONFIRM):
    return client.post(
        "/properties",
        json={
            "name": "Harbor House",
            "address_line_1": "1 Harbor Way",
            "city": "Boston",
            "country_code": "us",
            "actor": "aria",
            "confirmation": confirmation,
        },
    )


def create_unit(client, property_id, number="2A", confirmation=CONFIRM):
    return client.post(
        "/units",
        json={
            "property_id": property_id,
            "number": number,
            "actor": "aria",
            "confirmation": confirmation,
        },
    )


def create_tenant(client, unit_id, email="sam@example.test", confirmation=CONFIRM):
    return client.post(
        "/tenants",
        json={
            "unit_id": unit_id,
            "full_name": "Sam Tenant",
            "email": email,
            "actor": "aria",
            "confirmation": confirmation,
        },
    )


def test_property_unit_tenant_lifecycle_is_audited(client, session):
    property_ = create_property(client).json()
    assert property_["country_code"] == "US"
    unit = create_unit(client, property_["id"]).json()
    tenant = create_tenant(client, unit["id"]).json()

    assert client.get("/properties").json()[0]["id"] == property_["id"]
    assert client.get(f"/properties/{property_['id']}/units").json()[0]["id"] == unit["id"]
    assert client.get("/tenants", params={"query": "SAM@EXAMPLE"}).json() == [tenant]

    actions = {event.action for event in session.exec(select(AuditEvent)).all()}
    assert {"property.created", "unit.created", "tenant.created"} <= actions


def test_property_write_requires_confirmation(client):
    response = create_property(client, confirmation=None)
    assert response.status_code == 409


def test_unit_requires_existing_property(client):
    response = create_unit(client, str(uuid4()))
    assert response.status_code == 404


def test_tenant_requires_existing_unit(client):
    response = create_tenant(client, str(uuid4()))
    assert response.status_code == 404


def test_unit_number_must_be_unique_within_property(client):
    property_ = create_property(client).json()
    assert create_unit(client, property_["id"]).status_code == 201
    duplicate = create_unit(client, property_["id"])
    assert duplicate.status_code == 422


def test_tenant_email_must_be_unique(client):
    property_ = create_property(client).json()
    unit = create_unit(client, property_["id"]).json()
    assert create_tenant(client, unit["id"]).status_code == 201
    duplicate = create_tenant(client, unit["id"], email="SAM@example.test")
    assert duplicate.status_code == 422


def test_invalid_required_fields_are_rejected(client):
    response = client.post(
        "/properties",
        json={
            "name": "",
            "address_line_1": "",
            "city": "",
            "country_code": "USA",
            "confirmation": CONFIRM,
        },
    )
    assert response.status_code == 422
