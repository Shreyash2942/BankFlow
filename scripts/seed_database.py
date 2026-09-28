"""Insert the idempotent fictional BankFlow demo customer, account, and card."""

import argparse
import base64
import hashlib
import secrets
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.database.connection import create_database_engine
from bankflow.database.session import create_session_factory, session_scope
from bankflow.models import Account, AccountType, AuditEvent, Card, Customer

DEMO_CUSTOMER_ID = UUID("11111111-1111-4111-8111-111111111111")
DEMO_ACCOUNT_ID = UUID("22222222-2222-4222-8222-222222222222")
DEMO_CARD_ID = UUID("33333333-3333-4333-8333-333333333333")
DEMO_EMAIL = "demo.customer@bankflow.example"
DEMO_ACCOUNT_NUMBER = "BF-DEMO-CHECKING-1001"
DEMO_CARD_TOKEN = "bankflow-demo-card-1001"
DEMO_STARTING_BALANCE = Decimal("500.00")
_DEMO_PIN = "2468"  # Fictional credential already published in the project README.


class SeedConflictError(RuntimeError):
    """Existing fixed demo identifiers do not form the expected complete seed."""


@dataclass(frozen=True)
class SeedResult:
    created: bool
    customer_id: UUID = DEMO_CUSTOMER_ID
    account_id: UUID = DEMO_ACCOUNT_ID
    card_id: UUID = DEMO_CARD_ID


def _hash_demo_pin(pin: str) -> str:
    """Create a salted scrypt hash; Day 5 authentication will own verification."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(pin.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=32)
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii").rstrip("=")
    encoded_digest = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"scrypt$16384$8$1${encoded_salt}${encoded_digest}"


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
        pin_hash=_hash_demo_pin(_DEMO_PIN),
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
