import {
  athletes as demoAthletes,
  getCaseDetail as getDemoCaseDetail,
  getShareView as getDemoShareView,
  type AthleteSummary,
  type CaseDetail,
  type FunctionalTest,
  type Phase,
  type ReadinessSignal,
  type ShareView,
  type SymptomLog,
  type WorkloadSession,
} from "@/lib/demo-data";

export type DataSource = "demo" | "api";

export type DashboardData = {
  source: DataSource;
  athletes: AthleteSummary[];
};

export type CasePageData = {
  source: DataSource;
  detail: CaseDetail;
  auditEvents: AuditEvent[];
};

export type SharePageData = {
  source: DataSource;
  share: ShareView;
};

export class UnauthorizedApiError extends Error {
  constructor(message = "Your session does not have access to this workflow.") {
    super(message);
    this.name = "UnauthorizedApiError";
  }
}

type ApiList<T> = { items: T[] };
type DemoSeed = { injury_case_id: string; share_token: string | null };
export type ApiAthlete = {
  id: string;
  organization_id: string;
  name: string;
  date_of_birth: string;
  sport: string;
  position: string | null;
  guardian_contact: string | null;
  active: boolean;
};
type ApiCase = {
  id: string;
  organization_id: string;
  athlete_id: string;
  title: string;
  injury_category: string;
  body_region: string;
  side: string;
  date_of_injury: string;
  clinician_owner_id: string;
  summary: string | null;
};
export type ApiTemplate = {
  id: string;
  organization_id: string;
  name: string;
  injury_category: string;
  description: string | null;
  created_by: string;
  version: number;
  active: boolean;
};
export type ApiTemplateMilestone = {
  id: string;
  title: string;
  kind: string;
  required: boolean;
  instructions: string | null;
};
export type ApiTemplatePhase = {
  id: string;
  name: string;
  order_index: number;
  objective: string | null;
  minimum_days: number;
  exit_summary: string | null;
  milestones: ApiTemplateMilestone[];
};
export type ApiTemplateDetail = ApiTemplate & {
  phases: ApiTemplatePhase[];
};
type ApiMilestone = {
  id: string;
  title: string;
  kind: string;
  required: boolean;
  status: "not_started" | "passed" | "failed" | "waived";
};
type ApiPhase = {
  id: string;
  name: string;
  status: "current" | "locked" | "passed" | "held";
  objective: string | null;
  minimum_days: number;
  milestones: ApiMilestone[];
};
type ApiSymptomLog = {
  date: string;
  pain: number;
  swelling: string;
  confidence: number;
};
type ApiFunctionalTest = {
  name: string;
  result_value: number | null;
  unit: string | null;
  side_to_side_difference_percent: number | null;
  passed: boolean;
  recorded_by: string;
};
type ApiWorkloadSession = {
  activity: string;
  duration_minutes: number;
  intensity: number;
  completed: boolean;
  symptom_response: string | null;
};
type ApiClearanceDecision = {
  decision: "advance" | "hold" | "clear_full" | "close_case";
  decided_by: string;
  decided_by_role: string;
  restrictions: string | null;
  rationale: string;
};
type ApiCaseDetail = ApiCase & {
  phases: ApiPhase[];
  current_phase: ApiPhase | null;
  symptom_logs: ApiSymptomLog[];
  functional_tests: ApiFunctionalTest[];
  workload_sessions: ApiWorkloadSession[];
  clearance_decisions: ApiClearanceDecision[];
  notes: { body: string }[];
};
type ApiReadiness = {
  signals: Array<{
    type: string;
    severity: string;
    message: string;
    source_facts: Record<string, unknown>;
  }>;
};
type ApiShare = {
  audience: "coach" | "guardian" | "athlete";
  athlete_name: string;
  sport: string;
  injury_title: string;
  current_phase: string | null;
  participation_status: string;
  allowed_activities: string;
  restricted_activities: string;
  next_review_date: string | null;
  clearance_status: string;
  clinician_note: string;
};
type ApiShareToken = {
  token: string;
  audience: "coach" | "guardian" | "athlete";
};
type ApiAuditEvent = {
  id: string;
  event_type: string;
  actor_id: string;
  created_at: string;
  metadata_json: Record<string, unknown>;
};

export type CaseCreationData = {
  source: DataSource;
  athletes: ApiAthlete[];
  templates: ApiTemplate[];
};

export type AthletePayload = {
  organization_id: string;
  name: string;
  date_of_birth: string;
  sport: string;
  position?: string | null;
  guardian_contact?: string | null;
  active?: boolean;
};

export type AthleteUpdatePayload = Partial<
  Pick<AthletePayload, "name" | "date_of_birth" | "sport" | "position" | "guardian_contact" | "active">
