from pathlib import Path


def test_goal_7_migration_adds_audit_log_table() -> None:
    migration = Path("alembic/versions/0003_goal_7_audit_log.py")

    assert migration.exists()

    migration_text = migration.read_text(encoding="utf-8")
    assert "create_table(" in migration_text
    assert '"audit_log_entries"' in migration_text
    assert '"event_type"' in migration_text
    assert '"metadata_json"' in migration_text
