import unittest

from fastapi.testclient import TestClient

from app import database
from app.config import get_settings
from app.main import app
from app.models import AuditLog, Comment, Link, Team, TeamInvitation, TeamMember


class InvitationsFlowTest(unittest.TestCase):
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

    def _get_invitation(self, *, team_id: int, email: str) -> TeamInvitation | None:
        db = database._SessionLocal()
        try:
            return (
                db.query(TeamInvitation)
                .filter(
                    TeamInvitation.team_id == team_id,
                    TeamInvitation.email == email,
                )
                .first()
            )
        finally:
            db.close()

    def _count_audit_events(
        self,
        *,
        event_type: str,
        team_id: int | None = None,
        actor_id: str | None = None,
    ) -> int:
        db = database._SessionLocal()
        try:
            query = db.query(AuditLog).filter(AuditLog.event_type == event_type)
            if team_id is not None:
                query = query.filter(AuditLog.team_id == team_id)
            if actor_id is not None:
                query = query.filter(AuditLog.actor_id == actor_id)
            return query.count()
        finally:
            db.close()

    def test_owner_can_create_invitation_and_persist_state(self) -> None:
        team = self._create_team()

        response = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "invitee@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["team_id"], team["id"])
        self.assertEqual(body["email"], "invitee@example.com")
        self.assertEqual(body["status"], "pending")

        db = database._SessionLocal()
        try:
            invitation = (
                db.query(TeamInvitation)
                .filter(TeamInvitation.team_id == team["id"], TeamInvitation.email == "invitee@example.com")
                .one()
            )
            self.assertEqual(invitation.role, "member")
        finally:
            db.close()

    def test_admin_can_create_invitation(self) -> None:
        team = self._create_team()
        add_member = self.client.post(
            f"/teams/{team['id']}/members",
            json={"principal_id": "principal_b", "role": "admin"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(add_member.status_code, 201)

        response = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "admin-invite@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["invited_by"], "principal_b")

    def test_non_admin_is_rejected(self) -> None:
        team = self._create_team()

        response = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "blocked@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only team owners or admins can create invitations")

    def test_cross_team_admin_cannot_revoke_other_team_invitation(self) -> None:
        team = self._create_team()
        other_team = self._create_team(api_key=self.api_key_b, name="Other Team")
        self.assertNotEqual(other_team["id"], team["id"])

        created = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "revoke-target@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(created.status_code, 201)
        invitation_id = created.json()["id"]

        revoked_count_before = self._count_audit_events(
            event_type="invite.revoked",
            team_id=team["id"],
            actor_id="principal_b",
        )

        response = self.client.delete(
            f"/teams/{team['id']}/invitations/{invitation_id}",
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only team owners or admins can revoke invitations")

        invitation = self._get_invitation(team_id=team["id"], email="revoke-target@example.com")
        self.assertIsNotNone(invitation)
        self.assertEqual(invitation.status, "pending")
        self.assertEqual(
            self._count_audit_events(
                event_type="invite.revoked",
                team_id=team["id"],
                actor_id="principal_b",
            ),
            revoked_count_before,
        )

    def test_normal_member_cannot_revoke_invitation_from_own_team(self) -> None:
        team = self._create_team()
        add_member = self.client.post(
            f"/teams/{team['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(add_member.status_code, 201)

        created = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "member-revoke@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(created.status_code, 201)
        invitation_id = created.json()["id"]

        revoked_count_before = self._count_audit_events(
            event_type="invite.revoked",
            team_id=team["id"],
            actor_id="principal_b",
        )

        response = self.client.delete(
            f"/teams/{team['id']}/invitations/{invitation_id}",
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only team owners or admins can revoke invitations")

        invitation = self._get_invitation(team_id=team["id"], email="member-revoke@example.com")
        self.assertIsNotNone(invitation)
        self.assertEqual(invitation.status, "pending")
        self.assertEqual(
            self._count_audit_events(
                event_type="invite.revoked",
                team_id=team["id"],
                actor_id="principal_b",
            ),
            revoked_count_before,
        )

    def test_cross_team_admin_cannot_create_invitation_or_emit_audit_event(self) -> None:
        team = self._create_team()
        other_team = self._create_team(api_key=self.api_key_b, name="Other Team")
        self.assertNotEqual(other_team["id"], team["id"])

        invite_created_count_before = self._count_audit_events(
            event_type="invite.created",
            team_id=team["id"],
            actor_id="principal_b",
        )

        response = self.client.post(
            f"/teams/{team['id']}/invitations",
            json={"email": "cross-team-create@example.com", "role": "member"},
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only team owners or admins can create invitations")

        self.assertIsNone(
            self._get_invitation(team_id=team["id"], email="cross-team-create@example.com")
        )
        self.assertEqual(
            self._count_audit_events(
                event_type="invite.created",
                team_id=team["id"],
                actor_id="principal_b",
            ),
            invite_created_count_before,
        )


if __name__ == "__main__":
    unittest.main()
