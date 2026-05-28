"use client";

import type { ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { useFormStatus } from "react-dom";

type PendingSubmitButtonProps = {
  className?: string;
  icon?: ReactNode;
  label: string;
  pendingLabel: string;
  tone?: "pine" | "gold" | "rust" | "outline";
};

export function PendingSubmitButton({
  className = "",
  icon,
  label,
  pendingLabel,
  tone = "pine",
}: PendingSubmitButtonProps) {
  const { pending } = useFormStatus();

  return (
    <button
      aria-live="polite"
      className={`rp-submit-button rp-submit-button-${tone} ${className}`}
      data-disables-while-pending="true"
      data-pending-label={pendingLabel}
      disabled={pending}
      type="submit"
    >
      {pending ? <Loader2 aria-hidden="true" className="rp-submit-spinner" /> : icon}
      <span>{pending ? pendingLabel : label}</span>
    </button>
  );
}
