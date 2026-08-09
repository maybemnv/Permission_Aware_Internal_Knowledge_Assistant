from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOCUMENTS = {
    "README.md": ROOT / "README.md",
    "DEMO_SCRIPT.md": ROOT / "DEMO_SCRIPT.md",
    "RUNBOOK.md": ROOT / "RUNBOOK.md",
    "CONNECTOR_MATRIX.md": ROOT / "CONNECTOR_MATRIX.md",
    "deployment.md": ROOT / "deployment.md",
}

CONNECTORS = (
    "Google Drive",
    "SharePoint",
    "Slack",
    "Teams",
    "Notion",
    "Confluence",
    "Jira",
    "GitHub",
)

SECRET_NAMES = (
    "DATABASE_URL",
    "SUPABASE_POOLER_URL",
    "SUPABASE_DIRECT_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "REDIS_URL",
    "OPENSEARCH_PASSWORD",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "APP_SECRET_KEY",
    "ADMIN_TOKEN",
    "CONNECTOR_CREDENTIALS_ENCRYPTION_KEY",
    "GOOGLE_DRIVE_CLIENT_SECRET",
    "SHAREPOINT_CLIENT_SECRET",
    "SLACK_BOT_TOKEN",
    "TEAMS_CLIENT_SECRET",
    "NOTION_TOKEN",
    "CONFLUENCE_CLIENT_SECRET",
    "JIRA_API_TOKEN",
    "GITHUB_APP_PRIVATE_KEY",
)


def _document_text() -> str:
    missing = [name for name, path in DOCUMENTS.items() if not path.is_file()]
    assert not missing, f"Missing Task 7 documents: {', '.join(missing)}"
    return "\n".join(path.read_text(encoding="utf-8") for path in DOCUMENTS.values())


def _read_document(name: str) -> str:
    path = DOCUMENTS[name]
    assert path.is_file(), f"Missing Task 7 document: {name}"
    return path.read_text(encoding="utf-8")


def test_task7_documents_exist() -> None:
    missing = [name for name, path in DOCUMENTS.items() if not path.is_file()]
    assert not missing, f"Missing Task 7 documents: {', '.join(missing)}"


def test_readme_exposes_setup_demo_commands_environment_and_limitations() -> None:
    text = _read_document("README.md")
    required = (
        "## Quick start",
        "## Fixture seed and reset",
        "## Run the API, web, and worker",
        "## Tests and acceptance commands",
        "## Environment variables",
        "## Known limitations",
        "pytest -q",
        "npm run lint",
        "npm run build",
        "X-Demo-Principal",
    )
    missing = [fragment for fragment in required if fragment not in text]
    assert not missing, f"README is missing required contract text: {missing}"


def test_connector_matrix_covers_all_eight_connectors_and_status_labels() -> None:
    text = _read_document("CONNECTOR_MATRIX.md")
    missing_connectors = [connector for connector in CONNECTORS if connector not in text]
    assert not missing_connectors, f"Missing connector rows: {missing_connectors}"

    for label in ("fixture", "live", "blocked", "unverified", "configured", "running", "healthy", "degraded", "failed", "paused"):
        assert label in text.lower(), f"Missing connector status label: {label}"


def test_deployment_handoff_covers_required_operational_choices() -> None:
    text = _read_document("deployment.md").lower()
    required = (
        "supabase",
        "postgresql",
        "pgvector",
        "managed opensearch",
        "self-hosted opensearch",
        "postgres-only",
        "redis",
        "supabase jobs",
        "web",
        "api",
        "worker",
        "domain",
        "tls",
        "migrations",
        "seed",
        "/health",
        "/health/ready",
        "logging",
        "monitoring",
        "backups",
        "rollback",
        "smoke test",
        "client-owned",
        "live verification",
        "[redacted_secret]",
    )
    missing = [fragment for fragment in required if fragment not in text]
    assert not missing, f"Deployment handoff is missing required coverage: {missing}"


def test_secret_inventory_names_are_present_and_only_use_redacted_values() -> None:
    text = _document_text()
    missing = [name for name in SECRET_NAMES if name not in text]
    assert not missing, f"Secret names missing from documentation: {missing}"

    for name in SECRET_NAMES:
        assignments = re.findall(rf"(?im)^\s*{re.escape(name)}\s*=\s*(.+?)\s*$", text)
        assert assignments, f"Secret {name} must have a redacted example assignment"
        assert all(value.strip() == "[REDACTED_SECRET]" for value in assignments), (
            f"Secret {name} has a non-redacted example value"
        )


def test_documentation_contains_no_common_committed_secret_signatures() -> None:
    text = _document_text()
    forbidden = (
        r"sk-[A-Za-z0-9]{16,}",
        r"sk-ant-[A-Za-z0-9_-]{16,}",
        r"gh[pousr]_[A-Za-z0-9]{20,}",
        r"xox[baprs]-[A-Za-z0-9-]{16,}",
        r"AIza[A-Za-z0-9_-]{20,}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(?i)://[^\s:/]+:[^\s@]+@",
    )
    matches = [pattern for pattern in forbidden if re.search(pattern, text)]
    assert not matches, f"Documentation contains secret-like value signatures: {matches}"


def test_acceptance_commands_are_explicitly_recorded_as_local_or_unverified() -> None:
    text = _document_text().lower()
    for command in ("pytest -q", "npm run lint", "npm run build", "npm run dev", "uvicorn"):
        assert command in text, f"Missing acceptance command reference: {command}"
    assert "unverified" in text
