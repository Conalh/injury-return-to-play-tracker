import {
  athletes as demoAthletes,
  getCaseDetail as getDemoCaseDetail,
  getShareView as getDemoShareView,
  type AthleteSummary,
  type CaseDetail,
  type FunctionalTest,
  type Phase,
  type ReadinessSignal,
  type SymptomLog,
  type WorkloadSession,
} from "@/lib/demo-data";
import type {
  ApiAthlete,
  ApiAuditEvent,
  ApiCase,
  ApiCaseDetail,
  ApiFunctionalTest,
  ApiList,
  ApiPhase,
  ApiReadiness,
  ApiShare,
  ApiShareToken,
  ApiSymptomLog,
  ApiTemplate,
  ApiTemplateDetail,
  ApiWorkloadSession,
  AthletePayload,
  AthleteSymptomCheckInPayload,
  AthleteUpdatePayload,
  CaseCreationData,
  CasePageData,
  ClearanceDecisionPayload,
  DashboardData,
  DataSource,
  DemoSeed,
  FunctionalTestPayload,
  GuardianAcknowledgmentPayload,
  InjuryCasePayload,
  MilestoneEvidencePayload,
  SharePageData,
  ShareTokenPayload,
  SymptomLogPayload,
  TemplatePayload,
  WorkloadSessionPayload,
  AuditEvent,
} from "@/lib/api/types";
import {
  apiArrayBufferRequest,
  apiRequest,
  currentActorId,
  currentActorRole,
  currentOrganizationId,
  dataMode,
  ensureWritableApiMode,
  jsonRequest,
  UnauthorizedApiError,
  usesApi,
} from "@/lib/api/transport";

export {
  currentActorId,
  currentActorRole,
  currentOrganizationId,
  UnauthorizedApiError,
};

export type {
  ApiAthlete,
  ApiTemplate,
  ApiTemplateDetail,
  ApiTemplateMilestone,
  ApiTemplatePhase,
  AthletePayload,
  AthleteSymptomCheckInPayload,
  AthleteUpdatePayload,
  AuditEvent,
  CaseCreationData,
  CasePageData,
  ClearanceDecisionPayload,
  DashboardData,
  DataSource,
  FunctionalTestPayload,
  GuardianAcknowledgmentPayload,
  InjuryCasePayload,
  MilestoneEvidencePayload,
  SharePageData,
  ShareTokenPayload,
  SymptomLogPayload,
  TemplatePayload,
  WorkloadSessionPayload,
} from "@/lib/api/types";

export async function getDashboardData(): Promise<DashboardData> {
  if (!usesApi()) {
    return { source: "demo", athletes: demoAthletes };
  }

  await seedDemoIfConfigured();
  const casesResponse = await apiRequest<ApiList<ApiCase>>("/api/injury-cases");
  const caseDetails = await Promise.all(
    casesResponse.items.map((injuryCase) => getApiCasePageData(injuryCase.id)),
  );

  return {
    source: "api",
    athletes: caseDetails.map(({ detail }) => detail.athlete),
  };
}

export async function getCasePageData(caseId: string): Promise<CasePageData> {
  if (!usesApi()) {
    return { source: "demo", detail: getDemoCaseDetail(caseId), auditEvents: [] };
  }

  const seed = await seedDemoIfConfigured();
  const apiCaseId = seed && caseId === "case_demo" ? seed.injury_case_id : caseId;
  return getApiCasePageData(apiCaseId);
}

export async function getCaseReportPdf(caseId: string): Promise<ArrayBuffer> {
  ensureWritableApiMode();
  return apiArrayBufferRequest(`/api/injury-cases/${caseId}/report`, "report");
}

export async function getSharePageData(token: string): Promise<SharePageData> {
  if (!usesApi()) {
    return { source: "demo", share: getDemoShareView(token) };
  }

  const seed = await seedDemoIfConfigured();
  const apiToken = seed?.share_token && token === "demo-coach-token" ? seed.share_token : token;
  const share = await apiRequest<ApiShare>(`/api/share/${apiToken}`);
  return {
    source: "api",
    share: {
      token: apiToken,
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
    },
  };
}

export async function getCaseCreationData(): Promise<CaseCreationData> {
  if (!usesApi()) {
    return { source: "demo", athletes: [], templates: [] };
  }

  await seedDemoIfConfigured();
  const [athletes, templates] = await Promise.all([
    apiRequest<ApiList<ApiAthlete>>("/api/athletes"),
    apiRequest<ApiList<ApiTemplate>>("/api/templates"),
  ]);
  return {
    source: "api",
    athletes: athletes.items,
    templates: templates.items.filter((template) => template.active),
  };
}

export async function getTemplateListData(): Promise<{
  source: DataSource;
  templates: ApiTemplate[];
}> {
  if (!usesApi()) {
    return { source: "demo", templates: [] };
  }

  await seedDemoIfConfigured();
  const templates = await apiRequest<ApiList<ApiTemplate>>("/api/templates");
  return { source: "api", templates: templates.items };
}

export async function getTemplatePageData(templateId: string): Promise<{
  source: DataSource;
  template: ApiTemplateDetail;
}> {
  ensureWritableApiMode();
  const template = await apiRequest<ApiTemplateDetail>(`/api/templates/${templateId}`);
  return { source: "api", template };
}

