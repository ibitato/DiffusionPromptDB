"""
Tests for profile and admin user endpoints.
"""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import psycopg
from psycopg import conninfo, sql
import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from api.config import settings
from api.main import app
from api.services import user_service, account_service
from api.auth import create_access_token


def _create_test_database() -> tuple[str, str, str]:
    """Create a dedicated PostgreSQL database cloned from the empty template."""
    base = conninfo.conninfo_to_dict(settings.prompts_db_url)
    admin_params = base.copy()
    admin_params["dbname"] = "postgres"
    admin_conn_str = conninfo.make_conninfo(**admin_params)

    db_name = f"dpdb_test_{uuid.uuid4().hex}"
    with psycopg.connect(admin_conn_str) as admin_conn:
        admin_conn.autocommit = True
        admin_conn.execute(
            sql.SQL("CREATE DATABASE {} TEMPLATE diffusion_promptdb_test").format(
                sql.Identifier(db_name)
            )
        )

    test_params = base.copy()
    test_params["dbname"] = db_name
    test_url = conninfo.make_conninfo(**test_params)
    return db_name, admin_conn_str, test_url


def _drop_test_database(db_name: str, admin_conn_str: str) -> None:
    with psycopg.connect(admin_conn_str) as admin_conn:
        admin_conn.autocommit = True
        admin_conn.execute(
            """
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
            """,
            (db_name,),
        )
        admin_conn.execute(
            sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name))
        )


