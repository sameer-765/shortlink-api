import unittest

from fastapi.testclient import TestClient

from app import database
from app.config import get_settings
from app.main import app
from app.models import AuditLog, Comment, Link, Team, TeamInvitation, TeamMember


class CommentsFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = get_settings()
        self.settings.api_key_a = self.settings.api_key_a or "team-test-key-a"
        self.settings.api_key_b = self.settings.api_key_b or "team-test-key-b"
        self.api_key_a = self.settings.api_key_a
        self.api_key_b = self.settings.api_key_b
        self.client = TestClient(app)
        database.init_db()
        self._reset_tables()

    def _reset_tables(self) -> None:
        db = database._SessionLocal()
        try:
            db.query(AuditLog).delete()
            db.query(Comment).delete()
            db.query(TeamInvitation).delete()
            db.query(TeamMember).delete()
            db.query(Team).delete()
            db.query(Link).delete()
            db.commit()
        finally:
            db.close()

    def _create_team(self, *, api_key: str | None = None, name: str = "Platform") -> dict:
        response = self.client.post(
            "/teams",
            json={"name": name},
            headers={"X-API-Key": api_key or self.api_key_a},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def _create_link(self, *, api_key: str | None = None, long_url: str = "https://example.com") -> dict:
        response = self.client.post(
            "/links",
            json={"long_url": long_url},
            headers={"X-API-Key": api_key or self.api_key_a},
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def _get_comment(self, *, comment_id: int) -> Comment | None:
        db = database._SessionLocal()
        try:
            return db.query(Comment).filter(Comment.id == comment_id).first()
        finally:
            db.close()

    def _get_audit_entries(self, *, event_type: str, target_id: str) -> list[AuditLog]:
        db = database._SessionLocal()
        try:
            return (
                db.query(AuditLog)
                .filter(
                    AuditLog.event_type == event_type,
                    AuditLog.target_id == target_id,
                )
                .order_by(AuditLog.id.asc())
                .all()
            )
        finally:
            db.close()

    def test_authorized_team_member_can_comment_on_team_link(self) -> None:
        team = self._create_team()
        link = self._create_link()

        add_member = self.client.post(
            f"/teams/{team['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(add_member.status_code, 201)

        response = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Looks good"},
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["team_id"], team["id"])
        self.assertEqual(body["link_id"], link["id"])
        self.assertEqual(body["author_id"], "principal_b")

    def test_cross_team_user_is_rejected(self) -> None:
        team = self._create_team()
        link = self._create_link()
        other_team = self._create_team(api_key=self.api_key_b, name="Other Team")
        self.assertNotEqual(other_team["id"], team["id"])

        response = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Not allowed"},
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only team members can comment on team links")

    def test_cross_team_admin_cannot_delete_another_teams_comment(self) -> None:
        team = self._create_team()
        link = self._create_link()
        other_team = self._create_team(api_key=self.api_key_b, name="Other Team")
        self.assertNotEqual(other_team["id"], team["id"])

        create_comment = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Protected comment"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(create_comment.status_code, 201)
        comment_id = create_comment.json()["id"]

        delete_response = self.client.delete(
            f"/teams/{team['id']}/links/{link['id']}/comments/{comment_id}",
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(delete_response.status_code, 403)
        body = delete_response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only team members can delete comments")

        comment = self._get_comment(comment_id=comment_id)
        self.assertIsNotNone(comment)
        self.assertEqual(comment.author_id, "principal_a")
        self.assertEqual(len(self._get_audit_entries(event_type="comment.deleted", target_id=str(comment_id))), 0)

    def test_non_author_team_member_cannot_delete_another_members_comment(self) -> None:
        team = self._create_team()
        link = self._create_link()
        add_member = self.client.post(
            f"/teams/{team['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(add_member.status_code, 201)

        create_comment = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Owner comment"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(create_comment.status_code, 201)
        comment_id = create_comment.json()["id"]

        delete_response = self.client.delete(
            f"/teams/{team['id']}/links/{link['id']}/comments/{comment_id}",
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(delete_response.status_code, 403)
        body = delete_response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only the author or a team admin can delete comments")

        comment = self._get_comment(comment_id=comment_id)
        self.assertIsNotNone(comment)
        self.assertEqual(comment.author_id, "principal_a")
        self.assertEqual(len(self._get_audit_entries(event_type="comment.deleted", target_id=str(comment_id))), 0)

    def test_comment_author_can_delete_their_own_comment(self) -> None:
        team = self._create_team()
        link = self._create_link()
        create_comment = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Delete me"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(create_comment.status_code, 201)
        comment_id = create_comment.json()["id"]

        delete_response = self.client.delete(
            f"/teams/{team['id']}/links/{link['id']}/comments/{comment_id}",
            headers={"X-API-Key": self.api_key_a},
        )

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(self._get_comment(comment_id=comment_id), None)

        audit_entries = self._get_audit_entries(event_type="comment.deleted", target_id=str(comment_id))
        self.assertEqual(len(audit_entries), 1)
        audit_entry = audit_entries[0]
        self.assertEqual(audit_entry.team_id, team["id"])
        self.assertEqual(audit_entry.actor_id, "principal_a")
        self.assertEqual(audit_entry.target_type, "comment")
        self.assertEqual(audit_entry.target_id, str(comment_id))
        self.assertEqual(audit_entry.event_type, "comment.deleted")

    def test_team_admin_can_delete_another_users_comment(self) -> None:
        team = self._create_team()
        link = self._create_link()
        add_member = self.client.post(
            f"/teams/{team['id']}/members",
            json={"principal_id": "principal_b", "role": "admin"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(add_member.status_code, 201)

        create_comment = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Admin can delete this"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(create_comment.status_code, 201)
        comment_id = create_comment.json()["id"]

        delete_response = self.client.delete(
            f"/teams/{team['id']}/links/{link['id']}/comments/{comment_id}",
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(self._get_comment(comment_id=comment_id), None)

        audit_entries = self._get_audit_entries(event_type="comment.deleted", target_id=str(comment_id))
        self.assertEqual(len(audit_entries), 1)
        audit_entry = audit_entries[0]
        self.assertEqual(audit_entry.team_id, team["id"])
        self.assertEqual(audit_entry.actor_id, "principal_b")
        self.assertEqual(audit_entry.target_type, "comment")
        self.assertEqual(audit_entry.target_id, str(comment_id))
        self.assertEqual(audit_entry.event_type, "comment.deleted")


if __name__ == "__main__":
    unittest.main()
