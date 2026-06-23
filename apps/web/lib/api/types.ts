import type { AthleteSummary, CaseDetail, ShareView } from "@/lib/demo-data";

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

export type ApiList<T> = { items: T[] };
export type DemoSeed = { injury_case_id: string; share_token: string | null };

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

export type ApiCase = {
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

export type ApiMilestone = {
  id: string;
  title: string;
  kind: string;
  required: boolean;
  status: "not_started" | "passed" | "failed" | "waived";
};

export type ApiPhase = {
  id: string;
  name: string;
  status: "current" | "locked" | "passed" | "held";
  objective: string | null;
  minimum_days: number;
  milestones: ApiMilestone[];
};

export type ApiSymptomLog = {
  date: string;
  pain: number;
  swelling: string;
  confidence: number;
};

export type ApiFunctionalTest = {
  name: string;
  result_value: number | null;
  unit: string | null;
  side_to_side_difference_percent: number | null;
  passed: boolean;
  recorded_by: string;
};

export type ApiWorkloadSession = {
  activity: string;
  duration_minutes: number;
  intensity: number;
  completed: boolean;
  symptom_response: string | null;
};

export type ApiClearanceDecision = {
  decision: "advance" | "hold" | "clear_full" | "close_case";
  decided_by: string;
  decided_by_role: string;
  restrictions: string | null;
  rationale: string;
};

export type ApiCaseDetail = ApiCase & {
  phases: ApiPhase[];
  current_phase: ApiPhase | null;
  symptom_logs: ApiSymptomLog[];
  functional_tests: ApiFunctionalTest[];
  workload_sessions: ApiWorkloadSession[];
  clearance_decisions: ApiClearanceDecision[];
  notes: { body: string }[];
};

export type ApiReadiness = {
  signals: Array<{
    type: string;
    severity: string;
    message: string;
    source_facts: Record<string, unknown>;
  }>;
};

export type ApiShare = {
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

export type ApiShareToken = {
  token: string;
  audience: "coach" | "guardian" | "athlete";
};

export type ApiAuditEvent = {
  id: string;
  event_type: string;
  actor_id: string | null;
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

export type GuardianAcknowledgmentPayload = {
  acknowledged_by: string;
  relationship: string;
  message?: string | null;
};

export type AuditEvent = {
  id: string;
  eventType: string;
  actorId: string;
  occurredAt: string;
  metadata: Record<string, unknown>;
};
