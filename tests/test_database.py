
import json
import tempfile
import unittest
from pathlib import Path

import database

from core import access_decision


class TestRogueGuardDatabase(unittest.TestCase):

    def setUp(self):
        # Give every test its own temporary database.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_db = database.DB
        database.DB = Path(self.temp_dir.name) / "test_rogueguard.db"

        database.init_db()

    def tearDown(self):
        database.DB = self.original_db
        self.temp_dir.cleanup()

    def test_four_synthetic_accounts_are_seeded(self):
        accounts = database.get_accounts()
        self.assertEqual(len(accounts), 4)

    def test_containment_removes_excess_permissions(self):
        email = "svc-results-export@campus-demo.iam"

        account = database.get_account(email)
        required = json.loads(account["required_roles"])

        evidence = database.contain_account(email, required)

        updated = database.get_account(email)

        self.assertEqual(updated["status"], "QUARANTINED")
        self.assertEqual(json.loads(updated["roles"]), required)
        self.assertEqual(len(evidence["removed_roles"]), 3)

    def test_containment_preserves_before_and_after_evidence(self):
        email = "svc-results-export@campus-demo.iam"

        account = database.get_account(email)
        original_roles = json.loads(account["roles"])
        required = json.loads(account["required_roles"])

        database.contain_account(email, required)

        events = database.audit_rows()
        event = events[0]
        details = json.loads(event["details"])

        self.assertEqual(details["before"]["roles"], original_roles)
        self.assertEqual(details["after"]["roles"], required)
        self.assertEqual(event["outcome"], "SUCCESS")

    def test_quarantined_account_cannot_access_retained_role(self):
        email = "svc-results-export@campus-demo.iam"

        account = database.get_account(email)
        required = json.loads(account["required_roles"])

        database.contain_account(email, required)

        updated = database.get_account(email)

        simulated_account = {
            "status": updated["status"],
            "granted_roles": json.loads(updated["roles"]),
        }

        result = access_decision(
            simulated_account,
            "storage.objectViewer",
        )

        self.assertFalse(result["allowed"])
        self.assertEqual(
            result["reason"],
            "Account is not active.",
        )

    def test_reactivation_does_not_restore_excess_permissions(self):
        email = "svc-results-export@campus-demo.iam"

        account = database.get_account(email)
        required = json.loads(account["required_roles"])

        database.contain_account(email, required)
        database.restore_account(email)

        updated = database.get_account(email)

        self.assertEqual(updated["status"], "ACTIVE")
        self.assertEqual(json.loads(updated["roles"]), required)

        events = database.audit_rows()

        self.assertEqual(events[0]["event"], "STATUS_CHANGE")
        self.assertEqual(events[0]["outcome"], "REVIEW_REQUIRED")

    def test_invalid_containment_rolls_back(self):
        email = "svc-results-export@campus-demo.iam"

        original = database.get_account(email)

        with self.assertRaises(ValueError):
            database.contain_account(
                email,
                ["iam.serviceAccountAdmin"],
            )

        updated = database.get_account(email)

        self.assertEqual(updated["status"], original["status"])
        self.assertEqual(updated["roles"], original["roles"])

    def test_nonexistent_account_cannot_be_contained(self):
        with self.assertRaises(ValueError):
            database.contain_account(
                "unknown@campus-demo.iam",
                [],
            )


if __name__ == "__main__":
    unittest.main()
