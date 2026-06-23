import type {
  AthleteSummary,
  CaseDetail,
  FunctionalTest,
  Phase,
  ReadinessSignal,
  ShareView,
  SymptomLog,
  WorkloadSession,
} from "@/lib/demo-data";
import type {
  ApiAthlete,
  ApiAuditEvent,
  ApiCaseDetail,
  ApiFunctionalTest,
  ApiPhase,
  ApiReadiness,
  ApiShare,
  ApiSymptomLog,
  ApiWorkloadSession,
  AuditEvent,
} from "@/lib/api/types";

export function toShareView(token: string, share: ApiShare): ShareView {
  return {
    token,
    audience: share.audience,
    athleteName: share.athlete_name,
    sport: share.sport,
    injuryTitle: share.injury_title,
    currentPhase: share.current_phase ?? "Phase not assigned",
    participationStatus: share.participation_status,
    allowedActivities: share.allowed_activities,
    restrictedActivities: share.restricted_activities,
    nextReviewDate: formatDate(share.next_review_date),
    clearanceStatus: share.clearance_status,
    clinicianNote: share.clinician_note,
  };
}

export function toCaseDetail(
  detail: ApiCaseDetail,
  readiness: ApiReadiness,
  athlete: ApiAthlete | undefined,
): CaseDetail {
  const athleteSummary = toAthleteSummaryFromApi(detail, readiness, athlete);
  const clearance = detail.clearance_decisions.at(-1);
  const note = detail.notes.at(-1);

  return {
    id: detail.id,
    athleteId: detail.athlete_id,
    athlete: athleteSummary,
    injuryTitle: detail.title,
    summary: detail.summary ?? "No case summary recorded.",
    restrictions: clearance?.restrictions ?? "No current restrictions recorded.",
    clinicianNote: clearance?.rationale ?? note?.body ?? "No clinician note recorded.",
    phases: detail.phases.map(toPhase),
    symptomLogs: detail.symptom_logs.map(toSymptomLog),
    functionalTests: detail.functional_tests.map(toFunctionalTest),
    workloadSessions: detail.workload_sessions.map(toWorkloadSession),
    readinessSignals: readiness.signals.map(toReadinessSignal),
  };
}

export function toAuditEvent(event: ApiAuditEvent): AuditEvent {
  return {
    id: event.id,
    eventType: event.event_type,
    actorId: event.actor_id ?? "public share view",
    occurredAt: formatDate(event.created_at.slice(0, 10)),
    metadata: event.metadata_json,
  };
}

function toAthleteSummaryFromApi(
  detail: ApiCaseDetail,
  readiness: ApiReadiness,
  athlete: ApiAthlete | undefined,
): AthleteSummary {
  const currentPhase = detail.current_phase ?? detail.phases[0];
  const latestSymptom = detail.symptom_logs.at(-1);
  const missingGateCount = readiness.signals.filter(
    (signal) => signal.severity === "blocker",
  ).length;
  const primarySignal =
    readiness.signals.find((signal) => signal.type === "symptom_worsening") ??
    readiness.signals[0];

  return {
    id: detail.id,
    name: athlete?.name ?? "Unknown athlete",
    sport: athlete?.sport ?? "Sport not recorded",
    position: athlete?.position ?? "Position not recorded",
    activeInjury: detail.title,
    currentPhase: currentPhase?.name ?? "No phase assigned",
    daysInPhase: currentPhase?.minimum_days ?? 0,
    latestSymptomStatus: latestSymptom
      ? `Pain ${latestSymptom.pain}, swelling ${latestSymptom.swelling}`
      : "No symptoms logged",
    missingGateCount,
    nextAction: primarySignal?.message ?? "Continue current plan.",
    participationStatus: "Modified training only",
  };
}

function toPhase(phase: ApiPhase): Phase {
  return {
    id: phase.id,
    name: phase.name,
    status: phase.status,
    objective: phase.objective ?? "No objective recorded.",
    days: phase.minimum_days,
    milestones: phase.milestones.map((milestone) => ({
      id: milestone.id,
      title: milestone.title,
      kind: titleCase(milestone.kind),
      required: milestone.required,
      status: milestone.status,
    })),
  };
}

function toSymptomLog(log: ApiSymptomLog): SymptomLog {
  return {
    date: formatDate(log.date),
    pain: log.pain,
    swelling: log.swelling,
    confidence: log.confidence,
  };
}

function toFunctionalTest(test: ApiFunctionalTest): FunctionalTest {
  return {
    name: test.name,
    result:
      test.result_value === null
        ? "Not recorded"
        : `${test.result_value} ${test.unit ?? ""}`.trim(),
    passed: test.passed,
    recordedBy: test.recorded_by,
  };
}

function toWorkloadSession(session: ApiWorkloadSession): WorkloadSession {
  return {
    activity: session.activity,
    duration: `${session.duration_minutes} min`,
    intensity: `${session.intensity} / 10`,
    completed: session.completed,
    symptomResponse: session.symptom_response ?? "No symptom response recorded.",
  };
}

function toReadinessSignal(signal: ApiReadiness["signals"][number]): ReadinessSignal {
  return {
    type: titleCase(signal.type),
    severity: signal.severity,
    message: signal.message,
    source: sourceFactsToText(signal.source_facts),
  };
}

function sourceFactsToText(value: unknown): string {
  if (value === null || value === undefined) {
    return "No source facts recorded.";
  }
  if (Array.isArray(value)) {
    return value.map(sourceFactsToText).filter(Boolean).join("; ");
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) {
      return "No source facts recorded.";
    }
    return entries
      .map(([key, nestedValue]) => `${titleCase(key.replaceAll("_", " "))}: ${sourceFactsToText(nestedValue)}`)
      .join(", ");
  }
  return String(value);
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Not scheduled";
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
  }).format(new Date(`${value}T00:00:00`));
}

function titleCase(value: string): string {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
}
