from pathlib import Path


def test_goal_14_migration_adds_user_admin_persistence() -> None:
    migration = Path("alembic/versions/0005_goal_14_user_admin.py")

    assert migration.exists()

    migration_text = migration.read_text(encoding="utf-8")
    assert 'revision: str = "0005_goal_14"' in migration_text
    assert 'down_revision: Union[str, None] = "0004_goal_10"' in migration_text
    assert '"active"' in migration_text
    assert '"organization_audit_log_entries"' in migration_text
    assert '"target_user_id"' in migration_text
