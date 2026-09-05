from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def amount(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def require_positive(value: Decimal) -> Decimal:
    value = amount(value)
    if value <= 0:
        from smartbuilding.domain.errors import DomainError

        raise DomainError("amount must be positive")
    return value
