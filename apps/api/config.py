"""Environment configuration with safe fixture defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = "local-fixture"
    app_mode: str = "fixture"
    demo_principal: str = "allowed-user"
    search_provider: str = "fixture"
    queue_provider: str = "inline"
    model_provider: str = "fixture"
    database_url: str | None = None
    opensearch_url: str | None = None
    redis_url: str | None = None
    next_public_api_base_url: str = "/api"

    @classmethod
    def from_env(cls) -> "Settings":
        settings = cls(
            app_env=os.getenv("APP_ENV", "local-fixture").strip().lower(),
            app_mode=os.getenv("APP_MODE", "fixture").strip().lower(),
            demo_principal=os.getenv("DEMO_PRINCIPAL", "allowed-user"),
            search_provider=os.getenv("SEARCH_PROVIDER", "fixture"),
            queue_provider=os.getenv("QUEUE_PROVIDER", "inline"),
            model_provider=os.getenv("MODEL_PROVIDER", "fixture"),
            database_url=os.getenv("DATABASE_URL") or None,
            opensearch_url=os.getenv("OPENSEARCH_URL") or None,
            redis_url=os.getenv("REDIS_URL") or None,
            next_public_api_base_url=os.getenv(
                "NEXT_PUBLIC_API_BASE_URL", "/api"
            ),
        )
        settings.validate_runtime()
        return settings

    def validate_runtime(self) -> None:
        if self.app_env not in {"local-fixture", "staging", "production"}:
            raise ValueError("APP_ENV must be local-fixture, staging, or production")
        if self.app_env == "local-fixture":
            if self.app_mode != "fixture":
                raise ValueError("APP_MODE=fixture requires APP_ENV=local-fixture")
            return
        if self.app_mode != "postgres":
            raise ValueError("APP_MODE=postgres is required outside APP_ENV=local-fixture")
        if not self.database_url or not self.database_url.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL must be a PostgreSQL URL outside APP_ENV=local-fixture")
        if self.search_provider != "postgres":
            raise ValueError("SEARCH_PROVIDER=postgres is required outside APP_ENV=local-fixture")
        if self.queue_provider not in {"redis", "celery"} or not self.redis_url:
            raise ValueError("REDIS_URL and a durable queue provider are required outside APP_ENV=local-fixture")
        if not os.getenv("AUTH_BEARER_TOKEN") or not os.getenv("AUTH_PRINCIPAL_KEY"):
            raise ValueError("AUTH_BEARER_TOKEN and AUTH_PRINCIPAL_KEY are required outside APP_ENV=local-fixture")
