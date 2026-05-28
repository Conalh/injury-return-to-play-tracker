"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import {
  Activity,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

type NavItem = {
  href: string;
  icon: LucideIcon;
  label: string;
};

type NavSection = {
  items: NavItem[];
  label: string;
};

const navSections: NavSection[] = [
  {
    label: "Clinical",
    items: [
      { href: "/", label: "Dashboard", icon: LayoutDashboard },
      { href: "/#active-cases", label: "Active cases", icon: ClipboardList },
      { href: "/#athlete-roster", label: "Athletes", icon: Users },
      { href: "/#evidence-queue", label: "Evidence queue", icon: Activity },
    ],
  },
  {
    label: "Decisions & access",
    items: [
      { href: "/#decision-queue", label: "Decision queue", icon: ShieldCheck },
      { href: "/templates", label: "Templates", icon: FileText },
    ],
  },
  {
    label: "Workspace",
    items: [{ href: "/#workspace-settings", label: "Settings", icon: Settings }],
  },
];

const dashboardBreadcrumbs: Record<string, string> = {
  "#active-cases": "Clinical / Active cases",
  "#athlete-roster": "Clinical / Athletes",
  "#decision-queue": "Decisions & access / Decision queue",
  "#evidence-queue": "Clinical / Evidence queue",
  "#workspace-settings": "Workspace / Settings",
};

export function ShellBreadcrumbs() {
  const pathname = usePathname();
  const hash = useLocationHash();

  return (
    <div aria-label="Workspace breadcrumb" className="rp-crumbs">
      {getBreadcrumb(pathname, hash)}
    </div>
  );
}

export function ShellNavigation() {
  const pathname = usePathname();
  const hash = useLocationHash();

  return (
    <nav aria-label="Primary clinical navigation" className="rp-nav">
      {navSections.map((section) => (
        <div className="rp-nav-section" key={section.label}>
          <div className="rp-nav-section-label">{section.label}</div>
          {section.items.map((item) => {
            const current = getAriaCurrent(item.href, pathname, hash);
            return (
              <Link
                aria-current={current}
                className="rp-nav-item"
                href={item.href}
                key={item.label}
              >
                <item.icon aria-hidden="true" className="h-4 w-4" />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      ))}
    </nav>
  );
}

function getAriaCurrent(href: string, pathname: string, hash: string) {
  if (href === "/") {
    return pathname === "/" && !hash ? "page" : undefined;
  }
  if (href === "/templates") {
    return pathname.startsWith("/templates") ? "page" : undefined;
  }
  if (href === "/#active-cases" && pathname.startsWith("/cases")) {
    return "page";
  }
  if (href.startsWith("/#")) {
    return pathname === "/" && hash === href.slice(1) ? "location" : undefined;
  }
  return undefined;
}

function getBreadcrumb(pathname: string, hash: string) {
  if (pathname === "/" && hash) {
    return dashboardBreadcrumbs[hash] ?? "Clinical / Dashboard";
  }
  if (pathname === "/") {
    return "Clinical / Dashboard";
  }
  if (pathname === "/cases/new") {
    return "Clinical / New case";
  }
  if (pathname.startsWith("/cases/")) {
    return "Clinical / Case detail";
  }
  if (pathname.startsWith("/templates")) {
    return "Decisions & access / Templates";
  }
  if (pathname.startsWith("/share/")) {
    return "Shared access / Limited view";
  }
  return "Clinical workspace";
}

function useLocationHash() {
  const [hash, setHash] = useState("");

  useEffect(() => {
    function syncHash() {
      setHash(window.location.hash);
    }

    function syncHashAfterNavigation(event: MouseEvent) {
      const target = event.target instanceof Element ? event.target.closest("a[href*='#']") : null;
      if (!target) {
        return;
      }
      window.setTimeout(syncHash, 0);
      window.setTimeout(syncHash, 50);
    }

    syncHash();
    const interval = window.setInterval(syncHash, 100);
    document.addEventListener("click", syncHashAfterNavigation);
    window.addEventListener("hashchange", syncHash);
    window.addEventListener("popstate", syncHash);
    return () => {
      window.clearInterval(interval);
      document.removeEventListener("click", syncHashAfterNavigation);
      window.removeEventListener("hashchange", syncHash);
      window.removeEventListener("popstate", syncHash);
    };
  }, []);

  return hash;
}
