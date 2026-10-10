"""Run the BankFlow operational Kafka consumer until SIGINT or SIGTERM."""

import logging
import signal
import sys

from bankflow.config.settings import ConfigurationError, load_settings
from bankflow.database.connection import create_database_engine
from bankflow.database.session import create_session_factory
from bankflow.messaging import (
    EventPersistenceError,
    KafkaConsumerError,
    KafkaEventConsumer,
    StructuredJsonFormatter,
)

LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredJsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)


def main() -> int:
    configure_logging()
    try:
        settings = load_settings()
    except ConfigurationError as exc:
        LOGGER.error(str(exc))
        return 2

    engine = create_database_engine(settings)
    consumer = KafkaEventConsumer.from_settings(settings, create_session_factory(engine))

    def request_shutdown(signum, _frame) -> None:
        LOGGER.info("Shutdown requested", extra={"signal": signum})
        consumer.request_shutdown()

    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)
    try:
        consumer.run()
    except (KafkaConsumerError, EventPersistenceError) as exc:
        LOGGER.error(str(exc))
        return 1
    finally:
        consumer.close()
        engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
