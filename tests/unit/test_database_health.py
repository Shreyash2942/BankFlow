from unittest.mock import Mock

from sqlalchemy.exc import OperationalError

from bankflow.database.health import check_database_health


def test_health_failure_does_not_expose_driver_message():
    engine = Mock()
    engine.connect.side_effect = OperationalError("SELECT 1", {}, Exception("password=do-not-leak"))
    result = check_database_health(engine)
    assert not result.healthy
    assert "POSTGRES_*" in result.message
    assert "do-not-leak" not in result.message
