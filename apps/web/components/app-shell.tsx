import Link from "next/link";
import {
  Activity,
  Bell,
  ClipboardList,
  FileText,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import { ClinicalCommandSearch } from "@/components/clinical-command-search";
import { Tooltip } from "@/components/ui-primitives";

const navSections = [
  {
    label: "Clinical",
    items: [
      { href: "/", label: "Dashboard", icon: LayoutDashboard },
      { href: "/", label: "Active cases", icon: ClipboardList, count: "8" },
      { href: "/", label: "Athletes", icon: Users, count: "142" },
      { href: "/", label: "Evidence queue", icon: Activity, count: "4" },
    ],
  },
  {
    label: "Decisions & access",
    items: [
      { href: "/", label: "Decision queue", icon: ShieldCheck, count: "2" },
      { href: "/templates", label: "Templates", icon: FileText },
    ],
  },
  {
    label: "Workspace",
    items: [{ href: "/", label: "Settings", icon: Settings }],
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="rp-shell">
      <a className="rp-skip-link" href="#clinical-workspace">
        Skip to clinical workspace
      </a>
      <aside className="rp-sidebar">
        <Link aria-label="Stagewise dashboard" className="rp-brand" href="/">
          <span className="rp-brand-mark">S</span>
          <span className="rp-brand-copy">
            <span className="rp-brand-name">Stagewise</span>
            <span className="rp-brand-tag">Athletic Medicine</span>
          </span>
        </Link>

        <nav aria-label="Primary clinical navigation" className="rp-nav">
          {navSections.map((section) => (
            <div className="rp-nav-section" key={section.label}>
              <div className="rp-nav-section-label">{section.label}</div>
              {section.items.map((item) => (
                <Link className="rp-nav-item" href={item.href} key={item.label}>
                  <item.icon aria-hidden="true" className="h-4 w-4" />
                  <span>{item.label}</span>
                  {item.count ? <span className="rp-nav-count">{item.count}</span> : null}
                </Link>
              ))}
            </div>
          ))}
        </nav>

        <div className="rp-sidebar-user">
          <span className="rp-user-avatar">AP</span>
          <span className="min-w-0">
            <span className="rp-user-name">Dr. Aanya Patel</span>
            <span className="rp-user-role">Team Physician</span>
          </span>
        </div>
      </aside>

      <div className="rp-main">
        <header className="rp-topbar">
          <div className="rp-crumbs">Clinical / Dashboard</div>
          <ClinicalCommandSearch />
          <div className="rp-topbar-actions">
            <Tooltip label="Review clinical notifications">
              <button aria-label="Notifications" className="rp-icon-button" type="button">
                <Bell aria-hidden="true" className="h-4 w-4" />
                <span className="rp-notification-dot" />
              </button>
            </Tooltip>
            <div className="rp-role-chip">Physician</div>
          </div>
        </header>
        <div className="rp-content" id="clinical-workspace" tabIndex={-1}>
          {children}
        </div>
      </div>
    </div>
  );
}
