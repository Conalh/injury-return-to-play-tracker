from __future__ import annotations


PASSED_MILESTONE_STATUSES = {"passed", "waived"}


def build_readiness(
    *,
    injury_case_id: str,
    current_phase: dict | None,
    symptom_logs: list[dict],
    workload_sessions: list[dict],
    required_clearance_roles: list[str] | None = None,
    clearance_decisions: list[dict] | None = None,
) -> dict:
    required_roles = required_clearance_roles or ["clinician"]
    decisions = clearance_decisions or []
    signals: list[dict] = []

    missing_milestones = _missing_required_milestones(current_phase)
    if missing_milestones:
        signals.append(
            {
                "type": "missing_required_milestones",
                "severity": "blocker",
                "message": "Required milestone missing.",
                "source_facts": missing_milestones,
            }
        )

    symptom_signal = _symptom_worsening_signal(symptom_logs)
    if symptom_signal is not None:
        signals.append(symptom_signal)

    workload_signal = _workload_tolerance_signal(workload_sessions)
    if workload_signal is not None:
        signals.append(workload_signal)

    missing_roles = _missing_clearance_roles(required_roles, decisions)
    if missing_roles:
        signals.append(
            {
                "type": "clearance_completeness",
                "severity": "blocker",
                "message": "Clinician clearance required.",
                "source_facts": [
                    {"missing_role": missing_role} for missing_role in missing_roles
                ],
            }
        )

    return {
        "injury_case_id": injury_case_id,
        "current_phase_id": current_phase["id"] if current_phase else None,
        "current_phase_name": current_phase["name"] if current_phase else None,
        "can_auto_clear": False,
        "summary": {
            "missing_required_milestone_count": len(missing_milestones),
            "concern_count": len(
                [
                    signal
                    for signal in signals
                    if signal["type"] in {"symptom_worsening", "workload_tolerance"}
                ]
            ),
            "missing_clearance_count": len(missing_roles),
        },
        "signals": signals,
    }


def _missing_required_milestones(current_phase: dict | None) -> list[dict]:
    if current_phase is None:
        return []

    missing = []
    for milestone in current_phase["milestones"]:
        if milestone["required"] and milestone["status"] not in PASSED_MILESTONE_STATUSES:
            missing.append(
                {
                    "phase_id": current_phase["id"],
                    "milestone_id": milestone["id"],
                    "title": milestone["title"],
                    "status": milestone["status"],
                }
            )
    return missing


def _symptom_worsening_signal(symptom_logs: list[dict]) -> dict | None:
    recent_logs = sorted(symptom_logs, key=lambda log: log["date"])[-7:]
    if not recent_logs:
        return None

    latest = recent_logs[-1]
    previous = recent_logs[-2] if len(recent_logs) > 1 else None
    pain_increase = latest["pain"] - previous["pain"] if previous else 0
    severity = None

    if latest["swelling"] == "severe" or latest["pain"] >= 7:
        severity = "severe"
    elif latest["swelling"] == "moderate" or latest["pain"] >= 5:
        severity = "moderate"
    elif pain_increase >= 2:
        severity = "mild"

    if severity is None:
        return None

    source_fact = {
        "date": latest["date"],
        "pain": latest["pain"],
        "swelling": latest["swelling"],
        "confidence": latest["confidence"],
        "pain_increase": pain_increase,
    }
    if previous is not None:
        source_fact["previous_date"] = previous["date"]
        source_fact["previous_pain"] = previous["pain"]

    return {
        "type": "symptom_worsening",
        "severity": severity,
        "message": "Review symptoms before advancing.",
        "source_facts": [source_fact],
    }


def _workload_tolerance_signal(workload_sessions: list[dict]) -> dict | None:
    concerning_sessions = [
        session
        for session in workload_sessions
        if not session["completed"] or _mentions_symptom_increase(session)
    ]
    if not concerning_sessions:
        return None

    severity = "concern" if len(concerning_sessions) >= 2 else "watch"
    return {
        "type": "workload_tolerance",
        "severity": severity,
        "message": "Workload progression incomplete.",
        "source_facts": [
            {
                "id": session["id"],
                "date": session["date"],
                "activity": session["activity"],
                "completed": session["completed"],
                "symptom_response": session["symptom_response"],
            }
            for session in concerning_sessions
        ],
    }


def _mentions_symptom_increase(session: dict) -> bool:
    symptom_response = session.get("symptom_response") or ""
    return "increase" in symptom_response.lower()


def _missing_clearance_roles(
    required_roles: list[str],
    clearance_decisions: list[dict],
) -> list[str]:
    decided_roles = {
        decision.get("decided_by_role")
        for decision in clearance_decisions
        if decision.get("decision") in {"advance", "clear_full", "close_case"}
    }
    return [role for role in required_roles if role not in decided_roles]
