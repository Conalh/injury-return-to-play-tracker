import { AlertTriangle, LockKeyhole } from "lucide-react";

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <section className="border-y border-mist bg-white">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <h2 className="text-lg font-semibold text-ink">{title}</h2>
        <p className="mt-2 max-w-2xl text-sm text-slate-600">{body}</p>
      </div>
    </section>
  );
}

export function ErrorState({ title, body }: { title: string; body: string }) {
  return (
    <section className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="border border-rust/30 bg-white p-5 shadow-panel">
        <div className="flex gap-3">
          <AlertTriangle aria-hidden="true" className="mt-0.5 h-5 w-5 text-rust" />
          <div>
            <h2 className="text-lg font-semibold text-ink">{title}</h2>
            <p className="mt-2 text-sm text-slate-600">{body}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export function UnauthorizedState() {
  return (
    <section className="mx-auto max-w-4xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="border border-mist bg-white p-5 shadow-panel">
        <div className="flex gap-3">
          <LockKeyhole aria-hidden="true" className="mt-0.5 h-5 w-5 text-pine" />
          <div>
            <h2 className="text-lg font-semibold text-ink">Access unavailable</h2>
            <p className="mt-2 text-sm text-slate-600">
              Your current session cannot access this return-to-play workspace.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
