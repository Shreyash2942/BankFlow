"""Keep external environment overrides from changing test database selection."""

import pytest

from bankflow.config.settings import Settings


@pytest.fixture(autouse=True)
def isolate_settings_environment(monkeypatch):
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)
        monkeypatch.delenv(name, raising=False)
