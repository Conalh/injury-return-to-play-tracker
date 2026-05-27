import { Activity, Ban, CalendarDays, CheckCircle2, HeartPulse, LockKeyhole, ShieldAlert } from "lucide-react";
import {
  submitAthleteSymptomCheckInAction,
  submitGuardianAcknowledgmentAction,
} from "@/app/share/[token]/actions";
import { ErrorState, UnauthorizedState } from "@/components/state-panels";
import { getSharePageData, UnauthorizedApiError } from "@/lib/api-client";

export default async function SharePage({
  params,
  searchParams,
}: {
  params: Promise<{ token: string }>;
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const { token } = await params;
  const query = await searchParams;
  const data = await loadSharePageData(token);
  if (data.status === "unauthorized") {
    return <UnauthorizedState />;
  }
  if (data.status === "error") {
    return (
      <ErrorState
        title="Share unavailable"
        body="This shared status view could not be loaded."
      />
    );
  }

  const { share, source } = data;
  if (share.audience === "athlete") {
    return (
      <AthletePortal
        checkInReceived={singleQueryValue(query.checkin) === "received"}
        share={share}
        source={source}
        token={token}
      />
    );
  }
  if (share.audience === "guardian") {
    return (
      <GuardianPortal
        acknowledgmentRecorded={singleQueryValue(query.acknowledgment) === "recorded"}
        share={share}
        source={source}
        token={token}
      />
    );
  }

  return (
    <main data-source={source} data-testid="share-view">
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

function AthletePortal({
  checkInReceived,
  share,
  source,
  token,
}: {
  checkInReceived: boolean;
  share: Awaited<ReturnType<typeof getSharePageData>>["share"];
  source: string;
  token: string;
}) {
  return (
    <main data-source={source} data-testid="share-view">
      <section className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">Athlete portal</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">{share.athleteName}</h1>
            <p className="mt-3 max-w-2xl text-base text-slate-600">
              Track today&apos;s assigned work and report symptoms for clinician review. This is not medical clearance.
            </p>
          </div>
          <div className="inline-flex min-h-10 items-center gap-2 bg-white px-3 py-2 text-sm font-semibold text-pine shadow-panel">
            <LockKeyhole aria-hidden="true" className="h-4 w-4" />
            Limited athlete view
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-4xl gap-5 px-4 pb-8 sm:px-6 lg:px-8">
        {checkInReceived ? (
          <p className="border border-pine/25 bg-pine/10 px-4 py-3 text-sm font-semibold text-pine">
            Symptom check-in received.
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          <StatusPanel
            icon={<Activity aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Current phase"
            body={share.currentPhase}
          />
          <StatusPanel
            icon={<CheckCircle2 aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Assigned activities"
            body={share.allowedActivities}
          />
          <StatusPanel
            icon={<CalendarDays aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Today's instructions"
            body={share.restrictedActivities}
          />
          <StatusPanel
            icon={<HeartPulse aria-hidden="true" className="h-5 w-5 text-rust" />}
            title="Clinician message"
            body={share.clinicianNote}
          />
        </div>

        <form action={submitAthleteSymptomCheckInAction} className="bg-white p-5 shadow-panel">
          <input name="token" type="hidden" value={token} />
          <h2 className="text-lg font-semibold text-ink">Symptom check-in</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <label className="block text-sm font-medium text-slate-700">
              Pain score
              <input className="mt-1 w-full border border-mist px-3 py-2" max="10" min="0" name="pain" required type="number" />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Swelling
              <select className="mt-1 w-full border border-mist px-3 py-2" name="swelling">
                <option value="none">None</option>
                <option value="mild">Mild</option>
                <option value="moderate">Moderate</option>
                <option value="severe">Severe</option>
              </select>
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Confidence
              <input className="mt-1 w-full border border-mist px-3 py-2" max="5" min="1" name="confidence" required type="number" />
            </label>
          </div>
          <label className="mt-3 block text-sm font-medium text-slate-700">
            Symptom notes
            <textarea className="mt-1 min-h-20 w-full border border-mist px-3 py-2" name="notes" />
          </label>
          <button className="mt-4 inline-flex min-h-10 items-center justify-center gap-2 bg-pine px-4 text-sm font-semibold text-white">
            <HeartPulse aria-hidden="true" className="h-4 w-4" />
            Submit symptom check-in
          </button>
        </form>
      </section>
    </main>
  );
}

function GuardianPortal({
  acknowledgmentRecorded,
  share,
  source,
  token,
}: {
  acknowledgmentRecorded: boolean;
  share: Awaited<ReturnType<typeof getSharePageData>>["share"];
  source: string;
  token: string;
}) {
  return (
    <main data-source={source} data-testid="share-view">
      <section className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-pine">Guardian portal</p>
            <h1 className="mt-2 text-3xl font-semibold text-ink sm:text-4xl">{share.athleteName}</h1>
            <p className="mt-3 max-w-2xl text-base text-slate-600">
              Conservative participation summary for family support. Clinical evidence and private case details are not included.
            </p>
          </div>
          <div className="inline-flex min-h-10 items-center gap-2 bg-white px-3 py-2 text-sm font-semibold text-pine shadow-panel">
            <LockKeyhole aria-hidden="true" className="h-4 w-4" />
            Limited guardian view
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-4xl gap-5 px-4 pb-8 sm:px-6 lg:px-8">
        {acknowledgmentRecorded ? (
          <p className="border border-pine/25 bg-pine/10 px-4 py-3 text-sm font-semibold text-pine">
            Guardian acknowledgment recorded.
          </p>
        ) : null}

        <div className="grid gap-4 md:grid-cols-2">
          <StatusPanel
            icon={<Activity aria-hidden="true" className="h-5 w-5 text-pine" />}
            title="Participation status"
            body={share.participationStatus}
          />
          <StatusPanel
            icon={<Ban aria-hidden="true" className="h-5 w-5 text-rust" />}
            title="Restrictions"
            body={share.restrictedActivities}
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
        </div>

        <div className="bg-ink p-5 text-white shadow-panel">
          <h2 className="text-lg font-semibold">Clinician note</h2>
          <p className="mt-2 text-sm text-white/75">{share.clinicianNote}</p>
          <p className="mt-4 text-sm text-white/75">
            This view is not medical clearance and does not include the full clinical record.
          </p>
        </div>

        <form action={submitGuardianAcknowledgmentAction} className="bg-white p-5 shadow-panel">
          <input name="token" type="hidden" value={token} />
          <h2 className="text-lg font-semibold text-ink">Guardian acknowledgment</h2>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <label className="block text-sm font-medium text-slate-700">
              Guardian name
              <input className="mt-1 w-full border border-mist px-3 py-2" name="acknowledged_by" required />
            </label>
            <label className="block text-sm font-medium text-slate-700">
              Relationship
              <input className="mt-1 w-full border border-mist px-3 py-2" name="relationship" required />
            </label>
          </div>
          <label className="mt-3 block text-sm font-medium text-slate-700">
            Acknowledgment note
            <textarea className="mt-1 min-h-20 w-full border border-mist px-3 py-2" name="message" />
          </label>
          <button className="mt-4 inline-flex min-h-10 items-center justify-center gap-2 bg-pine px-4 text-sm font-semibold text-white">
            <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
            Record acknowledgment
          </button>
        </form>
      </section>
    </main>
  );
}

async function loadSharePageData(token: string) {
  try {
    const data = await getSharePageData(token);
    return { status: "ok" as const, ...data };
  } catch (error) {
    if (error instanceof UnauthorizedApiError) {
      return { status: "unauthorized" as const };
    }
    return { status: "error" as const };
  }
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

function singleQueryValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}
