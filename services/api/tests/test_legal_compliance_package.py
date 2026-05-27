from pathlib import Path


def test_legal_compliance_review_package_covers_goal_34_deliverables() -> None:
    root = Path(__file__).resolve().parents[3]
    package = root / "docs" / "product" / "legal-compliance-review-package.md"

    assert package.exists()
    text = package.read_text(encoding="utf-8")

    required_sections = [
        "# Legal And Compliance Review Package",
        "## Review Scope",
        "## Data Flow Map",
        "## User Role And Data Access Matrix",
        "## Security Controls Summary",
        "## HIPAA And FTC Review Notes",
        "## Terms And Privacy Policy Input Packet",
        "## BAA Decision Checklist",
        "## Counsel Review Questions",
        "## Launch Gate",
    ]
    for section in required_sections:
        assert section in text

    required_references = [
        "permission-matrix.md",
        "privacy-controls.md",
        "security-baseline.md",
        "safety-and-compliance-notes.md",
        "backups-and-recovery.md",
        "observability.md",
    ]
    for reference in required_references:
        assert reference in text
