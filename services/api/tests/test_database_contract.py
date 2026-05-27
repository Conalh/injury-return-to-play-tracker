from return_play.db import Base


def test_metadata_contains_goal_2_tables() -> None:
    expected_tables = {
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
    }

    assert expected_tables.issubset(set(Base.metadata.tables))


def test_tenant_scoped_tables_include_organization_id() -> None:
    tenant_tables = [
        "users",
        "athletes",
        "injury_cases",
        "return_plan_templates",
    ]

    for table_name in tenant_tables:
        assert "organization_id" in Base.metadata.tables[table_name].columns
