from pathlib import Path


def test_goal_10_migration_adds_runtime_persistence_columns() -> None:
    migration = Path("alembic/versions/0004_goal_10_persistence_columns.py")

    assert migration.exists()

    migration_text = migration.read_text(encoding="utf-8")
    assert 'revision: str = "0004_goal_10"' in migration_text
    assert 'down_revision: Union[str, None] = "0003_goal_7"' in migration_text
    assert '"decided_by_role"' in migration_text
    assert '"allowed_activities"' in migration_text
    assert '"restricted_activities"' in migration_text
    assert '"clinician_note"' in migration_text
    assert '"next_review_date"' in migration_text