>;

export type InjuryCasePayload = {
  organization_id: string;
  athlete_id: string;
  title: string;
  injury_category: string;
  body_region: string;
  side: string;
  date_of_injury: string;
  clinician_owner_id: string;
  summary?: string | null;
};
export type TemplatePayload = {
  organization_id: string;
  name: string;
  injury_category: string;
  description?: string | null;
  created_by: string;
  phases: Array<{
    name: string;
    order_index: number;
    objective?: string | null;
    minimum_days: number;
    exit_summary?: string | null;
    milestones: Array<{
      title: string;
      kind: string;
      required: boolean;
      instructions?: string | null;
    }>;
  }>;
};
export type SymptomLogPayload = {
  injury_case_id: string;
  athlete_id: string;
  date: string;
  pain: number;
  swelling: string;
  confidence: number;
  notes?: string | null;
};
export type FunctionalTestPayload = {
  injury_case_id: string;
  name: string;
  test_date: string;
  result_value?: number | null;
  unit?: string | null;
  side_to_side_difference_percent?: number | null;
  passed: boolean;
  recorded_by: string;
  notes?: string | null;
};
export type WorkloadSessionPayload = {
  injury_case_id: string;
  date: string;
  activity: string;
  duration_minutes: number;
  intensity: number;
  symptom_response?: string | null;
  completed: boolean;
  notes?: string | null;
};
export type MilestoneEvidencePayload = {
  status: "not_started" | "passed" | "failed" | "waived";
  recorded_by: string;
  notes?: string | null;
  evidence_json: Record<string, string>;
};
export type ClearanceDecisionPayload = {
  injury_case_id: string;
  phase_id: string;
  decision: "advance" | "hold" | "clear_full" | "close_case";
  decided_by: string;
  decided_by_role: string;
  rationale: string;
  restrictions?: string | null;
};
export type ShareTokenPayload = {
  injury_case_id: string;
  audience: "coach" | "guardian" | "athlete";
  expires_in_days: number;
  created_by: string;
  allowed_activities: string;
  restricted_activities: string;
  clinician_note: string;
  next_review_date?: string | null;
};
export type AthleteSymptomCheckInPayload = {
  date: string;
  pain: number;
  swelling: "none" | "mild" | "moderate" | "severe";
  confidence: number;
  notes?: string | null;
};
export type AuditEvent = {
  id: string;
  eventType: string;
  actorId: string;
  occurredAt: string;
  metadata: Record<string, unknown>;
};

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

export function currentOrganizationId(): string {
  return process.env.RETURN_PLAY_ORGANIZATION_ID ?? "org_demo";
}

export function currentActorId(): string {
  return process.env.RETURN_PLAY_ACTOR_ID ?? "clinician_demo";
}

export function currentActorRole(): string {
  return process.env.RETURN_PLAY_ACTOR_ROLE ?? "clinician";
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

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      ...authHeaders(),
      ...(init.headers ?? {}),
    },
  });
  if (response.status === 401 || response.status === 403) {
    throw new UnauthorizedApiError();
  }
  if (!response.ok) {
    throw new Error(`API request failed with ${response.status}: ${path}`);
  }
  return response.json() as Promise<T>;
}

function jsonRequest(method: "POST" | "PATCH", payload: unknown): RequestInit {
  return {
    method,
    body: JSON.stringify(payload),
    headers: {
      "content-type": "application/json",
    },
  };
}

function ensureWritableApiMode() {
  if (!usesApi()) {
    throw new Error("Case creation requires RETURN_PLAY_DATA_MODE=api or api-demo.");
  }
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
    source: Object.values(signal.source_facts).join(", "),
  };
}

function toAuditEvent(event: ApiAuditEvent): AuditEvent {
  return {
    id: event.id,
    eventType: event.event_type,
    actorId: event.actor_id,
    occurredAt: formatDate(event.created_at.slice(0, 10)),
    metadata: event.metadata_json,
  };
}

function usesApi(): boolean {
  return dataMode() === "api" || dataMode() === "api-demo";
}

function dataMode(): string {
  return process.env.RETURN_PLAY_DATA_MODE ?? "demo";
}

function apiBaseUrl(): string {
  return process.env.RETURN_PLAY_API_BASE_URL ?? "http://127.0.0.1:8000";
}

function authHeaders(): Record<string, string> {
  const token = process.env.RETURN_PLAY_API_TOKEN;
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {
    "x-actor-id": process.env.RETURN_PLAY_ACTOR_ID ?? "clinician_demo",
    "x-actor-role": process.env.RETURN_PLAY_ACTOR_ROLE ?? "clinician",
    "x-organization-id": process.env.RETURN_PLAY_ORGANIZATION_ID ?? "org_demo",
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
