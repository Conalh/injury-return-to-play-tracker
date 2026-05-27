from pathlib import Path


def test_usability_review_package_covers_goal_35_deliverables() -> None:
    root = Path(__file__).resolve().parents[3]
    review = root / "docs" / "product" / "usability-review.md"

    assert review.exists()
    text = review.read_text(encoding="utf-8")

    required_sections = [
        "# Product Polish And Usability Review",
        "## Review Scope",
        "## Non-Diagnostic Copy Review",
        "## Empty And Error States",
        "## Mobile Layout Pass",
        "## Accessibility Pass",
        "## Clinician Workflow Timing Review",
        "## Beta Polish Backlog",
        "## Launch Gate",
    ]
    for section in required_sections:
        assert section in text

    required_references = [
        "dashboard.spec.ts",
        "usability-review.spec.ts",
        "case-creation.spec.ts",
        "evidence-entry.spec.ts",
        "clearance-decision.spec.ts",
        "share-management.spec.ts",
    ]
    for reference in required_references:
        assert reference in text
