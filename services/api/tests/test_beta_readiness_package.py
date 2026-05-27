from pathlib import Path


def test_beta_readiness_package_covers_goal_36_deliverables() -> None:
    root = Path(__file__).resolve().parents[3]
    package = root / "docs" / "operations" / "beta-readiness.md"

    assert package.exists()
    text = package.read_text(encoding="utf-8")

    required_sections = [
        "# Beta Readiness",
        "## Beta Scope",
        "## Beta Onboarding Checklist",
        "## Feedback Capture Process",
        "## Known Limitations",
        "## Support Runbook",
        "## Incident Response Starter Plan",
        "## Beta Organization Workflow",
        "## Launch Gate",
    ]
    for section in required_sections:
        assert section in text

    required_references = [
        "legal-compliance-review-package.md",
        "usability-review.md",
        "privacy-controls.md",
        "security-baseline.md",
        "backups-and-recovery.md",
        "observability.md",
        "local-production-compose.md",
    ]
    for reference in required_references:
        assert reference in text
