"""Insert the idempotent fictional BankFlow demo customer, account, and card."""

import argparse
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.database.connection import create_database_engine
from bankflow.database.session import create_session_factory, session_scope
from bankflow.demo import (
    DEMO_ACCOUNT_ID,
    DEMO_ACCOUNT_NUMBER,
    DEMO_CARD_ID,
    DEMO_CARD_TOKEN,
    DEMO_CUSTOMER_ID,
    DEMO_EMAIL,
    DEMO_PIN,
    DEMO_STARTING_BALANCE,
)
from bankflow.models import Account, AccountType, AuditEvent, Card, Customer
from bankflow.utils import hash_pin


class SeedConflictError(RuntimeError):
    """Existing fixed demo identifiers do not form the expected complete seed."""


@dataclass(frozen=True)
class SeedResult:
    created: bool
    customer_id: UUID = DEMO_CUSTOMER_ID
    account_id: UUID = DEMO_ACCOUNT_ID
    card_id: UUID = DEMO_CARD_ID


def seed_demo_data(session: Session) -> SeedResult:
    """Create the fixed demo graph once and reject partial/conflicting state."""
    customer = session.get(Customer, DEMO_CUSTOMER_ID)
    account = session.get(Account, DEMO_ACCOUNT_ID)
    card = session.get(Card, DEMO_CARD_ID)
    existing_count = sum(item is not None for item in (customer, account, card))
    if existing_count:
        if existing_count != 3:
            raise SeedConflictError("The demo seed is partial; no records were changed.")
        if (
            customer.email != DEMO_EMAIL
            or account.customer_id != customer.id
            or account.account_number != DEMO_ACCOUNT_NUMBER
            or card.account_id != account.id
            or card.card_token != DEMO_CARD_TOKEN
        ):
            raise SeedConflictError("The demo identifiers conflict with existing records.")
        return SeedResult(created=False)

    customer = Customer(id=DEMO_CUSTOMER_ID, full_name="BankFlow Demo Customer", email=DEMO_EMAIL)
    account = Account(
        id=DEMO_ACCOUNT_ID,
        customer=customer,
        account_number=DEMO_ACCOUNT_NUMBER,
        account_type=AccountType.CHECKING,
        balance=DEMO_STARTING_BALANCE,
        currency="USD",
    )
    card = Card(
        id=DEMO_CARD_ID,
        account=account,
        card_token=DEMO_CARD_TOKEN,
        last_four="1001",
        pin_hash=hash_pin(DEMO_PIN),
        expiry_month=12,
        expiry_year=2035,
    )
    session.add_all(
        [
            customer,
            account,
            card,
            AuditEvent(
                event_type="demo.seeded",
                outcome="completed",
                customer_id=DEMO_CUSTOMER_ID,
                account_id=DEMO_ACCOUNT_ID,
                card_id=DEMO_CARD_ID,
                details={"source": "scripts/seed_database.py", "fictional": True},
            ),
        ]
    )
    session.flush()
    return SeedResult(created=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    args = parser.parse_args()
    try:
        settings = load_settings(args.env_file)
    except ConfigurationError as exc:
        print(str(exc))
        return 2
    engine = create_database_engine(settings)
    try:
        factory = create_session_factory(engine)
        with session_scope(factory) as session:
            result = seed_demo_data(session)
        print(
            "Demo customer, account, and card created."
            if result.created
            else "Demo data already present."
        )
        return 0
    except SeedConflictError as exc:
        print(str(exc))
        return 1
    except SQLAlchemyError:
        print("Demo seed failed. Check the database migration, availability, and credentials.")
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
