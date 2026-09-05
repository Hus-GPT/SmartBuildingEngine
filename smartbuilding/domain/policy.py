from enum import StrEnum


class Operation(StrEnum):
    READ = "READ"
    WRITE = "WRITE"


WRITE_CONFIRMATION = "CONFIRM_WRITE"


def require_write_confirmation(operation: Operation, confirmation: str | None) -> None:
    if operation is Operation.WRITE and confirmation != WRITE_CONFIRMATION:
        from smartbuilding.domain.errors import ConfirmationRequiredError

        raise ConfirmationRequiredError("write requires confirmation=CONFIRM_WRITE")
