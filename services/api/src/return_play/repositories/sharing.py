from __future__ import annotations

from typing import Protocol

from return_play.auth import RequestContext
from return_play.models import ShareTokenCreate, ShareTokenRevoke


class SharingReportingAuditRepositoryBoundary(Protocol):
    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        ...

    def get_share(self, token: str) -> dict:
        ...

    def revoke_share(
        self,
        share_id: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        ...

    def build_report(self, case_id: str, context: RequestContext) -> bytes:
        ...

    def get_audit_log(
        self,
        case_id: str,
        context: RequestContext,
    ) -> dict[str, list[dict]]:
        ...
