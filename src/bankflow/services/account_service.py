"""Authorized account lookup and persisted balance inquiry."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from bankflow.models import Account, AccountStatus, AuditEvent, TransactionStatus, TransactionType
from bankflow.repositories import AccountRepository, CardRepository, TransactionRepository
from bankflow.schemas.account import AccountBalance
from bankflow.schemas.authentication import AuthenticationSession


class BankingServiceError(RuntimeError):
    """Base exception for stable transaction-service failures."""


class AccountAuthorizationError(BankingServiceError):
    """The authenticated subjects do not form one customer/account/card graph."""


class AccountUnavailableError(BankingServiceError):
    """The account status does not allow a new financial operation."""


class AccountService:
    """Resolve the authenticated account inside a caller-owned unit of work."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._accounts = AccountRepository(session)
        self._cards = CardRepository(session)
        self._transactions = TransactionRepository(session)

    def require_authorized_account(
        self,
        authentication: AuthenticationSession,
        *,
        for_update: bool,
        require_active: bool = True,
    ) -> Account:
        account = self._accounts.require_by_id(authentication.account_id, for_update=for_update)
        card = self._cards.require_by_id(authentication.card_id)
        if account.customer_id != authentication.customer_id or card.account_id != account.id:
            raise AccountAuthorizationError(
                "The authentication session is not authorized for this account."
            )
        if require_active and account.status is not AccountStatus.ACTIVE:
            raise AccountUnavailableError(
                f"The account is {account.status.value} and cannot accept this operation."
            )
        return account

    def inquire_balance(self, authentication: AuthenticationSession) -> AccountBalance:
        """Persist an exact balance snapshot before returning it."""
        account = self.require_authorized_account(
            authentication, for_update=True, require_active=True
        )
        transaction = self._transactions.create(
            transaction_id=uuid4(),
            account_id=account.id,
            card_id=authentication.card_id,
            transaction_type=TransactionType.BALANCE_INQUIRY,
            status=TransactionStatus.COMPLETED,
            amount=Decimal("0.00"),
            balance_before=account.balance,
            balance_after=account.balance,
        )
        self._session.add(
            AuditEvent(
                event_type="balance.viewed",
                outcome=TransactionStatus.COMPLETED,
                customer_id=authentication.customer_id,
                account_id=account.id,
                card_id=authentication.card_id,
                transaction_id=transaction.id,
                details={"currency": account.currency},
            )
        )
        self._session.flush()
        return AccountBalance(
            account_id=account.id,
            transaction_id=transaction.id,
            balance=account.balance,
            currency=account.currency,
            status=account.status,
            version=account.version,
        )
