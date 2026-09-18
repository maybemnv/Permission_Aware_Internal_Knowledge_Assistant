import pytest

from apps.api.config import Settings


def test_fixture_mode_is_rejected_outside_local_fixture(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_MODE", "fixture")

    with pytest.raises(ValueError, match="postgres"):
        Settings.from_env()


def test_production_requires_server_auth_boundary(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_MODE", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@db/app")
    monkeypatch.setenv("SEARCH_PROVIDER", "postgres")
    monkeypatch.setenv("QUEUE_PROVIDER", "redis")
    monkeypatch.setenv("REDIS_URL", "redis://redis/0")
    with pytest.raises(ValueError, match="AUTH_BEARER_TOKEN"):
        Settings.from_env()
