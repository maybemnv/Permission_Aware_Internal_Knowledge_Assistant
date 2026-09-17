import pytest

from apps.api.config import Settings


def test_fixture_mode_is_rejected_outside_local_fixture(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_MODE", "fixture")

    with pytest.raises(ValueError, match="local-fixture"):
        Settings.from_env()
