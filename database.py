
"""RogueGuard SQLite persistence layer.

All records are synthetic training data.
No real cloud identities are modified.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB = Path(__file__).with_name("rogueguard.db")


SEED_ACCOUNTS = [
    {
        "email": "svc-library-reader@campus-demo.iam",
        "purpose": "Read approved library catalogue files",
        "required_roles": ["storage.objectViewer"],
        "roles": ["storage.objectViewer"],
        "resources": ["gs://campus-library-public"],
        "owner": "Library Systems",
    },
    {
        "email": "svc-results-export@campus-demo.iam",
        "purpose": "Export approved examination result reports",
        "required_roles": ["storage.objectViewer"],
        "roles": [
            "storage.objectViewer",
            "storage.objectAdmin",
            "secretmanager.secretAccessor",
            "iam.serviceAccountTokenCreator",
        ],
        "resources": ["gs://exam-results"],
        "owner": "Examination Office",
    },
    {
        "email": "svc-backup-agent@campus-demo.iam",
        "purpose": "Read backup metadata and write backup archives",
        "required_roles": [
            "storage.objectViewer",
            "storage.objectCreator",
        ],
        "roles": [
            "storage.objectViewer",
            "storage.objectCreator",
        ],
        "resources": ["gs://campus-backups"],
        "owner": "IT Operations",
    },
    {
    "email": "svc-reporting-old@campus-demo.iam",
    "purpose": "Legacy reporting integration (no active permissions)",
    "required_roles": [],
    "roles": [],
    "resources": ["project:campus-demo"],
    "owner": "Reporting Systems",
},
]


def connect():
    """Create a database connection."""

    con = sqlite3.connect(DB, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    """Create tables and seed demo accounts if the database is empty."""

    con = connect()

    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                email TEXT PRIMARY KEY,
                purpose TEXT,
                required_roles TEXT,
                roles TEXT,
                resources TEXT,
                owner TEXT,
                status TEXT DEFAULT 'ACTIVE'
            )
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event TEXT,
                principal TEXT,
                outcome TEXT,
                details TEXT
            )
        """)

        count = con.execute(
            "SELECT COUNT(*) FROM accounts"
        ).fetchone()[0]

        if count == 0:
            for account in SEED_ACCOUNTS:
                con.execute(
                    """
                    INSERT INTO accounts
                    (email, purpose, required_roles, roles,
                     resources, owner, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
                    """,
                    (
                        account["email"],
                        account["purpose"],
                        json.dumps(account["required_roles"]),
                        json.dumps(account["roles"]),
                        json.dumps(account["resources"]),
                        account["owner"],
                    ),
                )

        con.commit()

    finally:
        con.close()


def get_accounts():
    """Return all accounts as dictionaries."""

    con = connect()

    try:
        rows = con.execute(
            "SELECT * FROM accounts ORDER BY email"
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        con.close()


def get_account(email):
    """Return one account or None."""

    con = connect()

    try:
        row = con.execute(
            "SELECT * FROM accounts WHERE email = ?",
            (email,),
        ).fetchone()

        return dict(row) if row else None

    finally:
        con.close()


def log_event(event, principal, outcome, details):
    """Record an audit event with a UTC timestamp."""

    con = connect()

    try:
        con.execute(
            """
            INSERT INTO audit
            (timestamp, event, principal, outcome, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                event,
                principal,
                outcome,
                json.dumps(details),
            ),
        )

        con.commit()

    finally:
        con.close()


def contain_account(email, retained_roles):
    """
    Update a synthetic account and record before/after evidence.

    The caller must supply retained roles calculated by the
    security engine. This function does not call a cloud API.
    """

    con = connect()

    try:
        con.execute("BEGIN IMMEDIATE")

        row = con.execute(
            "SELECT * FROM accounts WHERE email = ?",
            (email,),
        ).fetchone()

        if row is None:
            raise ValueError("Account does not exist.")

        account = dict(row)

        if account["status"] != "ACTIVE":
            raise ValueError("Only active accounts can be contained.")

        original_roles = json.loads(account["roles"])
        required_roles = json.loads(account["required_roles"])

        retained = set(retained_roles)
        original = set(original_roles)

        # Prevent accidental permission grants or removal
        # of permissions outside the original grant set.
        if not retained.issubset(original):
            raise ValueError(
                "Containment cannot grant permissions that were not "
                "originally present."
            )

        if not retained.issubset(set(required_roles)):
            raise ValueError(
                "Containment cannot retain undeclared permissions."
            )

        removed_roles = sorted(original - retained)

        con.execute(
            """
            UPDATE accounts
            SET roles = ?, status = 'QUARANTINED'
            WHERE email = ?
            """,
            (json.dumps(sorted(retained)), email),
        )

        evidence = {
            "before": {
                "roles": original_roles,
                "status": account["status"],
            },
            "after": {
                "roles": sorted(retained),
                "status": "QUARANTINED",
            },
            "removed_roles": removed_roles,
            "required_roles": required_roles,
        }

        con.execute(
            """
            INSERT INTO audit
            (timestamp, event, principal, outcome, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                "CONTAINMENT",
                email,
                "SUCCESS",
                json.dumps(evidence),
            ),
        )

        con.commit()
        return evidence

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def restore_account(email):
    """Reactivate an account without restoring removed permissions."""

    con = connect()

    try:
        con.execute("BEGIN IMMEDIATE")

        row = con.execute(
            "SELECT * FROM accounts WHERE email = ?",
            (email,),
        ).fetchone()

        if row is None:
            raise ValueError("Account does not exist.")

        account = dict(row)

        if account["status"] != "QUARANTINED":
            raise ValueError("Only quarantined accounts can be reactivated.")

        current_roles = json.loads(account["roles"])

        con.execute(
            """
            UPDATE accounts
            SET status = 'ACTIVE'
            WHERE email = ?
            """,
            (email,),
        )

        details = {
            "roles_retained": current_roles,
            "old_permissions_restored": False,
            "review_required": True,
        }

        con.execute(
            """
            INSERT INTO audit
            (timestamp, event, principal, outcome, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                "STATUS_CHANGE",
                email,
                "REVIEW_REQUIRED",
                json.dumps(details),
            ),
        )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()


def audit_rows():
    """Return the latest 100 audit events."""

    con = connect()

    try:
        rows = con.execute(
            "SELECT * FROM audit ORDER BY id DESC LIMIT 100"
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        con.close()

def reset_demo_data():
    """
    Reset the local synthetic environment to its baseline state.

    Deletes all existing synthetic account changes and audit events,
    then recreates the four seed accounts.
    """

    con = connect()

    try:
        con.execute("BEGIN IMMEDIATE")

        con.execute("DELETE FROM audit")
        con.execute("DELETE FROM accounts")

        for account in SEED_ACCOUNTS:
            con.execute(
                """
                INSERT INTO accounts
                (email, purpose, required_roles, roles,
                 resources, owner, status)
                VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
                """,
                (
                    account["email"],
                    account["purpose"],
                    json.dumps(account["required_roles"]),
                    json.dumps(account["roles"]),
                    json.dumps(account["resources"]),
                    account["owner"],
                ),
            )

        con.commit()

    except Exception:
        con.rollback()
        raise

    finally:
        con.close()
