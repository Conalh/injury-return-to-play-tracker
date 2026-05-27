import type { ReactNode } from "react";

type ClinicalCardProps = {
  title?: string;
  subtitle?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
};

export function ClinicalCard({
  action,
  children,
  className = "",
  subtitle,
  title,
}: ClinicalCardProps) {
  return (
    <section className={`rp-card ${className}`}>
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
