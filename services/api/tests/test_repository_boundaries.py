from return_play.repositories import InMemoryWorkflowRepository, SqlAlchemyWorkflowRepository
from return_play.repositories.athletes import AthleteRepositoryBoundary
from return_play.repositories.cases import CaseRepositoryBoundary
from return_play.repositories.demo import DemoSeedService
from return_play.repositories.evidence import EvidenceRepositoryBoundary
from return_play.repositories.readiness import ReadinessRepositoryBoundary
from return_play.repositories.sharing import SharingReportingAuditRepositoryBoundary
from return_play.repositories.templates import TemplatePlanRepositoryBoundary


BOUNDARY_METHODS = {
    AthleteRepositoryBoundary: {"create_athlete", "list_athletes"},
    CaseRepositoryBoundary: {
        "create_injury_case",
        "get_injury_case_detail",
        "list_case_phases",
        "update_milestone",
        "create_note",
        "create_clearance_decision",
    },
    TemplatePlanRepositoryBoundary: {"create_template", "list_templates", "apply_template"},
    EvidenceRepositoryBoundary: {
        "create_symptom_log",
        "list_symptom_logs",
        "create_functional_test",
        "list_functional_tests",
        "create_workload_session",
        "list_workload_sessions",
    },
    ReadinessRepositoryBoundary: {"get_readiness"},
    SharingReportingAuditRepositoryBoundary: {
        "create_share",
        "get_share",
        "revoke_share",
        "build_report",
        "get_audit_log",
    },
}


def test_repository_boundary_modules_define_the_workflow_surface() -> None:
    for boundary, methods in BOUNDARY_METHODS.items():
        assert methods <= set(boundary.__dict__)


def test_runtime_repositories_implement_each_boundary() -> None:
    for repository_class in (InMemoryWorkflowRepository, SqlAlchemyWorkflowRepository):
        for methods in BOUNDARY_METHODS.values():
            for method in methods:
                assert hasattr(repository_class, method)


def test_legacy_repository_imports_remain_compatible() -> None:
    from return_play.repository import InMemoryWorkflowRepository as LegacyInMemory
    from return_play.sql_repository import SqlAlchemyWorkflowRepository as LegacySqlAlchemy

    assert LegacyInMemory is InMemoryWorkflowRepository
    assert LegacySqlAlchemy is SqlAlchemyWorkflowRepository


def test_demo_seed_is_exposed_through_explicit_service_boundary() -> None:
    assert {"seed_demo", "find_demo_case", "demo_seed_response"} <= set(
        DemoSeedService.__dict__
    )