export async function createAthlete(payload: AthletePayload): Promise<ApiAthlete> {
  ensureWritableApiMode();
  return apiRequest<ApiAthlete>("/api/athletes", jsonRequest("POST", payload));
}

export async function updateAthlete(
  athleteId: string,
  payload: AthleteUpdatePayload,
): Promise<ApiAthlete> {
  ensureWritableApiMode();
  return apiRequest<ApiAthlete>(`/api/athletes/${athleteId}`, jsonRequest("PATCH", payload));
}

export async function createInjuryCase(payload: InjuryCasePayload): Promise<ApiCase> {
  ensureWritableApiMode();
  return apiRequest<ApiCase>("/api/injury-cases", jsonRequest("POST", payload));
}

export async function applyTemplate(caseId: string, templateId: string): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(`/api/injury-cases/${caseId}/apply-template`, jsonRequest("POST", {
    template_id: templateId,
  }));
}

export async function createTemplate(payload: TemplatePayload): Promise<ApiTemplateDetail> {
  ensureWritableApiMode();
  return apiRequest<ApiTemplateDetail>("/api/templates", jsonRequest("POST", payload));
}

export async function updateTemplateVersion(
  templateId: string,
  payload: TemplatePayload,
): Promise<ApiTemplateDetail> {
  ensureWritableApiMode();
  return apiRequest<ApiTemplateDetail>(`/api/templates/${templateId}`, jsonRequest("PATCH", payload));
}

export async function archiveTemplate(templateId: string): Promise<ApiTemplate> {
  ensureWritableApiMode();
  return apiRequest<ApiTemplate>(`/api/templates/${templateId}/archive`, {
    method: "POST",
  });
}

export async function createSymptomLog(
  caseId: string,
  payload: SymptomLogPayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(`/api/injury-cases/${caseId}/symptoms`, jsonRequest("POST", payload));
}

export async function createFunctionalTest(
  caseId: string,
  payload: FunctionalTestPayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(
    `/api/injury-cases/${caseId}/functional-tests`,
    jsonRequest("POST", payload),
  );
}

export async function createWorkloadSession(
  caseId: string,
  payload: WorkloadSessionPayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(
    `/api/injury-cases/${caseId}/workload-sessions`,
    jsonRequest("POST", payload),
  );
}

export async function updateMilestoneEvidence(
  caseId: string,
  milestoneId: string,
  payload: MilestoneEvidencePayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(
    `/api/injury-cases/${caseId}/milestones/${milestoneId}`,
    jsonRequest("PATCH", payload),
  );
}

export async function createClearanceDecision(
  caseId: string,
  payload: ClearanceDecisionPayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(`/api/injury-cases/${caseId}/clearance`, jsonRequest("POST", payload));
}

export async function createShareToken(
  caseId: string,
  payload: ShareTokenPayload,
): Promise<ApiShareToken> {
  ensureWritableApiMode();
  return apiRequest<ApiShareToken>(`/api/injury-cases/${caseId}/share`, jsonRequest("POST", payload));
}

export async function revokeShareToken(token: string): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(`/api/share/${token}/revoke`, jsonRequest("POST", {
    revoked_by: currentActorId(),
  }));
}

export async function submitAthleteSymptomCheckIn(
  token: string,
  payload: AthleteSymptomCheckInPayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(`/api/share/${token}/symptoms`, jsonRequest("POST", payload));
}

export async function submitGuardianAcknowledgment(
  token: string,
  payload: GuardianAcknowledgmentPayload,
): Promise<void> {
  ensureWritableApiMode();
  await apiRequest(
    `/api/share/${token}/guardian-acknowledgment`,
    jsonRequest("POST", payload),
  );
}

async function getApiCasePageData(caseId: string): Promise<CasePageData> {
  const [detail, readiness, athletesResponse, auditResponse] = await Promise.all([
    apiRequest<ApiCaseDetail>(`/api/injury-cases/${caseId}`),
    apiRequest<ApiReadiness>(`/api/injury-cases/${caseId}/readiness`),
    apiRequest<ApiList<ApiAthlete>>("/api/athletes"),
    apiRequest<ApiList<ApiAuditEvent>>(`/api/injury-cases/${caseId}/audit-log`),
  ]);
  const athlete = athletesResponse.items.find((item) => item.id === detail.athlete_id);
  return {
    source: "api",
    detail: toCaseDetail(detail, readiness, athlete),
    auditEvents: auditResponse.items.map(toAuditEvent),
  };
}

async function seedDemoIfConfigured(): Promise<DemoSeed | null> {
  if (dataMode() !== "api-demo") {
    return null;
  }
  return apiRequest<DemoSeed>("/api/demo/seed", { method: "POST" });
}

function toCaseDetail(
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

function toAuditEvent(event: ApiAuditEvent): AuditEvent {
  return {
    id: event.id,
    eventType: event.event_type,
    actorId: event.actor_id ?? "public share view",
    occurredAt: formatDate(event.created_at.slice(0, 10)),
    metadata: event.metadata_json,
  };
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
