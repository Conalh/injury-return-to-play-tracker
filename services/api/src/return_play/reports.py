from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_case_report_pdf(case_detail: dict, readiness: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter, pageCompression=0)
    width, height = letter
    y = height - 72

    def line(text: str, size: int = 11, gap: int = 18) -> None:
        nonlocal y
        pdf.setFont("Helvetica", size)
        pdf.drawString(72, y, text)
        y -= gap

    line("Return-to-Play Status Report", 16, 26)
    line(f"Athlete: {case_detail.get('athlete_name', 'Unknown')}")
    line(f"Injury: {case_detail.get('title', 'Unknown injury')}")
    line(f"Status: {case_detail.get('status', 'active')}")
    line("This report summarizes tracked evidence. It is not medical clearance.")
    y -= 8

    line("Readiness Signals", 13, 22)
    for signal in readiness.get("signals", []):
        line(f"- {signal['message']} ({signal['type']})", 10, 14)

    y -= 8
    line("Restrictions and clearance require named human decision records.", 10, 14)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
