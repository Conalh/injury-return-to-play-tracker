import {
  athletes as demoAthletes,
  getCaseDetail as getDemoCaseDetail,
  getShareView as getDemoShareView,
  templates as demoTemplates,
} from "@/lib/demo-data";
import { toAuditEvent, toCaseDetail, toShareView } from "@/lib/api/mappers";
import type {
  ApiAthlete,
  ApiAuditEvent,
  ApiCase,
  ApiCaseDetail,
  ApiList,
  ApiReadiness,
  ApiShare,
  ApiShareToken,
  ApiTemplate,
  ApiTemplateDetail,
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
    share: toShareView(apiToken, share),
  };
}

export async function getCaseCreationData(): Promise<CaseCreationData> {
  if (!usesApi()) {
    return {
      source: "demo",
      athletes: [],
      templates: demoTemplates.filter((template) => template.active),
    };
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
    return { source: "demo", templates: demoTemplates };
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
