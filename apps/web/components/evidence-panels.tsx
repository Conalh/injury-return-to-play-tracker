import type { CaseDetail } from "@/lib/demo-data";

export function SymptomTrend({ symptomLogs }: Pick<CaseDetail, "symptomLogs">) {
  const maxPain = 10;
  return (
    <section className="rp-detail-card min-w-0">
      <div className="rp-detail-card-header">
        <div>
          <h2>Symptom trend</h2>
          <p>Pain score over recent logs</p>
        </div>
      </div>
      <div className="rp-symptom-chart">
        {symptomLogs.map((log) => (
          <div key={log.date} className="rp-symptom-bar">
            <div>
              <div
                className="rp-symptom-fill"
                style={{ height: `${Math.max(8, (log.pain / maxPain) * 100)}%` }}
                aria-hidden="true"
              />
            </div>
            <div>
              <strong>{log.pain}/10</strong>
              <div>{log.date}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

export function FunctionalTestTable({ functionalTests }: Pick<CaseDetail, "functionalTests">) {
  return (
    <section className="rp-detail-card min-w-0 overflow-hidden">
      <div className="rp-detail-card-header">
        <div>
          <h2>Functional tests</h2>
          <p>{functionalTests.length} recorded tests</p>
        </div>
      </div>
      <div
        aria-label="Functional test results"
        className="rp-functional-table-wrap"
        tabIndex={0}
      >
        <table className="rp-functional-table">
          <thead>
            <tr>
              <th>Test</th>
              <th>Result</th>
              <th>Status</th>
              <th>Recorded by</th>
            </tr>
          </thead>
          <tbody>
            {functionalTests.map((test) => (
              <tr key={test.name}>
                <td>{test.name}</td>
                <td>{test.result}</td>
                <td>{test.passed ? "Pass" : "Review"}</td>
                <td>{test.recordedBy}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function WorkloadProgression({ workloadSessions }: Pick<CaseDetail, "workloadSessions">) {
  return (
    <section className="rp-detail-card min-w-0">
      <div className="rp-detail-card-header">
        <div>
          <h2>Workload progression</h2>
          <p>Current activity tolerance</p>
        </div>
      </div>
      <div className="rp-workload-list">
        {workloadSessions.map((session) => (
          <div key={session.activity} className="rp-workload-item">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3>{session.activity}</h3>
                <p>{session.symptomResponse}</p>
              </div>
              <span>
                {session.duration} - {session.intensity}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
