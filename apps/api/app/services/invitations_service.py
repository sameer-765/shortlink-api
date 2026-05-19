from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import TeamInvitation
from app.services.audit_service import AuditService
from app.services.teams_service import TeamsService


class InvitationsService:
    def __init__(self, db: Session):
        self.db = db
        self.teams = TeamsService(db)
        self.audit = AuditService(db)

    def create_invitation(
        self,
        *,
        team_id: int,
        acting_principal_id: str,
        email: str,
        role: str,
    ) -> TeamInvitation | None:
        try:
            self.teams.require_team_role(
                team_id=team_id,
                principal_id=acting_principal_id,
                allowed_roles={"owner", "admin"},
                forbidden_message="Only team owners or admins can create invitations",
            )
        except LookupError:
            return None

        invitation = TeamInvitation(
            team_id=team_id,
            email=email,
            role=role,
            invited_by=acting_principal_id,
            status="pending",
        )
        self.db.add(invitation)
        try:
            self.audit.record_event(
                event_type="invite.created",
                team_id=team_id,
                actor_id=acting_principal_id,
                target_type="invitation",
                target_id=email,
                metadata={"role": role},
            )
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValueError("Invitation already exists for this team and email") from exc

        self.db.refresh(invitation)
        return invitation

    def revoke_invitation(
        self,
        *,
        team_id: int,
        invitation_id: int,
        acting_principal_id: str,
    ) -> TeamInvitation | None:
        try:
            self.teams.require_team_role(
                team_id=team_id,
                principal_id=acting_principal_id,
                allowed_roles={"owner", "admin"},
                forbidden_message="Only team owners or admins can revoke invitations",
            )
        except LookupError:
            return None

        invitation = (
            self.db.query(TeamInvitation)
            .filter(
                TeamInvitation.id == invitation_id,
                TeamInvitation.team_id == team_id,
            )
            .first()
        )
        if invitation is None:
            return None

        invitation.status = "revoked"
        self.audit.record_event(
            event_type="invite.revoked",
            team_id=team_id,
            actor_id=acting_principal_id,
            target_type="invitation",
            target_id=str(invitation.id),
            metadata={"email": invitation.email},
        )
        self.db.commit()
        self.db.refresh(invitation)
        return invitation
