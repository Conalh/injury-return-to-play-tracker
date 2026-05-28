"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { AlertTriangle, Bell, ClipboardCheck, X } from "lucide-react";

type NotificationItem = {
  description: string;
  href: string;
  label: string;
  tone: "warn" | "bad" | "info";
};

const notifications: NotificationItem[] = [
  {
    description: "Riley Chen has symptom flags that need clinician review before phase advancement.",
    href: "/cases/case_demo#overview",
    label: "Review symptoms before advancing",
    tone: "bad",
  },
  {
    description: "Workload sessions are not yet complete for the current phase.",
    href: "/cases/case_demo#record-evidence",
    label: "Workload progression incomplete",
    tone: "warn",
  },
  {
    description: "One required milestone remains below the configured evidence threshold.",
    href: "/cases/case_demo#record-evidence",
    label: "Required milestone missing",
    tone: "info",
  },
];

export function ClinicalNotifications() {
  const [isOpen, setIsOpen] = useState(false);
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!isOpen) {
      return;
    }
    const frame = window.requestAnimationFrame(() => closeButtonRef.current?.focus());
    return () => window.cancelAnimationFrame(frame);
  }, [isOpen]);

  return (
    <span className="rp-notifications">
      <span className="rp-tooltip-host rp-tooltip-bottom">
        <button
          aria-haspopup="dialog"
          aria-label="Notifications"
          className="rp-icon-button"
          onClick={() => setIsOpen((current) => !current)}
          type="button"
        >
          <Bell aria-hidden="true" className="h-4 w-4" />
          <span className="rp-notification-dot" />
        </button>
        <span className="rp-tooltip" role="tooltip">
          Review clinical notifications
        </span>
      </span>

      {isOpen ? (
        <div
          aria-label="Clinical notifications"
          aria-modal="false"
          className="rp-notifications-panel"
          role="dialog"
        >
          <div className="rp-notifications-header">
            <div>
              <h2>Clinical notifications</h2>
              <p>{notifications.length} open clinical alerts</p>
            </div>
            <button
              aria-label="Close clinical notifications"
              className="rp-command-close"
              onClick={() => setIsOpen(false)}
              ref={closeButtonRef}
              type="button"
            >
              <X aria-hidden="true" className="h-4 w-4" />
            </button>
          </div>

          <div className="rp-notification-list">
            {notifications.map((notification) => (
              <Link
                className="rp-notification-item"
                href={notification.href}
                key={notification.label}
                onClick={() => setIsOpen(false)}
              >
                <span className={`rp-notification-icon rp-notification-icon-${notification.tone}`}>
                  {notification.tone === "info" ? (
                    <ClipboardCheck aria-hidden="true" className="h-4 w-4" />
                  ) : (
                    <AlertTriangle aria-hidden="true" className="h-4 w-4" />
                  )}
                </span>
                <span>
                  <span className="rp-notification-label">{notification.label}</span>
                  <span className="rp-notification-description">{notification.description}</span>
                </span>
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </span>
  );
}
