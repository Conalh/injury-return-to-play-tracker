import type { CaseDetail } from "@/lib/demo-data";
import {
  attachMilestoneEvidenceAction,
  recordFunctionalTestAction,
  recordSymptomAction,
  recordWorkloadAction,
} from "@/app/(app)/cases/[id]/evidence-actions";
import { PendingSubmitButton } from "@/components/pending-submit-button";

type EvidenceEntryPanelProps = {
  caseId: string;
  athleteId: string;
  currentPhase: CaseDetail["phases"][number];
};

export function EvidenceEntryPanel({
  caseId,
  athleteId,
  currentPhase,
}: EvidenceEntryPanelProps) {
  return (
    <section className="rp-detail-card">
      <div className="rp-detail-card-header">
        <div>
          <h2>Record evidence</h2>
          <p>Symptoms, tests, workload, and milestone evidence for clinician review.</p>
        </div>
      </div>
      <div className="rp-entry-body">
        <SymptomForm caseId={caseId} athleteId={athleteId} />
        <FunctionalTestForm caseId={caseId} />
        <WorkloadForm caseId={caseId} />
        <MilestoneEvidenceForm caseId={caseId} milestones={currentPhase.milestones} />
      </div>
    </section>
  );
}

function SymptomForm({ caseId, athleteId }: { caseId: string; athleteId: string }) {
  return (
    <form action={recordSymptomAction} className="rp-subform">
      <input name="case_id" type="hidden" value={caseId} />
      <input name="athlete_id" type="hidden" value={athleteId} />
      <h3>Symptoms</h3>
      <div className="rp-form-grid rp-form-grid-2">
        <Field label="Symptom date" name="symptom_date" required type="date" />
        <Field label="Pain score" max={10} min={0} name="pain" required type="number" />
        <SelectField
          label="Swelling"
          name="swelling"
          options={[
            ["none", "None"],
            ["mild", "Mild"],
            ["moderate", "Moderate"],
            ["severe", "Severe"],
          ]}
        />
        <Field label="Confidence" max={5} min={1} name="confidence" required type="number" />
        <div className="rp-form-grid-full">
          <Field label="Symptom notes" multiline name="symptom_notes" />
        </div>
      </div>
      <PendingSubmitButton
        className="justify-self-start"
        label="Record symptoms"
        pendingLabel="Recording symptoms..."
      />
    </form>
  );
}

function FunctionalTestForm({ caseId }: { caseId: string }) {
  return (
    <form action={recordFunctionalTestAction} className="rp-subform">
      <input name="case_id" type="hidden" value={caseId} />
      <h3>Functional test</h3>
      <div className="rp-form-grid rp-form-grid-2">
        <Field label="Functional test name" name="functional_test_name" required />
        <Field label="Test date" name="test_date" required type="date" />
        <Field label="Result value" name="result_value" type="number" />
        <Field label="Result unit" name="unit" />
        <Field label="Side-to-side difference" name="side_difference" type="number" />
        <SelectField
          label="Functional test outcome"
          name="passed"
          options={[
            ["true", "Pass"],
            ["false", "Review"],
          ]}
        />
        <div className="rp-form-grid-full">
          <Field label="Functional test notes" multiline name="functional_test_notes" />
        </div>
      </div>
      <PendingSubmitButton
        className="justify-self-start"
        label="Record functional test"
        pendingLabel="Recording functional test..."
      />
    </form>
  );
}

function WorkloadForm({ caseId }: { caseId: string }) {
  return (
    <form action={recordWorkloadAction} className="rp-subform">
      <input name="case_id" type="hidden" value={caseId} />
      <h3>Workload session</h3>
      <div className="rp-form-grid rp-form-grid-2">
        <Field label="Workload date" name="workload_date" required type="date" />
        <Field label="Activity" name="activity" required />
        <Field label="Duration minutes" min={0} name="duration_minutes" required type="number" />
        <Field label="Intensity" max={10} min={1} name="intensity" required type="number" />
        <SelectField
          label="Completed"
          name="completed"
          options={[
            ["true", "Completed"],
            ["false", "Stopped early"],
          ]}
        />
        <Field label="Symptom response" name="symptom_response" />
        <div className="rp-form-grid-full">
          <Field label="Workload notes" multiline name="workload_notes" />
        </div>
      </div>
      <PendingSubmitButton
        className="justify-self-start"
        label="Record workload"
        pendingLabel="Recording workload..."
      />
    </form>
  );
}

function MilestoneEvidenceForm({
  caseId,
  milestones,
}: {
  caseId: string;
  milestones: CaseDetail["phases"][number]["milestones"];
}) {
  if (milestones.length === 0) {
    return null;
  }
  return (
    <form action={attachMilestoneEvidenceAction} className="rp-subform">
      <input name="case_id" type="hidden" value={caseId} />
      <h3>Milestone evidence</h3>
      <div className="rp-form-grid rp-form-grid-2">
        <SelectField
          label="Milestone"
          name="milestone_id"
          options={milestones.map((milestone, index) => [
            milestone.id,
            `Gate ${index + 1}: ${milestone.title}`,
          ])}
        />
        <SelectField
          label="Milestone status"
          name="milestone_status"
          options={[
            ["passed", "Passed"],
            ["failed", "Failed"],
            ["waived", "Waived"],
            ["not_started", "Not started"],
          ]}
        />
        <Field label="Evidence source" name="evidence_source" required />
        <Field label="Milestone notes" name="milestone_notes" />
      </div>
      <PendingSubmitButton
        className="justify-self-start"
        label="Attach milestone evidence"
        pendingLabel="Attaching milestone evidence..."
      />
    </form>
  );
}

function Field({
  label,
  name,
  type = "text",
  required = false,
  multiline = false,
  min,
  max,
}: {
  label: string;
  name: string;
  type?: string;
  required?: boolean;
  multiline?: boolean;
  min?: number;
  max?: number;
}) {
  return (
    <label className="rp-field">
      {label}
      {multiline ? (
        <textarea name={name} />
      ) : (
        <input max={max} min={min} name={name} required={required} type={type} />
      )}
    </label>
  );
}

function SelectField({
  label,
  name,
  options,
}: {
  label: string;
  name: string;
  options: string[][];
}) {
  return (
    <label className="rp-field">
      {label}
      <select name={name}>
        {options.map(([value, text]) => (
          <option key={value} value={value}>
            {text}
          </option>
        ))}
      </select>
    </label>
  );
}
