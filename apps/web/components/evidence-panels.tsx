import type { CaseDetail } from "@/lib/demo-data";

export function SymptomTrend({ symptomLogs }: Pick<CaseDetail, "symptomLogs">) {
  const maxPain = 10;
  return (
    <section className="min-w-0 bg-white px-4 py-5 shadow-panel sm:px-5">
      <h2 className="text-base font-semibold text-ink">Symptom trend</h2>
      <div className="mt-4 flex h-32 items-end gap-3">
        {symptomLogs.map((log) => (
          <div key={log.date} className="flex flex-1 flex-col items-center gap-2">
            <div className="flex h-24 w-full items-end bg-field">
              <div
                className="w-full bg-rust"
                style={{ height: `${Math.max(8, (log.pain / maxPain) * 100)}%` }}
                aria-label={`${log.date} pain ${log.pain}`}
              />
            </div>
            <div className="text-center text-xs text-slate-600">
              <div className="font-semibold text-ink">{log.pain}/10</div>
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
    <section className="min-w-0 overflow-hidden bg-white px-4 py-5 shadow-panel sm:px-5">
      <h2 className="text-base font-semibold text-ink">Functional tests</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full table-fixed text-left text-sm">
          <thead>
            <tr className="border-b border-mist text-xs uppercase tracking-wide text-slate-500">
              <th className="w-[44%] py-2 pr-3">Test</th>
              <th className="w-[34%] px-3 py-2">Result</th>
              <th className="w-[22%] px-3 py-2">Status</th>
              <th className="hidden py-2 pl-3 sm:table-cell">Recorded by</th>
            </tr>
          </thead>
          <tbody>
            {functionalTests.map((test) => (
              <tr key={test.name} className="border-b border-mist/70 last:border-0">
                <td className="py-3 pr-3 font-medium text-ink">{test.name}</td>
                <td className="break-words px-3 py-3 text-slate-700">{test.result}</td>
                <td className="px-3 py-3 text-slate-700">{test.passed ? "Pass" : "Review"}</td>
                <td className="hidden py-3 pl-3 text-slate-700 sm:table-cell">{test.recordedBy}</td>
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
    <section className="min-w-0 bg-white px-4 py-5 shadow-panel sm:px-5">
      <h2 className="text-base font-semibold text-ink">Workload progression</h2>
      <div className="mt-4 grid gap-3">
        {workloadSessions.map((session) => (
          <div key={session.activity} className="border border-mist bg-field p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="font-semibold text-ink">{session.activity}</h3>
                <p className="mt-1 text-sm text-slate-600">{session.symptomResponse}</p>
              </div>
              <span className="whitespace-nowrap text-xs font-semibold text-slate-600">
                {session.duration} · {session.intensity}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
