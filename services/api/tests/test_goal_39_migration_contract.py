from pathlib import Path


def test_goal_39_migration_adds_auth_token_revocations() -> None:
    migration = Path("alembic/versions/0006_goal_39_auth_token_revocations.py")

    assert migration.exists()

    migration_text = migration.read_text(encoding="utf-8")
    assert 'revision: str = "0006_goal_39"' in migration_text
    assert 'down_revision: Union[str, None] = "0005_goal_14"' in migration_text
    assert '"auth_token_revocations"' in migration_text
    assert '"token_id_hash"' in migration_text
    assert '"expires_at"' in migration_text
    assert '"revoked_at"' in migration_text
