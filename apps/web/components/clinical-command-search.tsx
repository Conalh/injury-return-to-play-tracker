"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  ClipboardList,
  FilePenLine,
  FileText,
  Plus,
  Search,
  ShieldCheck,
  Stethoscope,
  X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type CommandItem = {
  description: string;
  href: string;
  icon: LucideIcon;
  keywords: string;
  label: string;
  section: string;
};

const commandItems: CommandItem[] = [
  {
    description: "Open the active return-to-play case detail.",
    href: "/cases/case_demo",
    icon: ClipboardList,
    keywords: "riley chen soccer midfielder case ankle sprain active athlete",
    label: "Riley Chen case detail",
    section: "Athletes",
  },
  {
    description: "Jump to the evidence-entry panel for the demo case.",
    href: "/cases/case_demo#record-evidence",
    icon: Stethoscope,
    keywords: "record evidence symptoms functional test workload milestone riley chen",
    label: "Record evidence for Riley Chen",
    section: "Evidence",
  },
  {
    description: "Review readiness signals and clearance decision controls.",
    href: "/cases/case_demo#clearance",
    icon: ShieldCheck,
    keywords: "clearance decision hold advance named clinician riley chen",
    label: "Review clearance decision panel",
    section: "Decisions",
  },
  {
    description: "Create a new athlete and injury case.",
    href: "/cases/new",
    icon: Plus,
    keywords: "new case intake athlete injury create",
    label: "Create new case",
    section: "Workflow",
  },
  {
    description: "Create, version, and archive staged return-plan templates.",
    href: "/templates",
    icon: FileText,
    keywords: "templates plan phases milestones builder",
    label: "Open template builder",
    section: "Templates",
  },
  {
    description: "Download status, evidence, and audit metadata for Riley Chen.",
    href: "/cases/case_demo/report",
    icon: FilePenLine,
    keywords: "pdf report download audit evidence riley chen",
    label: "Download Riley Chen PDF report",
    section: "Reports",
  },
];

export function ClinicalCommandSearch() {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setIsOpen(true);
      }
      if (event.key === "Escape") {
        setIsOpen(false);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!isOpen) {
      setQuery("");
      return;
    }
    const frame = window.requestAnimationFrame(() => inputRef.current?.focus());
    return () => window.cancelAnimationFrame(frame);
  }, [isOpen]);

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return commandItems;
    }
    return commandItems.filter((item) => {
      const haystack = `${item.label} ${item.description} ${item.keywords}`.toLowerCase();
      return haystack.includes(normalizedQuery);
    });
  }, [query]);

  return (
    <>
      <span className="rp-tooltip-host rp-tooltip-bottom rp-search-tooltip">
        <button
          aria-haspopup="dialog"
          className="rp-search"
          onClick={() => setIsOpen(true)}
          type="button"
        >
          <Search aria-hidden="true" className="h-4 w-4" />
          <span>Search athletes, cases, or evidence</span>
          <kbd>Ctrl K</kbd>
        </button>
        <span className="rp-tooltip" role="tooltip">
          Search athletes, cases, or evidence across the clinical workspace
        </span>
      </span>

      {isOpen ? (
        <div className="rp-command-overlay" role="presentation">
          <div
            aria-label="Clinical command search"
            aria-modal="true"
            className="rp-command-dialog"
            role="dialog"
          >
            <div className="rp-command-search-row">
              <Search aria-hidden="true" className="h-4 w-4" />
              <input
                aria-label="Search command palette"
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search athletes, cases, evidence, or actions"
                ref={inputRef}
                role="searchbox"
                type="search"
                value={query}
              />
              <button
                aria-label="Close command search"
                className="rp-command-close"
                onClick={() => setIsOpen(false)}
                type="button"
              >
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
            </div>

            <div className="rp-command-results">
              {filteredItems.length > 0 ? (
                filteredItems.map((item) => (
                  <CommandLink item={item} key={`${item.section}-${item.label}`} />
                ))
              ) : (
                <p className="rp-command-empty">No matching clinical commands.</p>
              )}
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}

function CommandLink({ item }: { item: CommandItem }) {
  return (
    <Link className="rp-command-item" href={item.href}>
      <span className="rp-command-icon">
        <item.icon aria-hidden="true" className="h-4 w-4" />
      </span>
      <span>
        <span className="rp-command-label">{item.label}</span>
        <span className="rp-command-description">{item.description}</span>
      </span>
      <span className="rp-command-section">{item.section}</span>
    </Link>
  );
}
