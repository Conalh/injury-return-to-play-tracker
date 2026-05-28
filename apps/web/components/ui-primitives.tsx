import type { ReactNode } from "react";

type ClinicalCardProps = {
  ariaLabel?: string;
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  id?: string;
};

export function ClinicalCard({
  ariaLabel,
  action,
  children,
  className = "",
  id,
  subtitle,
  title,
}: ClinicalCardProps) {
  return (
    <section aria-label={ariaLabel} className={`rp-card ${className}`} id={id}>
      {title || action ? (
        <div className="rp-card-header">
          <div className="min-w-0">
            {title ? <h2 className="rp-card-title">{title}</h2> : null}
            {subtitle ? <p className="rp-card-subtitle">{subtitle}</p> : null}
          </div>
          {action ? <div className="rp-card-action">{action}</div> : null}
        </div>
      ) : null}
      <div className="rp-card-body">{children}</div>
    </section>
  );
}

export function Tooltip({
  children,
  className = "",
  label,
  side = "bottom",
}: {
  children: ReactNode;
  className?: string;
  label: string;
  side?: "top" | "bottom";
}) {
  return (
    <span className={`rp-tooltip-host rp-tooltip-${side} ${className}`}>
      {children}
      <span className="rp-tooltip" role="tooltip">
        {label}
      </span>
    </span>
  );
}

export function ClinicalBadge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "ok" | "warn" | "bad" | "info" | "hold";
}) {
  return (
    <span className={`rp-badge rp-badge-${tone}`}>
      <span className="rp-badge-dot" />
      {children}
    </span>
  );
}

export function AthleteAvatar({ id, name, size = "md" }: { id: string; name: string; size?: "sm" | "md" | "lg" }) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  return (
    <span className={`rp-avatar rp-avatar-${size}`} data-athlete-id={id}>
      {initials}
    </span>
  );
}
