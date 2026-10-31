
import unittest

from core import (
    analyse_permissions,
    calculate_risk,
    get_risk_level,
    assess_account,
    remediate_permissions,
    access_decision,
)


class TestRogueGuardCore(unittest.TestCase):

    def setUp(self):
        self.account = {
            "principal": "svc-test-account",
            "granted_roles": [
                "storage.objectViewer",
                "storage.objectAdmin",
                "secretmanager.secretAccessor",
            ],
            "required_roles": [
                "storage.objectViewer",
            ],
            "status": "ACTIVE",
        }

    def test_excess_permissions_are_identified(self):
        result = analyse_permissions(
            self.account["granted_roles"],
            self.account["required_roles"],
        )

        self.assertEqual(
            result["excess_roles"],
            [
                "secretmanager.secretAccessor",
                "storage.objectAdmin",
            ],
        )

    def test_missing_permissions_are_identified(self):
        result = analyse_permissions(
            ["storage.objectViewer"],
            ["storage.objectViewer", "storage.objectCreator"],
        )

        self.assertEqual(
            result["missing_roles"],
            ["storage.objectCreator"],
        )

    def test_risk_score_is_calculated(self):
        score = calculate_risk(["storage.objectAdmin"])
        self.assertEqual(score, 56)

    def test_risk_score_is_capped_at_100(self):
        score = calculate_risk([
            "storage.admin",
            "iam.serviceAccountAdmin",
            "secretmanager.secretAccessor",
        ])

        self.assertEqual(score, 100)

    def test_risk_level_classification(self):
        self.assertEqual(get_risk_level(90), "CRITICAL")
        self.assertEqual(get_risk_level(60), "HIGH")
        self.assertEqual(get_risk_level(30), "MEDIUM")
        self.assertEqual(get_risk_level(10), "LOW")
        self.assertEqual(get_risk_level(0), "NONE")

    def test_account_assessment(self):
        result = assess_account(self.account)

        self.assertEqual(result["principal"], "svc-test-account")
        self.assertEqual(result["risk_score"], 100)
        self.assertEqual(result["risk_level"], "CRITICAL")

    def test_remediation_removes_excess_roles(self):
        result = remediate_permissions(
            self.account["granted_roles"],
            self.account["required_roles"],
        )

        self.assertEqual(result, ["storage.objectViewer"])

    def test_active_account_with_permission_is_allowed(self):
        result = access_decision(
            self.account,
            "storage.objectViewer",
        )

        self.assertTrue(result["allowed"])

    def test_ungranted_permission_is_denied(self):
        result = access_decision(
            self.account,
            "iam.serviceAccountAdmin",
        )

        self.assertFalse(result["allowed"])

    def test_quarantined_account_is_denied(self):
        quarantined = {
            "status": "QUARANTINED",
            "granted_roles": ["storage.objectViewer"],
        }

        result = access_decision(
            quarantined,
            "storage.objectViewer",
        )

        self.assertFalse(result["allowed"])


if __name__ == "__main__":
    unittest.main()
