from decimal import Decimal
from uuid import UUID

from sqlmodel import Session

from smartbuilding.application.commands import CreateAccountCommand, TransferCommand
from smartbuilding.domain.errors import DomainError
from smartbuilding.domain.money import require_positive
from smartbuilding.domain.policy import Operation, require_write_confirmation
from smartbuilding.infrastructure.models import Account, JournalEntry, Posting
from smartbuilding.infrastructure.repositories import LedgerRepository


class LedgerService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = LedgerRepository(session)

    def create_account(self, command: CreateAccountCommand) -> Account:
        require_write_confirmation(Operation.WRITE, command.confirmation)
        account = Account(
            building_id=command.building_id, name=command.name, currency=command.currency.upper()
        )
        self.repo.add_account(account)
        self.repo.add_audit(
            "account.created", command.actor, "account", account.id, name=account.name
        )
        self.session.commit()
        self.session.refresh(account)
        return account

    def transfer(self, command: TransferCommand) -> JournalEntry:
        require_write_confirmation(Operation.WRITE, command.confirmation)
        if command.debit_account_id == command.credit_account_id:
            raise DomainError("debit and credit accounts must differ")
        debit = self.repo.account(command.debit_account_id)
        credit = self.repo.account(command.credit_account_id)
        if debit.currency != credit.currency:
            raise DomainError("accounts must use the same currency")
        value = require_positive(command.amount)
        entry = JournalEntry(memo=command.memo, created_by=command.actor)
        postings = [
            Posting(
                journal_entry_id=entry.id,
                account_id=debit.id,
                side="DEBIT",
                amount=value,
                currency=debit.currency,
            ),
            Posting(
                journal_entry_id=entry.id,
                account_id=credit.id,
                side="CREDIT",
                amount=value,
                currency=credit.currency,
            ),
        ]
        self._assert_balanced(postings)
        self.repo.add_journal_entry(entry, postings)
        self.repo.add_audit(
            "ledger.transferred",
            command.actor,
            "journal_entry",
            entry.id,
            debit_account_id=debit.id,
            credit_account_id=credit.id,
            amount=str(value),
        )
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def accounts(self, building_id: UUID) -> list[Account]:
        return self.repo.list_accounts(building_id)

    @staticmethod
    def _assert_balanced(postings: list[Posting]) -> None:
        debits = sum((p.amount for p in postings if p.side == "DEBIT"), Decimal("0"))
        credits = sum((p.amount for p in postings if p.side == "CREDIT"), Decimal("0"))
        if debits != credits or not postings:
            raise DomainError("journal entries must balance")
