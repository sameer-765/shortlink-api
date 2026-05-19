import json
import unittest

from fastapi.testclient import TestClient

from app import database
from app.config import get_settings
from app.main import app
from app.models import AuditLog, Comment, Link, Team, TeamInvitation, TeamMember
from app.schemas.activity import TeamActivityEvent


class AuditEventsTest(unittest.TestCase):
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

    def test_invite_and_comment_actions_record_shared_activity_events(self) -> None:
        team = self._create_team()
        link = self._create_link()

        invite = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "audit@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(invite.status_code, 201)

        add_member = self.client.post(
            f"/teams/{team['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(add_member.status_code, 201)

        comment = self.client.post(
            f"/teams/{team['id']}/links/{link['id']}/comments",
            json={"body": "Audit this comment"},
            headers={"X-API-Key": self.api_key_b},
        )
        self.assertEqual(comment.status_code, 201)

        db = database._SessionLocal()
        try:
            audit_entries = db.query(AuditLog).order_by(AuditLog.id.asc()).all()
            self.assertEqual(len(audit_entries), 2)

            event_types = [entry.event_type for entry in audit_entries]
            self.assertEqual(event_types, ["invite.created", "comment.created"])

            first_event = TeamActivityEvent(
                event_id=audit_entries[0].event_id,
                event_type=audit_entries[0].event_type,
                team_id=audit_entries[0].team_id,
                actor_id=audit_entries[0].actor_id,
                target_type=audit_entries[0].target_type,
                target_id=audit_entries[0].target_id,
                created_at=audit_entries[0].created_at,
                metadata=json.loads(audit_entries[0].metadata_json),
            )
            self.assertEqual(first_event.team_id, team["id"])
            self.assertEqual(first_event.target_type, "invitation")
            self.assertEqual(first_event.metadata["role"], "member")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
