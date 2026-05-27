from __future__ import annotations

from io import BytesIO
from textwrap import wrap

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_case_report_pdf(
    case_detail: dict,
    readiness: dict,
    audit_events: list[dict] | None = None,
) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter, pageCompression=0)
    width, height = letter
    y = height - 72

    def new_page_if_needed(required: int = 40) -> None:
        nonlocal y
        if y < 72 + required:
            pdf.showPage()
            y = height - 72

    def line(text: str, size: int = 10, gap: int = 15, indent: int = 0) -> None:
        nonlocal y
        new_page_if_needed(gap)
        pdf.setFont("Helvetica", size)
        for part in wrap(str(text), width=92 - indent // 6) or [""]:
            new_page_if_needed(gap)
            pdf.drawString(72 + indent, y, part)
            y -= gap

    def section(title: str) -> None:
        nonlocal y
        y -= 7
        line(title, 13, 18)

    latest_clearance = _latest(case_detail.get("clearance_decisions", []))
    current_phase = case_detail.get("current_phase") or _first_active_phase(
        case_detail.get("phases", [])
    )
    events = audit_events or []

    line("Return-to-Play Status Report", 16, 24)
    line("Non-diagnostic disclaimer", 12, 16)
    line(
        "This report summarizes tracked return-to-play workflow evidence. It is "
        "not medical clearance, diagnosis, treatment advice, or permission to participate.",
        10,
        14,
    )

    section("Status Summary")
    line(f"Athlete: {case_detail.get('athlete_name', 'Unknown')}")
    line(f"Injury: {case_detail.get('title', 'Unknown injury')}")
    line(f"Case status: {case_detail.get('status', 'active')}")
    line(f"Current phase: {current_phase.get('name', 'No phase assigned') if current_phase else 'No phase assigned'}")

    section("Phase Summary")
    for phase in case_detail.get("phases", []) or []:
        line(
            f"- {phase.get('name', 'Unnamed phase')}: {phase.get('status', 'unknown')} "
            f"({phase.get('minimum_days', 0)} minimum days)",
            10,
            14,
        )

    section("Evidence Summary")
    symptom_logs = case_detail.get("symptom_logs", []) or []
    functional_tests = case_detail.get("functional_tests", []) or []
    workload_sessions = case_detail.get("workload_sessions", []) or []
    line(f"Symptom logs: {len(symptom_logs)}")
    if symptom_logs:
        latest = _latest(symptom_logs)
        line(
            f"Latest symptom log: pain {latest.get('pain')}, swelling {latest.get('swelling')}, "
            f"confidence {latest.get('confidence')}",
            10,
            14,
        )
    line(f"Functional tests: {len(functional_tests)}")
    if functional_tests:
        passed = sum(1 for item in functional_tests if item.get("passed"))
        line(f"Functional tests passed: {passed} of {len(functional_tests)}", 10, 14)
    line(f"Workload sessions: {len(workload_sessions)}")
    if workload_sessions:
        completed = sum(1 for item in workload_sessions if item.get("completed"))
        line(f"Workload sessions completed: {completed} of {len(workload_sessions)}", 10, 14)

    section("Readiness Signals")
    for signal in readiness.get("signals", []):
        line(f"- {signal['message']} ({signal['type']})", 10, 14)

    section("Restrictions")
    line(latest_clearance.get("restrictions") if latest_clearance else "No restrictions recorded.")

    section("Clearance Decisions")
    decisions = case_detail.get("clearance_decisions", []) or []
    if not decisions:
        line("No named clearance decisions recorded.")
    for decision in decisions:
        line(
            f"- {decision.get('decision')} by {decision.get('decided_by')} "
            f"({decision.get('decided_by_role')}): {decision.get('rationale')}",
            10,
            14,
        )

    section("Audit Metadata")
    for event in events[-8:]:
        line(
            f"- {event.get('event_type')} by {event.get('actor_id')} at {event.get('created_at')}",
            10,
            14,
        )

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def _latest(items: list[dict]) -> dict:
    return items[-1] if items else {}


def _first_active_phase(phases: list[dict]) -> dict | None:
    return next(
        (
            phase
            for phase in phases
            if phase.get("status") in {"current", "held"}
        ),
        None,
    )
