import { AlertTriangle, LockKeyhole } from "lucide-react";

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <section className="rp-state">
      <div className="rp-state-card">
        <div>
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
      </div>
    </section>
  );
}

export function ErrorState({ title, body }: { title: string; body: string }) {
  return (
    <section className="rp-state">
      <div className="rp-state-card rp-state-card-error">
        <AlertTriangle aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-[var(--rp-bad-fg)]" />
        <div>
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
      </div>
    </section>
  );
}

export function UnauthorizedState() {
  return (
    <section className="rp-state">
      <div className="rp-state-card">
        <LockKeyhole aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-[var(--rp-accent)]" />
        <div>
          <h2>Access unavailable</h2>
          <p>Your current session cannot access this return-to-play workspace.</p>
        </div>
      </div>
    </section>
  );
}
