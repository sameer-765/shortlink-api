import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app import database
from app.config import get_settings
from app.main import app
from app.models import Team, TeamMember


class TeamFlowTest(unittest.TestCase):
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
            db.query(TeamMember).delete()
            db.query(Team).delete()
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

    def test_create_team_creates_owner_membership(self) -> None:
        created = self._create_team(name="Launch Team")

        self.assertEqual(created["name"], "Launch Team")
        self.assertEqual(created["owner_principal_id"], "principal_a")

        db = database._SessionLocal()
        try:
            owner_membership = (
                db.query(TeamMember)
                .filter(
                    TeamMember.team_id == created["id"],
                    TeamMember.principal_id == "principal_a",
                )
                .one()
            )
            self.assertEqual(owner_membership.role, "owner")
        finally:
            db.close()

    def test_add_team_member_returns_201_and_persists_membership(self) -> None:
        created = self._create_team()

        response = self.client.post(
            f"/teams/{created['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["team_id"], created["id"])
        self.assertEqual(body["principal_id"], "principal_b")
        self.assertEqual(body["role"], "member")

        db = database._SessionLocal()
        try:
            persisted = (
                db.query(TeamMember)
                .filter(
                    TeamMember.team_id == created["id"],
                    TeamMember.principal_id == "principal_b",
                )
                .one()
            )
            self.assertEqual(persisted.role, "member")
        finally:
            db.close()

    def test_add_team_member_requires_valid_api_key(self) -> None:
        created = self._create_team()

        response = self.client.post(
            f"/teams/{created['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": "bad-key"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "unauthorized")

    def test_add_team_member_rejects_non_owner(self) -> None:
        created = self._create_team()

        response = self.client.post(
            f"/teams/{created['id']}/members",
            json={"principal_id": "principal_c", "role": "member"},
            headers={"X-API-Key": self.api_key_b},
        )

        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "forbidden")
        self.assertEqual(body["error"]["message"], "Only the team owner can add members")

    def test_add_team_member_rejects_duplicates(self) -> None:
        created = self._create_team()
        first = self.client.post(
            f"/teams/{created['id']}/members",
            json={"principal_id": "principal_b", "role": "admin"},
            headers={"X-API-Key": self.api_key_a},
        )
        self.assertEqual(first.status_code, 201)

        duplicate = self.client.post(
            f"/teams/{created['id']}/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )

        self.assertEqual(duplicate.status_code, 409)
        body = duplicate.json()
        self.assertEqual(body["error"]["code"], "conflict")
        self.assertEqual(body["error"]["message"], "Member already belongs to this team")

    def test_add_team_member_rejects_invalid_role(self) -> None:
        created = self._create_team()

        response = self.client.post(
            f"/teams/{created['id']}/members",
            json={"principal_id": "principal_b", "role": "owner"},
            headers={"X-API-Key": self.api_key_a},
        )

        self.assertEqual(response.status_code, 422)
        body = response.json()
        self.assertEqual(body["error"]["code"], "validation_error")
        self.assertEqual(body["error"]["message"], "Input should be 'admin' or 'member'")

    def test_add_team_member_returns_conflict_when_commit_hits_unique_constraint(self) -> None:
        created = self._create_team()

        session_class = database._SessionLocal.class_

        def commit_with_duplicate(session) -> None:
            raise IntegrityError("duplicate membership", params=None, orig=None)

        with patch.object(session_class, "commit", autospec=True, side_effect=commit_with_duplicate):
            response = self.client.post(
                f"/teams/{created['id']}/members",
                json={"principal_id": "principal_b", "role": "member"},
                headers={"X-API-Key": self.api_key_a},
            )

        self.assertEqual(response.status_code, 409)
        body = response.json()
        self.assertEqual(body["error"]["code"], "conflict")
        self.assertEqual(body["error"]["message"], "Member already belongs to this team")

    def test_add_team_member_returns_404_for_missing_team(self) -> None:
        response = self.client.post(
            "/teams/99999/members",
            json={"principal_id": "principal_b", "role": "member"},
            headers={"X-API-Key": self.api_key_a},
        )

        self.assertEqual(response.status_code, 404)
        body = response.json()
        self.assertEqual(body["error"]["code"], "not_found")
        self.assertEqual(body["error"]["message"], "Team not found")


if __name__ == "__main__":
    unittest.main()
