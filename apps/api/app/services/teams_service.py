from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Team, TeamMember


class InvalidTeamMemberRoleError(ValueError):
    pass


class TeamsService:
    def __init__(self, db: Session):
        self.db = db

    def create_team(self, *, name: str, owner_principal_id: str) -> Team:
        team = Team(name=name, owner_principal_id=owner_principal_id)
        self.db.add(team)
        self.db.flush()

        owner_membership = TeamMember(
            team_id=team.id,
            principal_id=owner_principal_id,
            role="owner",
        )
        self.db.add(owner_membership)
        self.db.commit()
        self.db.refresh(team)
        return team

    def get_team(self, team_id: int) -> Team | None:
        return self.db.query(Team).filter(Team.id == team_id).first()

    def get_team_role(self, *, team_id: int, principal_id: str) -> str | None:
        team = self.get_team(team_id)
        if team is None:
            return None

        if team.owner_principal_id == principal_id:
            return "owner"

        membership = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.principal_id == principal_id,
            )
            .first()
        )
        return membership.role if membership is not None else None

    def require_team_role(
        self,
        *,
        team_id: int,
        principal_id: str,
        allowed_roles: set[str],
        forbidden_message: str,
    ) -> Team:
        team = self.get_team(team_id)
        if team is None:
            raise LookupError("Team not found")

        role = self.get_team_role(team_id=team_id, principal_id=principal_id)
        if role not in allowed_roles:
            raise PermissionError(forbidden_message)

        return team

    def add_team_member(
        self,
        *,
        team_id: int,
        acting_principal_id: str,
        principal_id: str,
        role: str,
    ) -> TeamMember | None:
        try:
            self.require_team_role(
                team_id=team_id,
                principal_id=acting_principal_id,
                allowed_roles={"owner"},
                forbidden_message="Only the team owner can add members",
            )
        except LookupError:
            return None

        if role not in {"admin", "member"}:
            raise InvalidTeamMemberRoleError("role must be one of: admin, member")

        existing_member = (
            self.db.query(TeamMember)
            .filter(
                TeamMember.team_id == team_id,
                TeamMember.principal_id == principal_id,
            )
            .first()
        )
        if existing_member is not None:
            raise ValueError("Member already belongs to this team")

        member = TeamMember(
            team_id=team_id,
            principal_id=principal_id,
            role=role,
        )
        self.db.add(member)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ValueError("Member already belongs to this team") from exc
        self.db.refresh(member)
        return member