def _seed_user(db_url: str, username: str, password: str, role: str = "user") -> int:
    hashed = user_service.hash_password(password)
    now = datetime.utcnow().isoformat()
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username, email, password_hash, role, password_last_changed, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (username, f"{username}@example.com", hashed, role, now, True),
            )
            user_id = cur.fetchone()[0]
            cur.execute(
                """
                INSERT INTO user_password_history (user_id, password_hash, changed_at)
                VALUES (%s, %s, %s)
                """,
                (user_id, hashed, now),
            )
            cur.execute(
                """
                INSERT INTO user_preferences (user_id)
                VALUES (%s)
                ON CONFLICT (user_id) DO NOTHING
                """,
                (user_id,),
            )
        conn.commit()
    return user_id


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _manual_token(username: str, user_id: int, role: str) -> str:
    return create_access_token(
        {"sub": username, "user_id": user_id, "role": role},
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    db_name, admin_conn_str, test_url = _create_test_database()
    monkeypatch.setattr(settings, "users_db_url", test_url)
    monkeypatch.setattr(settings, "prompts_db_url", test_url)
    monkeypatch.setattr(settings, "email_debug_mode", True)
    account_service.DUMP_DIR = tmp_path / "account_dumps"
    account_service.DUMP_DIR.mkdir(parents=True, exist_ok=True)

    admin_id = _seed_user(test_url, "admin", "REDACTED_PASSWORD", role="admin")
    user_id = _seed_user(test_url, "tester", "testpass", role="user")

    client = TestClient(app)
    try:
        yield client, test_url, test_url, admin_id, user_id
    finally:
        _drop_test_database(db_name, admin_conn_str)


def _login(client: TestClient, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


class TestProfileEndpoints:
    def test_profile_flow(self, api_client):
        client, _, _, _, _ = api_client
        token = _login(client, "tester", "testpass")

        resp = client.get("/api/v1/user/profile", headers=_auth_headers(token))
        assert resp.status_code == 200

        resp = client.put(
            "/api/v1/user/profile",
            json={"full_name": "Test User", "language": "es"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Test User"

        resp = client.put(
            "/api/v1/user/profile/default-page",
            json={"default_landing_page": "search"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["default_landing_page"] == "search"

        resp = client.put(
            "/api/v1/user/profile/password",
            json={"current_password": "testpass", "new_password": "NewPassword!123"},
            headers=_auth_headers(token),
        )
        assert resp.status_code == 200, resp.text

        new_token = _login(client, "tester", "NewPassword!123")
        assert new_token

        prefs_resp = client.put(
            "/api/v1/user/preferences",
            json={
                "show_unspecified": False,
                "my_prompts_only": True,
                "excluded_tags": ["lowres"],
            },
            headers=_auth_headers(new_token),
        )
        assert prefs_resp.status_code == 200
        assert prefs_resp.json()["my_prompts_only"] is True

    def test_account_deletion_dumps_data(self, api_client):
        client, users_db, prompts_db, _, _ = api_client

        victim_id = _seed_user(users_db, "deleteme", "delete123", role="user")
        with psycopg.connect(prompts_db) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO prompts (original_prompt, processed_at, model_used, created_by, input_tokens, output_tokens)
                    VALUES (%s, %s, %s, %s, 0, 0)
                    """,
                    ("test prompt", datetime.utcnow().isoformat(), "manual", victim_id),
                )
            conn.commit()

        token = _manual_token("deleteme", victim_id, "user")
        delete_resp = client.request(
            "DELETE",
            "/api/v1/user/account",
            json={"password": "delete123", "confirm": True},
            headers=_auth_headers(token),
        )
        assert delete_resp.status_code == 200, delete_resp.text

        with psycopg.connect(users_db) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM users WHERE username=%s", ("deleteme",)
                )
                assert cur.fetchone()[0] == 0
                cur.execute("SELECT dump_path FROM account_deletion_audit")
                audit = cur.fetchone()
        assert audit is not None
        assert Path(audit[0]).exists()


class TestAdminUsers:
    def test_admin_can_manage_users(self, api_client):
        client, users_db, _, admin_id, _ = api_client
        headers = _auth_headers(_manual_token("admin", admin_id, "admin"))

        create_resp = client.post(
            "/api/v1/admin/users",
            json={
                "username": "managed",
                "email": "managed@example.com",
                "role": "user",
                "password": "ManagedPass!23",
                "full_name": "Managed User",
            },
            headers=headers,
        )
        assert create_resp.status_code == 201, create_resp.text
        user_id = create_resp.json()["id"]

        list_resp = client.get("/api/v1/admin/users", headers=headers)
        assert any(u["username"] == "managed" for u in list_resp.json()["users"])

        update_resp = client.put(
            f"/api/v1/admin/users/{user_id}",
            json={"role": "admin", "is_active": False},
            headers=headers,
        )
        assert update_resp.status_code == 200

        reset_resp = client.put(
            f"/api/v1/admin/users/{user_id}/password",
            json={"new_password": "AnotherPass!9"},
            headers=headers,
        )
        assert reset_resp.status_code == 200

        client.put(
            f"/api/v1/admin/users/{user_id}",
            json={"is_active": True},
            headers=headers,
        )

        with psycopg.connect(users_db) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password_hash FROM users WHERE id=%s", (user_id,)
                )
                stored_hash = cur.fetchone()[0]
        assert user_service.verify_password("AnotherPass!9", stored_hash)

        delete_resp = client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 204


class TestAuthPasswordExpiry:
    def test_expired_password_flow(self, api_client):
        client, users_db, _, _, user_id = api_client

        with psycopg.connect(users_db) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET must_change_password=%s WHERE id=%s",
                    (True, user_id),
                )
            conn.commit()

        login_resp = client.post(
            "/api/v1/auth/login", json={"username": "tester", "password": "testpass"}
        )
        assert login_resp.status_code == 403
        assert login_resp.headers.get("X-Password-Expired") == "true"

        reset_resp = client.post(
            "/api/v1/auth/password/expired",
            json={
                "username": "tester",
                "current_password": "testpass",
                "new_password": "NewPassword!123",
            },
        )
        assert reset_resp.status_code == 200, reset_resp.text

        new_login = client.post(
            "/api/v1/auth/login",
            json={"username": "tester", "password": "NewPassword!123"},
        )
        assert new_login.status_code == 200, new_login.text


class TestDashboardStats:
    def test_my_prompts_requires_auth(self, api_client):
        client, _, _, _, _ = api_client
        resp = client.get("/api/v1/admin/stats?my_prompts_only=true")
        assert resp.status_code == 401

    def test_my_prompts_statistics_filtered(self, api_client):
        client, _, prompts_db, _, user_id = api_client

        with psycopg.connect(prompts_db) as conn:
            now = datetime.utcnow().isoformat()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO prompts (id, original_prompt, processed_at, model_used, created_by, input_tokens, output_tokens)
                    VALUES (%s, %s, %s, %s, %s, 0, 0)
                    """,
                    (101, "User prompt", now, "sd15", user_id),
                )
                cur.execute(
                    """
                    INSERT INTO prompts (id, original_prompt, processed_at, model_used, created_by, input_tokens, output_tokens)
                    VALUES (%s, %s, %s, %s, %s, 0, 0)
                    """,
                    (202, "Global prompt", now, "sdxl", None),
                )
                cur.execute(
                    "INSERT INTO nsfw_content (prompt_id, level) VALUES (%s, %s)",
                    (101, "safe"),
                )
                cur.execute(
                    "INSERT INTO nsfw_content (prompt_id, level) VALUES (%s, %s)",
                    (202, "explicit"),
                )
                cur.execute(
                    "INSERT INTO main_tags (prompt_id, tag) VALUES (%s, %s)",
                    (101, "forest"),
                )
                cur.execute(
                    "INSERT INTO main_tags (prompt_id, tag) VALUES (%s, %s)",
                    (202, "city"),
                )
                cur.execute(
                    "INSERT INTO art_styles (prompt_id, primary_style) VALUES (%s, %s)",
                    (101, "anime"),
                )
                cur.execute(
                    "INSERT INTO art_styles (prompt_id, primary_style) VALUES (%s, %s)",
                    (202, "realistic"),
                )
                cur.execute(
                    "INSERT INTO characters (prompt_id, number_of_people) VALUES (%s, %s)",
                    (101, 1),
                )
                cur.execute(
                    "INSERT INTO characters (prompt_id, number_of_people) VALUES (%s, %s)",
                    (202, 2),
                )
            conn.commit()

        token = _manual_token("tester", user_id, "user")
        filtered = client.get(
            "/api/v1/admin/stats?my_prompts_only=true",
            headers=_auth_headers(token),
        )
        assert filtered.status_code == 200, filtered.text
        data = filtered.json()
        assert data["total_prompts"] == 1
        assert data["top_tags"][0]["tag"] == "forest"
        assert data["total_tags"] == 1
        assert "safe" in data["nsfw_distribution"]
        assert "explicit" not in data["nsfw_distribution"]
        assert data["top_art_styles"][0]["style"] == "anime"


class TestRegistrationFlow:
    def test_register_and_verify(self, api_client):
        client, _, _, _, _ = api_client
        payload = {
            "username": "newtester",
            "email": "newtester@example.com",
            "password": "StrongPass!23",
        }

        register_resp = client.post("/api/v1/auth/register", json=payload)
        assert register_resp.status_code == 201, register_resp.text
        token = register_resp.json().get("verification_token")
        assert token

        # Cannot login until verification is completed
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": payload["username"], "password": payload["password"]},
        )
        assert login_resp.status_code == 403

        verify_resp = client.post("/api/v1/auth/verify", json={"token": token})
        assert verify_resp.status_code == 200, verify_resp.text

        login_resp = client.post(
            "/api/v1/auth/login",
            json={"username": payload["username"], "password": payload["password"]},
        )
        assert login_resp.status_code == 200
        assert login_resp.json()["user"]["username"] == payload["username"]

    def test_register_duplicate_email(self, api_client):
        client, _, _, _, _ = api_client
        payload = {
            "username": "uniqueuser",
            "email": "unique@example.com",
            "password": "StrongPass!23",
        }

        first = client.post("/api/v1/auth/register", json=payload)
        assert first.status_code == 201

        duplicate_username = client.post(
            "/api/v1/auth/register",
            json={
                "username": payload["username"],
                "email": "another@example.com",
                "password": payload["password"],
            },
        )
        assert duplicate_username.status_code == 400

        duplicate_email = client.post(
            "/api/v1/auth/register",
            json={
                "username": "differentuser",
                "email": payload["email"],
                "password": payload["password"],
            },
        )
        assert duplicate_email.status_code == 400
