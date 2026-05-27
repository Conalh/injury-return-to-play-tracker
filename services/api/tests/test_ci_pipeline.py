from pathlib import Path


def test_ci_workflow_defines_required_pipeline_jobs() -> None:
    root = Path(__file__).parents[3]
    workflow = (root / ".github" / "workflows" / "ci.yml").read_text()

    assert "name: CI" in workflow
    assert "backend-tests:" in workflow
    assert "migration-head:" in workflow
    assert "web-build:" in workflow
    assert "web-playwright:" in workflow
    assert "docker-compose-build:" in workflow
    assert "dependency-audit:" in workflow
    assert ".\\.venv\\Scripts\\python.exe -m pytest" in workflow
    assert ".\\.venv\\Scripts\\alembic.exe heads" in workflow
    assert "npm run build" in workflow
    assert "npm test" in workflow
    assert "docker compose -f compose.yml config" in workflow
    assert "docker compose -f compose.yml build api web" in workflow
    assert "npm audit --audit-level=high" in workflow
    assert "python -m pip freeze --exclude-editable > audit-requirements.txt" in workflow
    assert "pip-audit --strict -r audit-requirements.txt" in workflow


def test_required_status_checks_are_documented() -> None:
    root = Path(__file__).parents[3]
    docs = (root / "docs" / "operations" / "ci-required-checks.md").read_text()

    for check_name in [
        "Backend tests",
        "Migration head check",
        "Web build",
        "Web Playwright",
        "Docker compose build",
        "Dependency audit",
        "Secret scan",
    ]:
        assert check_name in docs

    assert "branch protection" in docs.lower()
    assert ".github/workflows/ci.yml" in docs
    assert ".github/workflows/security.yml" in docs
