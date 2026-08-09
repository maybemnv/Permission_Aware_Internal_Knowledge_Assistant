from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_release_contains_client_handoff_and_runtime_boundaries() -> None:
    required = [
        "README.md",
        "DEMO_SCRIPT.md",
        "RUNBOOK.md",
        "CONNECTOR_MATRIX.md",
        "deployment.md",
        "tests/acceptance/acceptance_matrix.md",
        ".env.example",
        "db/migrations/001_initial.sql",
        "db/seed_demo.sql",
        "apps/api/main.py",
        "apps/web/package.json",
        "connectors/registry.py",
        "workers/sync.py",
    ]

    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []


def test_no_real_secret_values_are_present_in_release_docs() -> None:
    for name in ("README.md", "DEMO_SCRIPT.md", "RUNBOOK.md", "CONNECTOR_MATRIX.md", "deployment.md", ".env.example"):
        content = (ROOT / name).read_text(encoding="utf-8").lower()
        assert "sk-proj-" not in content
        assert "-----begin private key-----" not in content
        assert "ghp_" not in content
