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
        "clinician_notes",
        "audit_log_entries",
        "share_tokens",
        "auth_token_revocations",
        "organization_audit_log_entries",
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


def test_goal_10_metadata_contains_runtime_persistence_columns() -> None:
    share_columns = Base.metadata.tables["share_tokens"].columns
    clearance_columns = Base.metadata.tables["clearance_decisions"].columns

    for column_name in [
        "created_at",
        "allowed_activities",
        "restricted_activities",
        "clinician_note",
        "next_review_date",
    ]:
        assert column_name in share_columns

    assert "decided_by_role" in clearance_columns


def test_goal_14_metadata_contains_user_admin_columns() -> None:
    user_columns = Base.metadata.tables["users"].columns
    organization_audit_columns = Base.metadata.tables["organization_audit_log_entries"].columns

    assert "active" in user_columns
    assert "organization_id" in organization_audit_columns
    assert "target_user_id" in organization_audit_columns
    assert "metadata_json" in organization_audit_columns


def test_goal_39_metadata_contains_auth_token_revocation_table() -> None:
    revocation_columns = Base.metadata.tables["auth_token_revocations"].columns

    assert "token_id_hash" in revocation_columns
    assert "actor_id" in revocation_columns
    assert "organization_id" in revocation_columns
    assert "expires_at" in revocation_columns
    assert "revoked_at" in revocation_columns
