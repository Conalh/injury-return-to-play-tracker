# Backups And Recovery

Status: Goal 31 data protection contract

The production data store is Postgres. Backups must be restorable, encrypted by
the storage provider, access-controlled, and periodically tested.

Never store database backup files in git.

## Strategy

- Run logical Postgres backups with `pg_dump` against the production database.
- Store backup artifacts outside the app host in provider-managed object
  storage or a managed database backup facility.
- Keep daily backups for at least 35 days before beta.
- Keep weekly backups for at least 12 weeks before production launch.
- Encrypt backups at rest and restrict restore permissions to named operators.
- Record every restore drill with date, operator, source backup, target
  environment, elapsed time, and result.

## Targets

- RPO target: 24 hours before beta; tighten after the first real customer risk
  review if the hosted database supports point-in-time recovery.
- RTO target: 4 hours for beta/staging; tighten before production launch after
  a timed restore drill.

## Local Commands

Create a backup from the compose Postgres service:

```powershell
./scripts/backup/backup-postgres.ps1
```

Restore a backup into the compose Postgres service:

```powershell
./scripts/backup/restore-postgres.ps1 `
  -BackupPath ./backups/return-play-YYYYMMDD-HHMMSS.sql `
  -ConfirmRestore "RESTORE return_play"
```

Run the automated local restore drill:

```powershell
./scripts/backup/restore-drill.ps1
```

The restore script is destructive. It drops and recreates the `public` schema in
the target database before applying the backup file.

## Verification Checklist

- Confirm the selected backup file is non-empty.
- Restore into a disposable local or staging database, never straight into
  production.
- Run migrations after restore if the backup is from an older schema version.
- Start the API against the restored database.
- Check `GET /health`, `GET /ready`, and `GET /metrics`.
- Seed only synthetic demo data when validating local/staging behavior.
- Confirm at least one restored table and row count expected by the drill.
- Record elapsed restore time against the RTO target.

## CI Drill

The `Backup restore drill` CI job starts the compose Postgres service, creates a
marker row, takes a logical backup, mutates the row, restores the backup, and
asserts the original marker value is back. This proves the backup and restore
commands are executable from a clean checkout.
