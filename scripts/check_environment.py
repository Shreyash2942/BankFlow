"""Check Day 1 imports without opening network connections or loading secrets."""

import importlib
import sys
from importlib.metadata import version

DEPENDENCIES = {
    "streamlit": "streamlit",
    "pydantic": "pydantic",
    "pydantic-settings": "pydantic_settings",
    "SQLAlchemy": "sqlalchemy",
    "alembic": "alembic",
    "psycopg": "psycopg",
    "redis": "redis",
    "confluent-kafka": "confluent_kafka",
}


def main() -> int:
    """Return nonzero if the selected interpreter or an application import fails."""
    if sys.version_info[:2] != (3, 14):
        print("Use Python 3.14 for the verified Day 1 environment.", file=sys.stderr)
        return 1

    failed = False
    for distribution, module in {"bankflow-atm": "bankflow", **DEPENDENCIES}.items():
        try:
            importlib.import_module(module)
            print(f"OK {distribution} {version(distribution)}")
        except Exception as exc:
            print(f"FAIL {distribution}: {type(exc).__name__}", file=sys.stderr)
            failed = True
    print("This check validates imports only; service connectivity is a Day 2 check.")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
