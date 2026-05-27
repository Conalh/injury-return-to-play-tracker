from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_dependabot_covers_all_managed_dependency_surfaces() -> None:
    config = ROOT / ".github" / "dependabot.yml"

    assert config.exists()
    text = config.read_text(encoding="utf-8")

    for required_phrase in [
        "version: 2",
        'package-ecosystem: "npm"',
        'directory: "/apps/web"',
        'package-ecosystem: "pip"',
        'directory: "/services/api"',
        'package-ecosystem: "github-actions"',
        'directory: "/"',
        "open-pull-requests-limit",
        "groups:",
        "security-updates",
    ]:
        assert required_phrase in text


def test_dependency_update_runbook_covers_triage_and_launch_gate() -> None:
    package = ROOT / "docs" / "operations" / "dependency-update-automation.md"

    assert package.exists()
    text = package.read_text(encoding="utf-8")

    for section in [
        "# Dependency Update Automation",
        "## Scope",
        "## Dependabot Configuration",
        "## Update Triage",
        "## Security Update Response",
        "## Validation",
        "## Launch Gate Impact",
    ]:
        assert section in text

    for required_phrase in [
        ".github/dependabot.yml",
        "apps/web/package-lock.json",
        "services/api/pyproject.toml",
        ".github/workflows",
        "npm audit --audit-level=high",
        "pip-audit --strict",
        "docs/operations/production-launch-gate.md",
    ]:
        assert required_phrase in text


def test_launch_and_security_docs_reference_dependency_update_automation() -> None:
    launch_gate = (ROOT / "docs" / "operations" / "production-launch-gate.md").read_text(
        encoding="utf-8"
    )
    security_baseline = (ROOT / "docs" / "product" / "security-baseline.md").read_text(
        encoding="utf-8"
    )

    assert "dependency-update-automation.md" in launch_gate
    assert "Dependency update automation" in security_baseline
