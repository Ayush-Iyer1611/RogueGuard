"""Local authentication for the RogueGuard synthetic workbench.

Passwords are salted PBKDF2-HMAC-SHA256 hashes. All SQLite values are bound
through placeholders. This is a local demo login layer, not production SSO.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any

DB = Path(__file__).with_name("rogueguard.db")
PBKDF2_ITERATIONS = 600_000
MAX_LOGIN_FAILURES = 5
LOCKOUT_SECONDS = 300
USERNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{2,31}$")
DUMMY_SALT = bytes.fromhex("efb2c1a6549a7f21d7803ab4b4e872c3")


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    return con


def initialize_auth() -> None:
    """Create local-auth tables without changing the synthetic identity tables."""
    with _connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS rg_local_users (
                username TEXT PRIMARY KEY,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'ADMIN',
                created_at INTEGER NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS rg_login_attempts (
                username TEXT PRIMARY KEY,
                failures INTEGER NOT NULL DEFAULT 0,
                locked_until INTEGER NOT NULL DEFAULT 0
            )
            """
        )


def _normalise_username(username: str) -> str:
    return str(username).strip().casefold()


def _derive(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )


def user_count() -> int:
    initialize_auth()
    with _connect() as con:
        row = con.execute("SELECT COUNT(*) AS total FROM rg_local_users").fetchone()
        return int(row["total"])


def create_first_user(username: str, password: str, confirmation: str) -> str:
    """Create the first local operator account; public registration is disabled."""
    initialize_auth()
    clean_username = _normalise_username(username)
    if not USERNAME_RE.fullmatch(clean_username):
        raise ValueError("Use 3–32 characters: letters, numbers, dot, underscore or hyphen.")
    if not isinstance(password, str) or len(password) < 12:
        raise ValueError("Use a password with at least 12 characters.")
    if len(password.encode("utf-8")) > 256:
        raise ValueError("Password is too long.")
    if not hmac.compare_digest(password, str(confirmation)):
        raise ValueError("The password confirmation does not match.")

    salt = secrets.token_bytes(16)
    password_hash = _derive(password, salt).hex()
    with _connect() as con:
        con.execute("BEGIN IMMEDIATE")
        current = con.execute("SELECT COUNT(*) AS total FROM rg_local_users").fetchone()
        if int(current["total"]) != 0:
            raise ValueError("Initial setup is already complete. Sign in instead.")
        con.execute(
            """
            INSERT INTO rg_local_users
                (username, password_salt, password_hash, role, created_at)
            VALUES (?, ?, ?, 'ADMIN', ?)
            """,
            (clean_username, salt.hex(), password_hash, int(time.time())),
        )
    return clean_username


def authenticate(username: str, password: str) -> dict[str, Any] | None:
    """Authenticate a local user; failures use one generic result and lock out briefly."""
    initialize_auth()
    clean_username = _normalise_username(username)
    if not clean_username or len(clean_username) > 64 or not isinstance(password, str) or len(password.encode("utf-8")) > 512:
        return None

    now = int(time.time())
    with _connect() as con:
        attempt = con.execute(
            "SELECT failures, locked_until FROM rg_login_attempts WHERE username = ?",
            (clean_username,),
        ).fetchone()
        failures = int(attempt["failures"]) if attempt else 0
        locked_until = int(attempt["locked_until"]) if attempt else 0
        if locked_until > now:
            return None

        user = con.execute(
            """
            SELECT username, password_salt, password_hash, role
            FROM rg_local_users
            WHERE username = ?
            """,
            (clean_username,),
        ).fetchone()

        if user is None:
            # Spend a comparable amount of CPU on unknown usernames.
            _derive(password, DUMMY_SALT)
            valid = False
        else:
            candidate = _derive(password, bytes.fromhex(user["password_salt"]))
            valid = hmac.compare_digest(candidate.hex(), user["password_hash"])

        if not valid:
            failures += 1
            lock_until = now + LOCKOUT_SECONDS if failures >= MAX_LOGIN_FAILURES else 0
            con.execute(
                """
                INSERT INTO rg_login_attempts (username, failures, locked_until)
                VALUES (?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    failures = excluded.failures,
                    locked_until = excluded.locked_until
                """,
                (clean_username, failures, lock_until),
            )
            return None

        con.execute("DELETE FROM rg_login_attempts WHERE username = ?", (clean_username,))
        return {"username": user["username"], "role": user["role"]}


def clear_auth_state(session_state) -> None:
    """Remove app-local authentication attributes from a Streamlit session."""
    for key in ("rg_auth_user", "rg_auth_role"):
        session_state.pop(key, None)
