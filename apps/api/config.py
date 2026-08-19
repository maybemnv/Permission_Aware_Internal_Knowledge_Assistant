"""Environment configuration with safe fixture defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str = "demo"
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
        return cls(
            app_env=os.getenv("APP_ENV", "demo"),
            app_mode=os.getenv("APP_MODE", "fixture"),
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
