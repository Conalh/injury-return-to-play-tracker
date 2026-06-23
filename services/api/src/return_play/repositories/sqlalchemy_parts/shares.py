from __future__ import annotations

from datetime import timedelta
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy import select

from return_play.audit import AuditEventType
from return_play.auth import RequestContext
from return_play.db import Athlete, InjuryCase, ShareToken, SymptomLog
from return_play.models import (
    AthleteSymptomCheckIn,
    GuardianAcknowledgmentCreate,
    ShareAudience,
    ShareTokenCreate,
    ShareTokenRevoke,
)
from return_play.permissions import Permission, assert_permission
from return_play.privacy import filter_share_view


class SqlAlchemyShareRepositoryMixin:
    def create_share(
        self,
        case_id: str,
        payload: ShareTokenCreate,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            self._validate_evidence_case(session, case_id, payload.injury_case_id, context)
            raw_token = token_urlsafe(24)
            now = self._now()
            share = ShareToken(
                id=self._new_id("share"),
                token_hash=self._hash_token(raw_token),
                created_at=now,
                expires_at=now + timedelta(days=payload.expires_in_days),
                revoked_at=None,
                injury_case_id=payload.injury_case_id,
                audience=payload.audience.value,
                allowed_activities=payload.allowed_activities,
                restricted_activities=payload.restricted_activities,
                clinician_note=payload.clinician_note,
                next_review_date=payload.next_review_date,
            )
            session.add(share)
            session.flush()
            self._record_audit_event(
                session,
                case_id,
                "share_created",
                context.actor_id,
                {"audience": payload.audience.value, "share_id": share.id},
            )
            session.commit()
            return {**self._share_dict(share), "token": raw_token}

    def get_share(self, token: str) -> dict:
        with self.session_factory() as session:
            share = self._get_active_share_by_token(session, token)
            injury_case = session.get(InjuryCase, share.injury_case_id)
            athlete = session.get(Athlete, injury_case.athlete_id)
            current_phase = next(
                (
                    phase
                    for phase in self._case_phases(session, injury_case.id)
                    if self._is_active_phase(phase)
                ),
                None,
            )
            self._record_audit_event(
                session,
                injury_case.id,
                AuditEventType.SHARE_VIEW_READ.value,
                None,
                {"audience": share.audience, "share_id": share.id},
            )
            session.commit()
            return filter_share_view(
                {
                    "audience": share.audience,
                    "athlete_name": athlete.name,
                    "sport": athlete.sport,
                    "injury_title": injury_case.title,
                    "current_phase": current_phase["name"] if current_phase else None,
                    "participation_status": "Modified participation",
                    "allowed_activities": share.allowed_activities,
                    "restricted_activities": share.restricted_activities,
                    "next_review_date": share.next_review_date,
                    "clearance_status": (
                        "Awaiting named clinician decision. "
                        "This shared view is not medical clearance."
                    ),
                    "clinician_note": share.clinician_note,
                },
                audience=share.audience,
            )

    def create_athlete_symptom_check_in(
        self,
        token: str,
        payload: AthleteSymptomCheckIn,
    ) -> dict:
        with self.session_factory() as session:
            share = self._get_active_share_by_token(session, token)
            if share.audience != ShareAudience.ATHLETE.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Symptom check-ins require an athlete share.",
                )
            injury_case = session.get(InjuryCase, share.injury_case_id)
            symptom_log = SymptomLog(
                id=self._new_id("symptom"),
                recorded_at=self._now(),
                injury_case_id=injury_case.id,
                athlete_id=injury_case.athlete_id,
                **payload.model_dump(mode="python"),
            )
            session.add(symptom_log)
            session.flush()
            self._record_audit_event(
                session,
                injury_case.id,
                "athlete_symptom_check_in",
                injury_case.athlete_id,
                {"symptom_log_id": symptom_log.id, "share_id": share.id},
            )
            session.commit()
            return self._symptom_dict(symptom_log)

    def create_guardian_acknowledgment(
        self,
        token: str,
        payload: GuardianAcknowledgmentCreate,
    ) -> dict:
        with self.session_factory() as session:
            share = self._get_active_share_by_token(session, token)
            if share.audience != ShareAudience.GUARDIAN.value:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Acknowledgments require a guardian share.",
                )
            acknowledgment = {
                **payload.model_dump(mode="json"),
                "id": self._new_id("guardian_ack"),
                "share_id": share.id,
                "injury_case_id": share.injury_case_id,
                "created_at": self._now(),
            }
            self._record_audit_event(
                session,
                share.injury_case_id,
                "guardian_acknowledgment_recorded",
                None,
                {
                    "share_id": share.id,
                    "acknowledged_by": acknowledgment["acknowledged_by"],
                    "relationship": acknowledgment["relationship"],
                },
            )
            session.commit()
            return acknowledgment

    def revoke_share(
        self,
        token: str,
        payload: ShareTokenRevoke,
        context: RequestContext,
    ) -> dict:
        assert_permission(context, Permission.MANAGE_SHARES)
        self._ensure_active_context(context)
        with self.session_factory() as session:
            share = session.scalar(
                select(ShareToken).where(ShareToken.token_hash == self._hash_token(token))
            )
            if share is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Share token not found.",
                )
            self._get_case(session, share.injury_case_id, context.organization_id)
            if payload.revoked_by != context.actor_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Revocation actor must match request context.",
                )
            if share.revoked_at is None:
                share.revoked_at = self._now()
                self._record_audit_event(
                    session,
                    share.injury_case_id,
                    "share_revoked",
                    context.actor_id,
                    {"audience": share.audience, "share_id": share.id},
                )
            session.commit()
            return self._share_dict(share)
