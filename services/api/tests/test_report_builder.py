from io import BytesIO

from pypdf import PdfReader

from helpers import create_client


def test_pdf_report_contains_production_sections_without_forbidden_clearance_language() -> None:
    client = create_client()
    seed = client.post("/api/demo/seed").json()

    response = client.get(f"/api/injury-cases/{seed['injury_case_id']}/report")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")

    reader = PdfReader(BytesIO(response.content))
    text = "\n".join(page.extract_text() for page in reader.pages)

    for expected in [
        "Return-to-Play Status Report",
        "Non-diagnostic disclaimer",
        "Status Summary",
        "Phase Summary",
        "Evidence Summary",
        "Restrictions",
        "Clearance Decisions",
        "Audit Metadata",
        "Riley Chen",
        "Restore motion",
        "No contact drills. No full-speed cutting.",
        "Symptoms require clinician review before progression.",
        "report_generated",
    ]:
        assert expected in text

    forbidden_phrases = [
        "medically cleared",
        "safe to play",
        "automatic clearance",
        "diagnosis:",
    ]
    assert all(phrase not in text.lower() for phrase in forbidden_phrases)


def test_pdf_report_has_renderable_pages_with_stable_letter_dimensions() -> None:
    client = create_client()
    seed = client.post("/api/demo/seed").json()

    response = client.get(f"/api/injury-cases/{seed['injury_case_id']}/report")

    reader = PdfReader(BytesIO(response.content))
    assert len(reader.pages) >= 1
    for page in reader.pages:
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        assert 610 <= width <= 612
        assert 790 <= height <= 792
