import { Activity, Ban, CalendarDays, CheckCircle2, LockKeyhole, ShieldAlert } from "lucide-react";
import { getShareView } from "@/lib/demo-data";

export default async function SharePage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  const share = getShareView(token);

  return (
    <main>
      <section className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">Coach status view</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">{share.athleteName}</h1>
            <p className="mt-3 max-w-2xl text-base text-slate-600">
              Limited participation summary for {share.sport}. Clinical details and private notes are not included in this view.
            </p>
          </div>
          <div className="inline-flex min-h-10 items-center gap-2 bg-white px-3 py-2 text-sm font-semibold text-pine shadow-panel">
            <LockKeyhole aria-hidden="true" className="h-4 w-4" />
            Limited share
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-4xl gap-5 px-4 pb-8 sm:px-6 lg:px-8">
        <div className="bg-white p-5 shadow-panel">
          <div className="flex gap-3">
            <ShieldAlert aria-hidden="true" className="mt-0.5 h-5 w-5 text-rust" />
            <div>
              <h2 className="text-lg font-semibold text-ink">{share.injuryTitle}</h2>
              <p className="mt-1 text-sm text-slate-600">{share.currentPhase}</p>
            </div>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <StatusPanel
            icon={<Activity aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Participation status"
            body={share.participationStatus}
          />
          <StatusPanel
            icon={<CalendarDays aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Next review"
            body={share.nextReviewDate}
          />
          <StatusPanel
            icon={<CheckCircle2 aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Allowed activities"
            body={share.allowedActivities}
          />
          <StatusPanel
            icon={<Ban aria-hidden="true" className="h-5 w-5 text-rust" />}
            title="Restricted activities"
            body={share.restrictedActivities}
          />
        </div>

        <div className="bg-ink p-5 text-white shadow-panel">
          <h2 className="text-lg font-semibold">Clearance status</h2>
          <p className="mt-2 text-sm text-white/75">{share.clearanceStatus}</p>
          <div className="mt-5 border border-white/15 bg-white/5 p-4">
            <p className="text-sm font-semibold">Clinician note</p>
            <p className="mt-1 text-sm text-white/75">{share.clinicianNote}</p>
          </div>
        </div>
      </section>
    </main>
  );
}

function StatusPanel({
  icon,
  title,
  body,
}: {
  icon: React.ReactNode;
  title: string;
  body: string;
}) {
  return (
    <div className="bg-white p-5 shadow-panel">
      <div className="flex gap-3">
        {icon}
        <div>
          <h2 className="text-sm font-semibold text-slate-500">{title}</h2>
          <p className="mt-1 font-semibold text-ink">{body}</p>
        </div>
      </div>
    </div>
  );
}
