from __future__ import annotations

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe

from fastapi import HTTPException, status

from return_play.audit import AuditEventType
from return_play.auth import RequestContext
from return_play.models import (
    AthleteSymptomCheckIn,
    GuardianAcknowledgmentCreate,
    ShareAudience,
    ShareTokenCreate,
    ShareTokenRevoke,
)
from return_play.permissions import Permission, assert_permission
from return_play.privacy import filter_share_view


class InMemoryShareRepositoryMixin:
    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_user(context)
        self._validate_evidence_case(case_id, payload.injury_case_id, context)
        raw_token = token_urlsafe(24)
        token_hash = self._hash_token(raw_token)
        now = datetime.now(UTC)
        share = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("share"),
            "token": raw_token,
            "token_hash": token_hash,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=payload.expires_in_days)).isoformat(),
            "revoked_at": None,
        }
        self.share_tokens[token_hash] = share
        self._record_audit_event(
            case_id,
            "share_created",
            context.actor_id,
            {"audience": payload.audience.value, "share_id": share["id"]},
        )
        return share

    def get_share(self, token: str) -> dict:
        share = self._get_active_share_by_token(token)

        injury_case = self._get_case(share["injury_case_id"])
        athlete = self.athletes[injury_case["athlete_id"]]
        phases = self.case_plans.get(injury_case["id"], [])
        current_phase = next(
            (phase for phase in phases if self._is_active_phase(phase)),
            None,
        )
        self._record_audit_event(
            injury_case["id"],
            AuditEventType.SHARE_VIEW_READ.value,
            None,
            {"audience": share["audience"], "share_id": share["id"]},
        )
        return filter_share_view(
            {
                "audience": share["audience"],
                "athlete_name": athlete["name"],
                "sport": athlete["sport"],
                "injury_title": injury_case["title"],
                "current_phase": current_phase["name"] if current_phase else None,
                "participation_status": "Modified participation",
                "allowed_activities": share["allowed_activities"],
                "restricted_activities": share["restricted_activities"],
                "next_review_date": share["next_review_date"],
                "clearance_status": (
                    "Awaiting named clinician decision. "
                    "This shared view is not medical clearance."
                ),
                "clinician_note": share["clinician_note"],
            },
            audience=share["audience"],
        )

    def create_athlete_symptom_check_in(
        self,
        token: str,
        payload: AthleteSymptomCheckIn,
    ) -> dict:
        share = self._get_active_share_by_token(token)
        if share["audience"] != ShareAudience.ATHLETE.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Symptom check-ins require an athlete share.",
            )
        injury_case = self._get_case(share["injury_case_id"])
        symptom_log = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("symptom"),
            "injury_case_id": injury_case["id"],
            "athlete_id": injury_case["athlete_id"],
            "recorded_at": self._now(),
        }
        self.symptom_logs.setdefault(injury_case["id"], []).append(symptom_log)
        self._record_audit_event(
            injury_case["id"],
            "athlete_symptom_check_in",
            injury_case["athlete_id"],
            {"symptom_log_id": symptom_log["id"], "share_id": share["id"]},
        )
        return symptom_log

    def create_guardian_acknowledgment(
        self,
        token: str,
        payload: GuardianAcknowledgmentCreate,
    ) -> dict:
        share = self._get_active_share_by_token(token)
        if share["audience"] != ShareAudience.GUARDIAN.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acknowledgments require a guardian share.",
            )
        acknowledgment = {
            **payload.model_dump(mode="json"),
            "id": self._new_id("guardian_ack"),
            "share_id": share["id"],
            "injury_case_id": share["injury_case_id"],
            "created_at": self._now(),
        }
        self._record_audit_event(
            share["injury_case_id"],
            "guardian_acknowledgment_recorded",
            None,
            {
                "share_id": share["id"],
                "acknowledged_by": acknowledgment["acknowledged_by"],
                "relationship": acknowledgment["relationship"],
            },
        )
        return acknowledgment

    def revoke_share(
        self,
        token: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_user(context)
        share = self._get_share_by_token(token)
        self._get_case(share["injury_case_id"], context.organization_id)
        if payload.revoked_by != context.actor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Revocation actor must match request context.",
            )
        if share["revoked_at"] is None:
            share["revoked_at"] = self._now()
            self._record_audit_event(
                share["injury_case_id"],
                "share_revoked",
                context.actor_id,
                {"audience": share["audience"], "share_id": share["id"]},
            )
        return share
