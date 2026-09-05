class DomainError(Exception):
    """A business rule was violated."""


class NotFoundError(DomainError):
    """An aggregate could not be found."""


class ConfirmationRequiredError(DomainError):
    """A state-changing command lacks an explicit confirmation token."""
