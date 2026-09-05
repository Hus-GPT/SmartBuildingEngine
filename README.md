# SmartBuildingManager v2

A modular-monolith foundation for building financial operations. The first vertical slice is an immutable double-entry ledger: accounts, transfers, auditable writes, read-only account lookup, and a Property → Unit → Tenant slice.

## Architecture

- `domain`: financial invariants and the explicit `READ`/`WRITE` policy.
- `application`: validated commands and transaction-owning use cases.
- `infrastructure`: SQLModel persistence, PostgreSQL wiring, and Alembic migrations.
- `api`: FastAPI HTTP adapter.
- `mcp`: transport-neutral MCP adapter with a declared tool policy.

Properties own units; tenants are assigned to a unit. API and MCP reads support property/unit lookup and tenant search. Foreign references, per-property unit numbers, and tenant email uniqueness are validated before mutation.

All writes require the exact `confirmation` value `CONFIRM_WRITE`. Journal entries emit equal debit and credit postings in one database transaction. Each write creates an audit event.

## Run

```bash
docker compose up --build
curl http://localhost:8000/health
```

Apply migrations outside Docker with `alembic upgrade head`. Run quality checks with `pip install -e '.[dev]' && ruff check . && pytest -q`.
