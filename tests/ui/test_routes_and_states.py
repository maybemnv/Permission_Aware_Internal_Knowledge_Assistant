from pathlib import Path


ROOT = Path(__file__).parents[2]
WEB = ROOT / "apps" / "web"


def read_web_file(relative_path: str) -> str:
    return (WEB / relative_path).read_text(encoding="utf-8")


def test_task_six_routes_and_components_exist() -> None:
    expected_files = [
        "package.json",
        "tsconfig.json",
        "next.config.mjs",
        "app/layout.tsx",
        "app/page.tsx",
        "app/tokens.css",
        "app/search/page.tsx",
        "app/admin/page.tsx",
        "lib/api.ts",
        "components/SearchWorkbench.tsx",
        "components/AnswerPanel.tsx",
        "components/SourcePreview.tsx",
        "components/ConnectorGrid.tsx",
        "components/StatusBadge.tsx",
    ]

    missing = [path for path in expected_files if not (WEB / path).is_file()]

    assert not missing, f"missing Task 6 web files: {missing}"


def test_ui_contains_explicit_safety_and_lifecycle_states() -> None:
    source = "\n".join(
        read_web_file(path)
        for path in [
            "components/StatusBadge.tsx",
            "components/SearchWorkbench.tsx",
            "components/AnswerPanel.tsx",
            "components/SourcePreview.tsx",
            "components/ConnectorGrid.tsx",
        ]
    )
    required_states = [
        "loading",
        "stale",
        "deleted",
        "pending_recheck",
        "unavailable",
        "insufficient_context",
        "refused",
        "failed",
        "no_accessible_context",
    ]

    for state in required_states:
        assert state in source, f"state {state!r} is not explicit in the UI"


def test_design_authority_and_accessibility_guards_are_present() -> None:
    tokens = read_web_file("app/tokens.css")
    layout = read_web_file("app/layout.tsx")
    stylesheet = read_web_file("app/tokens.css")

    for token in [
        "--brand-silver",
        "--brand-steel",
        "--brand-blue",
        "--brand-gray",
        "--brand-soft",
        "--brand-slate",
        "--brand-ink",
        "--brand-white",
        "--space-1",
        "--space-2",
        "--space-3",
        "--space-4",
    ]:
        assert token in tokens

    assert "Trebuchet MS" in tokens
    assert "Segoe UI" in tokens
    assert "ui-monospace" in tokens
    assert "prefers-reduced-motion: reduce" in stylesheet
    assert "overflow-x: hidden" in stylesheet
    assert ":focus-visible" in stylesheet
    assert "aria-label" in layout


def test_browser_bundle_does_not_handle_server_secrets() -> None:
    source = "\n".join(
        read_web_file(path)
        for path in [
            "app/layout.tsx",
            "app/page.tsx",
            "app/search/page.tsx",
            "app/admin/page.tsx",
            "components/SearchWorkbench.tsx",
            "components/AnswerPanel.tsx",
            "components/SourcePreview.tsx",
            "components/ConnectorGrid.tsx",
        ]
    ).lower()

    for forbidden in [
        "connector_secret",
        "database_url",
        "model_api_key",
        "client_secret",
        "authorization: bearer",
    ]:
        assert forbidden not in source


def test_api_boundary_uses_only_public_base_url_and_typed_request_shape() -> None:
    source = read_web_file("lib/api.ts")

    assert "NEXT_PUBLIC_API_BASE_URL" in source
    assert "SearchRequest" in source
    assert "sourceTypes" in source
    assert "freshness" in source
    assert "DATABASE_URL" not in source


def test_source_preview_state_supports_safe_close() -> None:
    source = read_web_file("components/SearchWorkbench.tsx")

    assert "useState<SourcePreviewData | null>" in source
