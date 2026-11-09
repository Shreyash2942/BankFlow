"""Evaluate and persist BankFlow cross-layer data-quality rules."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from bankflow.config.settings import load_settings  # noqa: E402
from bankflow.database.connection import create_database_engine  # noqa: E402
from bankflow.quality import (  # noqa: E402
    build_quality_run,
    execute_quality_rules,
    persist_quality_run,
)
from scripts.load_gold_serving import TrinoClient  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=".env")
    parser.add_argument("--trino-url", default=os.getenv("TRINO_URL", "http://127.0.0.1:8096"))
    parser.add_argument("--trino-user", default=os.getenv("TRINO_USER", "trino"))
    parser.add_argument("--triggered-by", default="manual")
    parser.add_argument("--report-only", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = load_settings(args.env_file)
    engine = create_database_engine(settings)
    try:
        results = execute_quality_rules(TrinoClient(args.trino_url, args.trino_user))
        run = build_quality_run(results, triggered_by=args.triggered_by)
        with engine.begin() as connection:
            persist_quality_run(connection, run)
        print(
            json.dumps(
                {
                    "event": "bankflow_data_quality_complete",
                    "run_id": str(run.run_id),
                    "status": run.status,
                    "total_rules": len(run.results),
                    "passed_rules": run.passed_rules,
                    "failed_rules": run.failed_rules,
                    "error_rules": run.error_rules,
                    "total_violations": run.total_violations,
                },
                sort_keys=True,
            )
        )
        return 0 if args.report_only or run.status == "passed" else 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
