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
type ApiAthlete = {
  id: string;
  name: string;
  sport: string;
  position: string | null;
};
type ApiCase = {
  id: string;
  athlete_id: string;
  title: string;
  summary: string | null;
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
    return { source: "demo", detail: getDemoCaseDetail(caseId) };
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

async function getApiCasePageData(caseId: string): Promise<CasePageData> {
  const [detail, readiness, athletesResponse] = await Promise.all([
    apiRequest<ApiCaseDetail>(`/api/injury-cases/${caseId}`),
    apiRequest<ApiReadiness>(`/api/injury-cases/${caseId}/readiness`),
    apiRequest<ApiList<ApiAthlete>>("/api/athletes"),
  ]);
  const athlete = athletesResponse.items.find((item) => item.id === detail.athlete_id);
  return {
    source: "api",
    detail: toCaseDetail(detail, readiness, athlete),
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
    athlete: athleteSummary,
    injuryTitle: detail.title,
    summary: detail.summary ?? "No case summary recorded.",
    restrictions: clearance?.restrictions ?? "No current restrictions recorded.",
    clinicianNote: note?.body ?? clearance?.rationale ?? "No clinician note recorded.",
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
