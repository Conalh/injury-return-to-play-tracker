export type AthleteSummary = {
  id: string;
  name: string;
  sport: string;
  position: string;
  activeInjury: string;
  currentPhase: string;
  daysInPhase: number;
  latestSymptomStatus: string;
  missingGateCount: number;
  nextAction: string;
  participationStatus: string;
};

export type Milestone = {
  id: string;
  title: string;
  kind: string;
  required: boolean;
  status: "not_started" | "passed" | "failed" | "waived";
};

export type Phase = {
  id: string;
  name: string;
  status: "current" | "locked" | "passed" | "held";
  objective: string;
  days: number;
  milestones: Milestone[];
};

export type SymptomLog = {
  date: string;
  pain: number;
  swelling: string;
  confidence: number;
};

export type FunctionalTest = {
  name: string;
  result: string;
  passed: boolean;
  recordedBy: string;
};

export type WorkloadSession = {
  activity: string;
  duration: string;
  intensity: string;
  completed: boolean;
  symptomResponse: string;
};

export type ReadinessSignal = {
  type: string;
  severity: string;
  message: string;
  source: string;
};

export type CaseDetail = {
  id: string;
  athlete: AthleteSummary;
  injuryTitle: string;
  summary: string;
  phases: Phase[];
  symptomLogs: SymptomLog[];
  functionalTests: FunctionalTest[];
  workloadSessions: WorkloadSession[];
  readinessSignals: ReadinessSignal[];
  restrictions: string;
  clinicianNote: string;
};

export type ShareView = {
  token: string;
  audience: "coach" | "guardian" | "athlete";
  athleteName: string;
  sport: string;
  injuryTitle: string;
  currentPhase: string;
  participationStatus: string;
  allowedActivities: string;
  restrictedActivities: string;
  nextReviewDate: string;
  clearanceStatus: string;
  clinicianNote: string;
};

export const athletes: AthleteSummary[] = [
  {
    id: "case_demo",
    name: "Riley Chen",
    sport: "Soccer",
    position: "Midfielder",
    activeInjury: "Left ankle sprain",
    currentPhase: "Restore motion",
    daysInPhase: 4,
    latestSymptomStatus: "Pain 5, swelling none",
    missingGateCount: 1,
    nextAction: "Review symptoms before advancing.",
    participationStatus: "Modified training only",
  },
  {
    id: "case_secondary",
    name: "Maya Ortiz",
    sport: "Basketball",
    position: "Guard",
    activeInjury: "Right knee soreness",
    currentPhase: "Controlled practice",
    daysInPhase: 2,
    latestSymptomStatus: "Pain 2, confidence 4",
    missingGateCount: 0,
    nextAction: "Clinician clearance required.",
    participationStatus: "Non-contact practice",
  },
  {
    id: "case_third",
    name: "Noah Brooks",
    sport: "Track",
    position: "Sprinter",
    activeInjury: "Hamstring strain",
    currentPhase: "Workload progression",
    daysInPhase: 7,
    latestSymptomStatus: "Pain 1, no swelling",
    missingGateCount: 2,
    nextAction: "Functional test missing.",
    participationStatus: "Straight-line running",
  },
];

export const caseDetail: CaseDetail = {
  id: "case_demo",
  athlete: athletes[0],
  injuryTitle: "Left ankle sprain",
  summary: "Rolled ankle during match. Current work is focused on motion, symptom response, and controlled loading.",
  restrictions: "No contact drills. No full-speed cutting.",
  clinicianNote: "Hold contact drills until next review.",
  phases: [
    {
      id: "phase_restore",
      name: "Restore motion",
      status: "current",
      objective: "Move without symptom increase and complete symptom review.",
      days: 4,
      milestones: [
        {
          id: "milestone_pain",
          title: "Pain remains below configured threshold",
          kind: "Symptom",
          required: true,
          status: "not_started",
        },
        {
          id: "milestone_review",
          title: "Clinician reviews ankle motion",
          kind: "Clinician review",
          required: true,
          status: "passed",
        },
      ],
    },
    {
      id: "phase_practice",
      name: "Controlled practice",
      status: "locked",
      objective: "Resume non-contact practice with stable response.",
      days: 0,
      milestones: [
        {
          id: "milestone_practice",
          title: "Complete controlled practice",
          kind: "Workload",
          required: true,
          status: "not_started",
        },
      ],
    },
  ],
  symptomLogs: [
    { date: "May 24", pain: 2, swelling: "none", confidence: 4 },
    { date: "May 25", pain: 3, swelling: "none", confidence: 4 },
    { date: "May 26", pain: 5, swelling: "none", confidence: 3 },
  ],
  functionalTests: [
    {
      name: "Single leg hop",
      result: "92% symmetry",
      passed: true,
      recordedBy: "Dr. Avery Stone",
    },
    {
      name: "Ankle dorsiflexion",
      result: "Within 5 degrees",
      passed: true,
      recordedBy: "Dr. Avery Stone",
    },
  ],
  workloadSessions: [
    {
      activity: "Non-contact practice",
      duration: "30 min",
      intensity: "5 / 10",
      completed: true,
      symptomResponse: "No symptom increase during session.",
    },
    {
      activity: "Change-of-direction ladder",
      duration: "12 min",
      intensity: "6 / 10",
      completed: false,
      symptomResponse: "Symptom increase after session.",
    },
  ],
  readinessSignals: [
    {
      type: "Symptom worsening",
      severity: "moderate",
      message: "Review symptoms before advancing.",
      source: "Pain increased from 3 to 5 on May 26.",
    },
    {
      type: "Missing required milestone",
      severity: "blocker",
      message: "Required milestone missing.",
      source: "Pain remains below configured threshold.",
    },
    {
      type: "Clearance completeness",
      severity: "blocker",
      message: "Clearance decision required.",
      source: "Clinician decision has not been recorded.",
    },
  ],
};

export function getCaseDetail(caseId: string): CaseDetail {
  if (caseId === caseDetail.id) {
    return caseDetail;
  }
  return {
    ...caseDetail,
    id: caseId,
    athlete: athletes.find((athlete) => athlete.id === caseId) ?? athletes[0],
  };
}

export function getShareView(token: string): ShareView {
  return {
    token,
    audience: "coach",
    athleteName: "Riley Chen",
    sport: "Soccer",
    injuryTitle: "Left ankle sprain",
    currentPhase: "Restore motion",
    participationStatus: "Modified training only",
    allowedActivities: "Non-contact practice and assigned rehab work.",
    restrictedActivities: "No contact drills. No full-speed cutting.",
    nextReviewDate: "May 30",
    clearanceStatus: "Awaiting named clinician decision. This shared view is not medical clearance.",
    clinicianNote: "Next review after symptom check.",
  };
}
