"""Generate deterministic fictional BankFlow events and optionally publish them to Kafka."""

import argparse
import json
from pathlib import Path

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.messaging import EventPublicationError, KafkaEventProducer
from bankflow.synthetic import (
    SyntheticEventGenerator,
    SyntheticGeneratorConfig,
    publish_generated_events,
    validate_generated_events,
)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def nonnegative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must not be negative")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=positive_int, default=1_000)
    parser.add_argument(
        "--rate",
        type=nonnegative_float,
        default=100.0,
        help="Maximum events per second; use 0 for no pacing.",
    )
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--customers", type=positive_int, default=100)
    parser.add_argument("--atms", type=positive_int, default=10)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and validate events without connecting to Kafka.",
    )
    return parser


def _print_report(*, mode: str, report) -> None:
    summary = {
        "mode": mode,
        "event_count": report.event_count,
        "configured_rate": report.configured_rate,
        "achieved_rate": round(report.achieved_rate, 2),
        "event_types": report.event_type_counts,
    }
    print(json.dumps(summary, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    generator = SyntheticEventGenerator(
        SyntheticGeneratorConfig(
            customer_count=args.customers,
            atm_count=args.atms,
            seed=args.seed,
        )
    )
    events = generator.iter_events(args.count)
    if args.dry_run:
        report = validate_generated_events(events)
        _print_report(mode="dry-run", report=report)
        return 0

    try:
        settings = load_settings(args.env_file)
    except ConfigurationError as exc:
        print(str(exc))
        return 2

    producer = KafkaEventProducer.from_settings(settings)
    try:
        report = publish_generated_events(events, producer, rate_per_second=args.rate)
    except EventPublicationError as exc:
        producer.close()
        print(str(exc))
        return 1
    if producer.close():
        print("Kafka closed with undelivered synthetic events.")
        return 1
    _print_report(mode="kafka", report=report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
