from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_workflows_opt_into_node_24_actions_runtime() -> None:
    for workflow_name in ["ci.yml", "security.yml"]:
        workflow = ROOT / ".github" / "workflows" / workflow_name
        text = workflow.read_text(encoding="utf-8")

        assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: \"true\"" in text
        assert "actions/checkout@v7" in text


def test_actions_runtime_runbook_covers_node_24_transition() -> None:
    runbook = ROOT / "docs" / "operations" / "github-actions-runtime-readiness.md"

    assert runbook.exists()
    text = runbook.read_text(encoding="utf-8")

    for section in [
        "# GitHub Actions Runtime Readiness",
        "## Scope",
        "## Runtime Control",
        "## Validation",
        "## Upgrade Response",
        "## Launch Gate Impact",
    ]:
        assert section in text

    for required_phrase in [
        "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24",
        ".github/workflows/ci.yml",
        ".github/workflows/security.yml",
        "actions/checkout@v7",
        "actions/setup-node@v6",
        "actions/setup-python@v6",
        "docs/operations/ci-required-checks.md",
        "docs/operations/dependency-update-automation.md",
    ]:
        assert required_phrase in text


def test_ci_and_launch_docs_reference_actions_runtime_readiness() -> None:
    ci_checks = (ROOT / "docs" / "operations" / "ci-required-checks.md").read_text(
        encoding="utf-8"
    )
    launch_gate = (ROOT / "docs" / "operations" / "production-launch-gate.md").read_text(
        encoding="utf-8"
    )

    assert "github-actions-runtime-readiness.md" in ci_checks
    assert "github-actions-runtime-readiness.md" in launch_gate
