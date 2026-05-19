from sqlalchemy.orm import Session

from app.models import Comment, Link
from app.services.audit_service import AuditService
from app.services.teams_service import TeamsService


class CommentsService:
    def __init__(self, db: Session):
        self.db = db
        self.teams = TeamsService(db)
        self.audit = AuditService(db)

    def _get_team_link(self, *, team_id: int, link_id: int) -> Link | None:
        link = self.db.query(Link).filter(Link.id == link_id).first()
        if link is None:
            return None

        owner_role = self.teams.get_team_role(team_id=team_id, principal_id=link.created_by or "")
        return link if owner_role is not None else None

    def create_comment(
        self,
        *,
        team_id: int,
        link_id: int,
        acting_principal_id: str,
        body: str,
        parent_id: int | None,
    ) -> Comment | None:
        try:
            self.teams.require_team_role(
                team_id=team_id,
                principal_id=acting_principal_id,
                allowed_roles={"owner", "admin", "member"},
                forbidden_message="Only team members can comment on team links",
            )
        except LookupError:
            return None

        link = self._get_team_link(team_id=team_id, link_id=link_id)
        if link is None:
            raise PermissionError("Link is not available to this team")

        comment = Comment(
            team_id=team_id,
            link_id=link_id,
            author_id=acting_principal_id,
            body=body,
            parent_id=parent_id,
        )
        self.db.add(comment)
        self.db.flush()
        self.audit.record_event(
            event_type="comment.created",
            team_id=team_id,
            actor_id=acting_principal_id,
            target_type="comment",
            target_id=str(comment.id),
            metadata={"link_id": link_id},
        )
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def list_comments(
        self,
        *,
        team_id: int,
        link_id: int,
        acting_principal_id: str,
    ) -> list[Comment] | None:
        try:
            self.teams.require_team_role(
                team_id=team_id,
                principal_id=acting_principal_id,
                allowed_roles={"owner", "admin", "member"},
                forbidden_message="Only team members can view team comments",
            )
        except LookupError:
            return None

        link = self._get_team_link(team_id=team_id, link_id=link_id)
        if link is None:
            raise PermissionError("Link is not available to this team")

        return (
            self.db.query(Comment)
            .filter(Comment.team_id == team_id, Comment.link_id == link_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

    def delete_comment(
        self,
        *,
        team_id: int,
        link_id: int,
        comment_id: int,
        acting_principal_id: str,
    ) -> bool | None:
        try:
            role = self.teams.get_team_role(team_id=team_id, principal_id=acting_principal_id)
            if role is None:
                if self.teams.get_team(team_id) is None:
                    return None
                raise PermissionError("Only team members can delete comments")
        except LookupError:
            return None

        link = self._get_team_link(team_id=team_id, link_id=link_id)
        if link is None:
            raise PermissionError("Link is not available to this team")

        comment = (
            self.db.query(Comment)
            .filter(
                Comment.id == comment_id,
                Comment.team_id == team_id,
                Comment.link_id == link_id,
            )
            .first()
        )
        if comment is None:
            return None

        role = self.teams.get_team_role(team_id=team_id, principal_id=acting_principal_id)
        if acting_principal_id != comment.author_id and role not in {"owner", "admin"}:
            raise PermissionError("Only the author or a team admin can delete comments")

        self.db.delete(comment)
        self.audit.record_event(
            event_type="comment.deleted",
            team_id=team_id,
            actor_id=acting_principal_id,
            target_type="comment",
            target_id=str(comment_id),
            metadata={"link_id": link_id},
        )
        self.db.commit()
        return True
