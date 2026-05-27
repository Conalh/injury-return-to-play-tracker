from pathlib import Path


def test_production_launch_gate_package_covers_goal_37_deliverables() -> None:
    root = Path(__file__).resolve().parents[3]
    package = root / "docs" / "operations" / "production-launch-gate.md"

    assert package.exists()
    text = package.read_text(encoding="utf-8")

    required_sections = [
        "# Production Launch Gate",
        "## Launch Scope",
        "## Critical Test Gate",
        "## Security Baseline Gate",
        "## Backup Restore Gate",
        "## Monitoring Gate",
        "## Legal And Compliance Gate",
        "## Safety Blocker Gate",
        "## Residual Risk Register",
        "## Signoff Checklist",
    ]
    for section in required_sections:
        assert section in text

    required_references = [
        "ci-required-checks.md",
        "security-baseline.md",
        "backups-and-recovery.md",
        "observability.md",
        "legal-compliance-review-package.md",
        "safety-and-compliance-notes.md",
        "beta-readiness.md",
    ]
    for reference in required_references:
        assert reference in text
