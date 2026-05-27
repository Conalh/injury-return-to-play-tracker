from pathlib import Path


def test_baseline_migration_creates_goal_2_tables() -> None:
    migration = Path("alembic/versions/0001_goal_2_backend_schema.py")

    assert migration.exists()

    migration_text = migration.read_text(encoding="utf-8")
    for table_name in [
        "organizations",
        "users",
        "athletes",
        "injury_cases",
        "return_plan_templates",
        "return_plan_phases",
        "milestones",
        "case_phase_statuses",
        "milestone_results",
        "symptom_logs",
        "functional_tests",
        "workload_sessions",
        "clearance_decisions",
        "share_tokens",
    ]:
        assert "create_table(" in migration_text
        assert f'"{table_name}"' in migration_text
