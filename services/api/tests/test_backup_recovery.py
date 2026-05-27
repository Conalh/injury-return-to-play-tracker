from pathlib import Path


ROOT = Path(__file__).parents[3]


def test_backup_restore_scripts_are_guarded_and_drillable() -> None:
    backup = (ROOT / "scripts" / "backup" / "backup-postgres.ps1").read_text()
    restore = (ROOT / "scripts" / "backup" / "restore-postgres.ps1").read_text()
    drill = (ROOT / "scripts" / "backup" / "restore-drill.ps1").read_text()

    assert "pg_dump" in backup
    assert "--format plain" in backup
    assert "RESTORE return_play" in restore
    assert "DROP SCHEMA IF EXISTS public CASCADE" in restore
    assert "docker cp" in restore
    assert "restore_drill_marker" in drill
    assert "Restore drill passed." in drill


def test_backup_recovery_runbook_defines_targets_and_checklist() -> None:
    runbook = (ROOT / "docs" / "operations" / "backups-and-recovery.md").read_text()

    assert "RPO target: 24 hours" in runbook
    assert "RTO target: 4 hours" in runbook
    assert "Verification Checklist" in runbook
    assert "./scripts/backup/backup-postgres.ps1" in runbook
    assert "./scripts/backup/restore-postgres.ps1" in runbook
    assert "./scripts/backup/restore-drill.ps1" in runbook
    assert "Never store database backup files in git." in runbook


def test_ci_runs_restore_drill_and_git_ignores_backup_artifacts() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    gitignore = (ROOT / ".gitignore").read_text()

    assert "backup-restore-drill:" in workflow
    assert "Backup restore drill" in workflow
    assert "./scripts/backup/restore-drill.ps1" in workflow
    assert "backups/" in gitignore
