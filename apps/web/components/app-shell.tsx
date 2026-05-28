import Link from "next/link";
import { ClinicalCommandSearch } from "@/components/clinical-command-search";
import { ClinicalNotifications } from "@/components/clinical-notifications";
import { ClinicianProfileMenu } from "@/components/clinician-profile-menu";
import { ShellBreadcrumbs, ShellNavigation } from "@/components/shell-navigation";

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

        <ShellNavigation />

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
          <ShellBreadcrumbs />
          <ClinicalCommandSearch />
          <div className="rp-topbar-actions">
            <ClinicalNotifications />
            <ClinicianProfileMenu />
          </div>
        </header>
        <div className="rp-content" id="clinical-workspace" tabIndex={-1}>
          {children}
        </div>
      </div>
    </div>
  );
}
