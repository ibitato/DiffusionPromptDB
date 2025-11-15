"""
Tests for profile and admin user endpoints.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from api.config import settings
from api.main import app
from api.services import user_service, account_service
from api.auth import create_access_token


def _create_users_db(path: Path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin','user')) DEFAULT 'user',
            full_name TEXT,
            avatar_url TEXT,
            location TEXT,
            language TEXT DEFAULT 'en',
            default_landing_page TEXT DEFAULT 'dashboard',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            must_change_password BOOLEAN DEFAULT 0,
            password_last_changed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE user_preferences (
            user_id INTEGER PRIMARY KEY,
            show_unspecified BOOLEAN DEFAULT 1,
            my_prompts_only BOOLEAN DEFAULT 0,
            excluded_tags TEXT DEFAULT '["high quality","masterpiece","best quality"]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE user_password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            password_hash TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE account_deletion_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            email TEXT,
            deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dump_path TEXT,
            reason TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def _create_prompts_db(path: Path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_prompt TEXT,
            processed_at TIMESTAMP,
            model_used TEXT,
            created_by INTEGER,
            negative_prompt TEXT,
            parameters TEXT,
            rating INTEGER,
            notes TEXT,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0
        );

        CREATE TABLE art_styles (
            prompt_id INTEGER,
            primary_style TEXT
        );

        CREATE TABLE main_tags (
            prompt_id INTEGER,
            tag TEXT
        );

        CREATE TABLE characters (
            prompt_id INTEGER,
            number_of_people INTEGER
        );
        """
    )
    conn.commit()
    conn.close()


def _seed_user(db_path: Path, username: str, password: str, role: str = "user") -> int:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hashed = user_service.hash_password(password)
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """
        INSERT INTO users (username, email, password_hash, role, password_last_changed)
        VALUES (?, ?, ?, ?, ?)
        """,
        (username, f"{username}@example.com", hashed, role, now),
    )
    user_id = cursor.lastrowid
    cursor.execute(
        """
        INSERT INTO user_password_history (user_id, password_hash, changed_at)
        VALUES (?, ?, ?)
        """,
        (user_id, hashed, now),
    )
    cursor.execute("INSERT INTO user_preferences (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
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
    users_db = tmp_path / "users.db"
    prompts_db = tmp_path / "prompts.db"
    _create_users_db(users_db)
    _create_prompts_db(prompts_db)

    monkeypatch.setattr(settings, "users_db_path", str(users_db))
    monkeypatch.setattr(settings, "prompts_db_path", str(prompts_db))
    monkeypatch.setattr(settings, "catalog_db_path", str(prompts_db))
    account_service.DUMP_DIR = tmp_path / "account_dumps"

    admin_id = _seed_user(users_db, "admin", "admin123", role="admin")
    user_id = _seed_user(users_db, "tester", "testpass", role="user")

    client = TestClient(app)
    yield client, users_db, prompts_db, admin_id, user_id


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
        conn = sqlite3.connect(prompts_db)
        conn.execute(
            """
            INSERT INTO prompts (original_prompt, processed_at, model_used, created_by)
            VALUES ('test prompt', ?, 'manual', ?)
            """,
            (datetime.utcnow().isoformat(), victim_id),
        )
        conn.commit()
        conn.close()

        token = _manual_token("deleteme", victim_id, "user")
        delete_resp = client.request(
            "DELETE",
            "/api/v1/user/account",
            json={"password": "delete123", "confirm": True},
            headers=_auth_headers(token),
        )
        assert delete_resp.status_code == 200, delete_resp.text

        conn = sqlite3.connect(users_db)
        assert (
            conn.execute(
                "SELECT COUNT(*) FROM users WHERE username='deleteme'"
            ).fetchone()[0]
            == 0
        )
        audit = conn.execute("SELECT dump_path FROM account_deletion_audit").fetchone()
        conn.close()
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

        conn = sqlite3.connect(users_db)
        stored_hash = conn.execute(
            "SELECT password_hash FROM users WHERE id=?", (user_id,)
        ).fetchone()[0]
        conn.close()
        assert user_service.verify_password("AnotherPass!9", stored_hash)

        delete_resp = client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers=headers,
        )
        assert delete_resp.status_code == 204
