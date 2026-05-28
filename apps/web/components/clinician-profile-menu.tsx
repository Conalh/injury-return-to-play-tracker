"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { ClipboardList, FileText, Settings, ShieldCheck, UserRound, X } from "lucide-react";

const workspaceLinks = [
  {
    description: "Adjust clinical workspace preferences and account details.",
    href: "/#workspace-settings",
    icon: Settings,
    label: "Open workspace settings",
  },
  {
    description: "Create, version, and archive staged return-plan templates.",
    href: "/templates",
    icon: FileText,
    label: "Open template management",
  },
  {
    description: "Review the active return-to-play case and readiness signals.",
    href: "/cases/case_demo",
    icon: ClipboardList,
    label: "Open Riley Chen case",
  },
  {
    description: "Download evidence, status, and audit metadata for the demo case.",
    href: "/cases/case_demo/report",
    icon: ShieldCheck,
    label: "Open Riley Chen report",
  },
];

export function ClinicianProfileMenu() {
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
    <span className="rp-profile-menu">
      <span className="rp-tooltip-host rp-tooltip-bottom">
        <button
          aria-haspopup="dialog"
          aria-label="Physician workspace menu"
          className="rp-role-chip"
          onClick={() => setIsOpen((current) => !current)}
          type="button"
        >
          Physician
        </button>
        <span className="rp-tooltip" role="tooltip">
          Open clinician profile and workspace tools
        </span>
      </span>

      {isOpen ? (
        <div
          aria-label="Clinician workspace menu"
          aria-modal="false"
          className="rp-profile-panel"
          role="dialog"
        >
          <div className="rp-profile-header">
            <span className="rp-profile-avatar" aria-hidden="true">
              AP
            </span>
            <span>
              <span className="rp-profile-name">Dr. Aanya Patel</span>
              <span className="rp-profile-role">Team Physician</span>
            </span>
            <button
              aria-label="Close clinician workspace menu"
              className="rp-command-close"
              onClick={() => setIsOpen(false)}
              ref={closeButtonRef}
              type="button"
            >
              <X aria-hidden="true" className="h-4 w-4" />
            </button>
          </div>

          <dl className="rp-profile-context" aria-label="Workspace context">
            <div>
              <dt>Organization</dt>
              <dd>Stagewise Athletic Medicine</dd>
            </div>
            <div>
              <dt>Session</dt>
              <dd>Demo environment</dd>
            </div>
          </dl>

          <div className="rp-profile-links">
            {workspaceLinks.map((item) => (
              <Link
                className="rp-profile-link"
                href={item.href}
                key={item.label}
                onClick={() => setIsOpen(false)}
              >
                <span className="rp-profile-link-icon">
                  <item.icon aria-hidden="true" className="h-4 w-4" />
                </span>
                <span>
                  <span className="rp-profile-link-label">{item.label}</span>
                  <span className="rp-profile-link-description">{item.description}</span>
                </span>
              </Link>
            ))}
          </div>

          <div className="rp-profile-footer">
            <UserRound aria-hidden="true" className="h-4 w-4" />
            <span>Signed in with clinician privileges</span>
          </div>
        </div>
      ) : null}
    </span>
  );
}
