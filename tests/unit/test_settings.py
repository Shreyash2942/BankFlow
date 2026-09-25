import pytest
from pydantic import ValidationError

from bankflow.config.settings import ConfigurationError, Settings, load_settings


def test_environment_overrides_file_and_arguments_override_environment(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("POSTGRES_PASSWORD=fixture-secret\nPOSTGRES_PORT=5433\n", encoding="utf-8")
    monkeypatch.setenv("POSTGRES_PORT", "5544")
    assert load_settings(env).postgres_port == 5544
    assert Settings(_env_file=env, postgres_port=6655).postgres_port == 6655


@pytest.mark.parametrize("password", ["", "   "])
def test_blank_password_is_rejected(password):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, postgres_password=password)


@pytest.mark.parametrize("port", [0, 65536, "not-a-port"])
def test_bad_port_is_rejected(port):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, postgres_password="fixture-secret", postgres_port=port)


def test_missing_password_has_safe_actionable_message():
    with pytest.raises(ConfigurationError, match="POSTGRES_PASSWORD"):
        load_settings(None)


def test_unknown_dotenv_setting_and_bad_secret_type_do_not_leak_values(tmp_path):
    env = tmp_path / ".env"
    env.write_text("POSTGRES_PASSWORD=private-value\nTYPO_SECRET=must-not-leak\n")
    with pytest.raises(ConfigurationError) as error:
        load_settings(env)
    assert "TYPO_SECRET" in str(error.value)
    assert "must-not-leak" not in str(error.value)
    assert "private-value" not in str(error.value)


def test_url_preserves_special_characters_without_exposing_password():
    password = "a@b:/%#? secret"
    settings = Settings(_env_file=None, postgres_password=password)
    assert settings.database_url.password == password
    assert password not in str(settings.database_url)
    assert password not in repr(settings)
    assert password not in settings.model_dump_json()


def test_invalid_secret_input_is_hidden_in_validation_message():
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, postgres_password={"private-value": "hidden"})
    assert "private-value" not in str(error.value)
