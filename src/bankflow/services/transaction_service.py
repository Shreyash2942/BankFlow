"""Atomic withdrawal, deposit, and transaction-history workflows."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from bankflow.config.settings import Settings
from bankflow.models import (
    AccountStatus,
    AuditEvent,
    Transaction,
    TransactionStatus,
    TransactionType,
)
from bankflow.repositories import AccountRepository, TransactionRepository
from bankflow.schemas.authentication import AuthenticationSession
from bankflow.schemas.transaction import (
    DepositRequest,
    TransactionHistory,
    TransactionHistoryItem,
    TransactionHistoryQuery,
    TransactionResult,
    WithdrawalRequest,
)
from bankflow.services.account_service import AccountService, BankingServiceError

MAX_MONEY = Decimal("9999999999999999.99")
INSUFFICIENT_FUNDS = "insufficient_funds"


class BalanceLimitExceededError(BankingServiceError):
    """A deposit would exceed the database's exact-money range."""


class TransactionService:
    """Apply business rules without committing the caller's database session."""

    def __init__(self, session: Session, *, auto_close_zero_balance: bool = True) -> None:
        self._session = session
        self._accounts = AccountRepository(session)
        self._transactions = TransactionRepository(session)
        self._account_service = AccountService(session)
        self._auto_close_zero_balance = auto_close_zero_balance

    @classmethod
    def from_settings(cls, session: Session, settings: Settings) -> "TransactionService":
        return cls(session, auto_close_zero_balance=settings.auto_close_zero_balance)

    def _audit(
        self,
        *,
        authentication: AuthenticationSession,
        transaction: Transaction,
        event_type: str,
        outcome: TransactionStatus | str,
        details: dict[str, str],
    ) -> None:
        self._session.add(
            AuditEvent(
                event_type=event_type,
                outcome=outcome,
                customer_id=authentication.customer_id,
                account_id=authentication.account_id,
                card_id=authentication.card_id,
                transaction_id=transaction.id,
                details=details,
            )
        )

    @staticmethod
    def _result(transaction: Transaction, account_status: AccountStatus) -> TransactionResult:
        return TransactionResult(
            transaction_id=transaction.id,
            transaction_type=transaction.transaction_type,
            status=transaction.status,
            amount=transaction.amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
            account_status=account_status,
            decline_reason=transaction.decline_reason,
        )

    def withdraw(
        self, authentication: AuthenticationSession, request: WithdrawalRequest
    ) -> TransactionResult:
        account = self._account_service.require_authorized_account(
            authentication, for_update=True, require_active=True
        )
        balance_before = account.balance
        if request.amount > balance_before:
            transaction = self._transactions.create(
                transaction_id=uuid4(),
                account_id=account.id,
                card_id=authentication.card_id,
                transaction_type=TransactionType.WITHDRAWAL,
                status=TransactionStatus.DECLINED,
                amount=request.amount,
                balance_before=balance_before,
                balance_after=balance_before,
                decline_reason=INSUFFICIENT_FUNDS,
            )
            self._audit(
                authentication=authentication,
                transaction=transaction,
                event_type="withdrawal.declined",
                outcome=TransactionStatus.DECLINED,
                details={"reason": INSUFFICIENT_FUNDS},
            )
            self._session.flush()
            return self._result(transaction, account.status)

        balance_after = balance_before - request.amount
        if self._auto_close_zero_balance and balance_after == 0:
            account.status = AccountStatus.CLOSED
        self._accounts.update_balance(account.id, balance_after, expected_version=account.version)
        transaction = self._transactions.create(
            transaction_id=uuid4(),
            account_id=account.id,
            card_id=authentication.card_id,
            transaction_type=TransactionType.WITHDRAWAL,
            status=TransactionStatus.COMPLETED,
            amount=request.amount,
            balance_before=balance_before,
            balance_after=balance_after,
        )
        self._audit(
            authentication=authentication,
            transaction=transaction,
            event_type="withdrawal.completed",
            outcome=TransactionStatus.COMPLETED,
            details={"amount": str(request.amount), "currency": account.currency},
        )
        if account.status is AccountStatus.CLOSED:
            self._audit(
                authentication=authentication,
                transaction=transaction,
                event_type="account.closed",
                outcome="completed",
                details={"reason": "zero_balance_demo_rule"},
            )
        self._session.flush()
        return self._result(transaction, account.status)

    def deposit(
        self, authentication: AuthenticationSession, request: DepositRequest
    ) -> TransactionResult:
        account = self._account_service.require_authorized_account(
            authentication, for_update=True, require_active=True
        )
        balance_before = account.balance
        balance_after = balance_before + request.amount
        if balance_after > MAX_MONEY:
            raise BalanceLimitExceededError("The deposit would exceed the supported balance limit.")
        self._accounts.update_balance(account.id, balance_after, expected_version=account.version)
        transaction = self._transactions.create(
            transaction_id=uuid4(),
            account_id=account.id,
            card_id=authentication.card_id,
            transaction_type=TransactionType.DEPOSIT,
            status=TransactionStatus.COMPLETED,
            amount=request.amount,
            balance_before=balance_before,
            balance_after=balance_after,
        )
        self._audit(
            authentication=authentication,
            transaction=transaction,
            event_type="deposit.completed",
            outcome=TransactionStatus.COMPLETED,
            details={"amount": str(request.amount), "currency": account.currency},
        )
        self._session.flush()
        return self._result(transaction, account.status)

    def history(
        self,
        authentication: AuthenticationSession,
        query: TransactionHistoryQuery | None = None,
    ) -> TransactionHistory:
        query = query or TransactionHistoryQuery()
        account = self._account_service.require_authorized_account(
            authentication, for_update=False, require_active=False
        )
        transactions = self._transactions.list_for_account(
            account.id, limit=query.limit, offset=query.offset
        )
        return TransactionHistory(
            account_id=account.id,
            limit=query.limit,
            offset=query.offset,
            items=tuple(
                TransactionHistoryItem(
                    transaction_id=transaction.id,
                    transaction_type=transaction.transaction_type,
                    status=transaction.status,
                    amount=transaction.amount,
                    balance_before=transaction.balance_before,
                    balance_after=transaction.balance_after,
                    decline_reason=transaction.decline_reason,
                    created_at=transaction.created_at,
                )
                for transaction in transactions
            ),
        )
