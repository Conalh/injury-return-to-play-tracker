import { CheckCircle2, Clock3, LockKeyhole, OctagonAlert } from "lucide-react";

type StatusBadgeProps = {
  status: string;
};

const tones: Record<string, string> = {
  current: "rp-badge-info",
  passed: "rp-badge-ok",
  locked: "rp-badge-neutral",
  held: "rp-badge-hold",
  not_started: "rp-badge-neutral",
  failed: "rp-badge-bad",
  waived: "rp-badge-warn",
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
    <span className={`rp-badge ${tones[status] ?? tones.not_started}`}>
      <Icon aria-hidden="true" className="h-3.5 w-3.5" />
      {status.replace("_", " ")}
    </span>
  );
}
