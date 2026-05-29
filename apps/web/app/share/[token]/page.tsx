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
    <main className="rp-share-page" data-source={source} data-testid="share-view">
      <header className="rp-share-header">
        <div>
          <p className="rp-share-kicker">Coach status view</p>
          <h1 className="rp-share-title">{share.athleteName}</h1>
          <p className="rp-share-lead">
            Limited participation summary for {share.sport}. Clinical details and private notes are not included in this view.
          </p>
        </div>
        <span className="rp-share-pill">
          <LockKeyhole aria-hidden="true" className="h-4 w-4" />
          Limited share
        </span>
      </header>

      <section className="rp-share-card">
        <ShieldAlert aria-hidden="true" className="mt-0.5 h-5 w-5 text-[var(--rp-bad-fg)]" />
        <div>
          <h2>{share.injuryTitle}</h2>
          <p>{share.currentPhase}</p>
        </div>
      </section>

      <section className="rp-share-grid rp-share-grid-2">
        <StatusPanel
          icon={<Activity aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Participation status"
          body={share.participationStatus}
        />
        <StatusPanel
          icon={<CalendarDays aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Next review"
          body={share.nextReviewDate}
        />
        <StatusPanel
          icon={<CheckCircle2 aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Allowed activities"
          body={share.allowedActivities}
        />
        <StatusPanel
          icon={<Ban aria-hidden="true" className="h-5 w-5 text-[var(--rp-bad-fg)]" />}
          title="Restricted activities"
          body={share.restrictedActivities}
        />
      </section>

      <section className="rp-share-clearance">
        <h2>Clearance status</h2>
        <p>{share.clearanceStatus}</p>
        <div className="rp-share-clearance-note">
          <p>Clinician note</p>
          <p>{share.clinicianNote}</p>
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
    <main className="rp-share-page" data-source={source} data-testid="share-view">
      <header className="rp-share-header">
        <div>
          <p className="rp-share-kicker">Athlete portal</p>
          <h1 className="rp-share-title">{share.athleteName}</h1>
          <p className="rp-share-lead">
            Track today&apos;s assigned work and report symptoms for clinician review. This is not medical clearance.
          </p>
        </div>
        <span className="rp-share-pill">
          <LockKeyhole aria-hidden="true" className="h-4 w-4" />
          Limited athlete view
        </span>
      </header>

      {checkInReceived ? (
        <p className="rp-share-notice">Symptom check-in received.</p>
      ) : null}

      <section className="rp-share-grid rp-share-grid-2">
        <StatusPanel
          icon={<Activity aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Current phase"
          body={share.currentPhase}
        />
        <StatusPanel
          icon={<CheckCircle2 aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Assigned activities"
          body={share.allowedActivities}
        />
        <StatusPanel
          icon={<CalendarDays aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Today's instructions"
          body={share.restrictedActivities}
        />
        <StatusPanel
          icon={<HeartPulse aria-hidden="true" className="h-5 w-5 text-[var(--rp-bad-fg)]" />}
          title="Clinician message"
          body={share.clinicianNote}
        />
      </section>

      <form action={submitAthleteSymptomCheckInAction} className="rp-share-form">
        <input name="token" type="hidden" value={token} />
        <h2>Symptom check-in</h2>
        <div className="rp-share-fields rp-share-fields-3">
          <label className="rp-field">
            Pain score
            <input max="10" min="0" name="pain" required type="number" />
          </label>
          <label className="rp-field">
            Swelling
            <select name="swelling">
              <option value="none">None</option>
              <option value="mild">Mild</option>
              <option value="moderate">Moderate</option>
              <option value="severe">Severe</option>
            </select>
          </label>
          <label className="rp-field">
            Confidence
            <input max="5" min="1" name="confidence" required type="number" />
          </label>
        </div>
        <label className="rp-field">
          Symptom notes
          <textarea name="notes" />
        </label>
        <button className="rp-submit-button rp-submit-button-pine" type="submit">
          <HeartPulse aria-hidden="true" className="h-4 w-4" />
          Submit symptom check-in
        </button>
      </form>
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
    <main className="rp-share-page" data-source={source} data-testid="share-view">
      <header className="rp-share-header">
        <div>
          <p className="rp-share-kicker">Guardian portal</p>
          <h1 className="rp-share-title">{share.athleteName}</h1>
          <p className="rp-share-lead">
            Conservative participation summary for family support. Clinical evidence and private case details are not included.
          </p>
        </div>
        <span className="rp-share-pill">
          <LockKeyhole aria-hidden="true" className="h-4 w-4" />
          Limited guardian view
        </span>
      </header>

      {acknowledgmentRecorded ? (
        <p className="rp-share-notice">Guardian acknowledgment recorded.</p>
      ) : null}

      <section className="rp-share-grid rp-share-grid-2">
        <StatusPanel
          icon={<Activity aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Participation status"
          body={share.participationStatus}
        />
        <StatusPanel
          icon={<Ban aria-hidden="true" className="h-5 w-5 text-[var(--rp-bad-fg)]" />}
          title="Restrictions"
          body={share.restrictedActivities}
        />
        <StatusPanel
          icon={<CalendarDays aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Next review"
          body={share.nextReviewDate}
        />
        <StatusPanel
          icon={<CheckCircle2 aria-hidden="true" className="h-5 w-5 text-[var(--rp-accent)]" />}
          title="Allowed activities"
          body={share.allowedActivities}
        />
      </section>

      <section className="rp-share-clearance">
        <h2>Clinician note</h2>
        <p>{share.clinicianNote}</p>
        <p>This view is not medical clearance and does not include the full clinical record.</p>
      </section>

      <form action={submitGuardianAcknowledgmentAction} className="rp-share-form">
        <input name="token" type="hidden" value={token} />
        <h2>Guardian acknowledgment</h2>
        <div className="rp-share-fields rp-share-fields-2">
          <label className="rp-field">
            Guardian name
            <input name="acknowledged_by" required />
          </label>
          <label className="rp-field">
            Relationship
            <input name="relationship" required />
          </label>
        </div>
        <label className="rp-field">
          Acknowledgment note
          <textarea name="message" />
        </label>
        <button className="rp-submit-button rp-submit-button-pine" type="submit">
          <CheckCircle2 aria-hidden="true" className="h-4 w-4" />
          Record acknowledgment
        </button>
      </form>
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
    <div className="rp-share-stat">
      {icon}
      <div>
        <h2>{title}</h2>
        <p>{body}</p>
      </div>
    </div>
  );
}

function singleQueryValue(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}
