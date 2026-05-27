import { CheckCircle2, Clock3, LockKeyhole, OctagonAlert } from "lucide-react";

type StatusBadgeProps = {
  status: string;
};

const styles: Record<string, string> = {
  current: "border-pine/25 bg-pine/10 text-pine",
  passed: "border-emerald-700/25 bg-emerald-700/10 text-emerald-800",
  locked: "border-slate-400/30 bg-slate-200 text-slate-700",
  held: "border-rust/25 bg-rust/10 text-rust",
  not_started: "border-slate-400/30 bg-slate-100 text-slate-700",
  failed: "border-rust/25 bg-rust/10 text-rust",
  waived: "border-gold/25 bg-gold/10 text-amber-800",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const Icon =
    status === "passed"
      ? CheckCircle2
      : status === "locked"
        ? LockKeyhole
        : status === "failed" || status === "held"
          ? OctagonAlert
          : Clock3;

  return (
    <span
      className={`inline-flex min-h-7 items-center gap-1.5 rounded-full border px-2.5 text-xs font-semibold ${styles[status] ?? styles.not_started}`}
    >
      <Icon aria-hidden="true" className="h-3.5 w-3.5" />
      {status.replace("_", " ")}
    </span>
  );
}
