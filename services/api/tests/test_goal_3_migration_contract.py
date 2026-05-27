from pathlib import Path


def test_goal_3_migration_adds_clinician_notes_table() -> None:
    migration = Path("alembic/versions/0002_goal_3_clinician_notes.py")

    assert migration.exists()

    migration_text = migration.read_text(encoding="utf-8")
    assert "create_table(" in migration_text
    assert '"clinician_notes"' in migration_text
    assert '"injury_case_id"' in migration_text
    assert '"author_id"' in migration_text
    assert '"body"' in migration_text
