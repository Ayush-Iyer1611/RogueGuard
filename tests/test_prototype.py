import json
import tempfile
import unittest
from pathlib import Path

import prototype


class TestRogueGuardV09(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_db = prototype.DB
        self.old_exports = prototype.EXPORT_DIR
        prototype.DB = Path(self.temp.name) / "test.db"
        prototype.EXPORT_DIR = Path(self.temp.name) / "exports"
        prototype.initialize_prototype()
        prototype.load_scenario("overprivileged-exporter")
        self.scenario = "overprivileged-exporter"
        self.principal = "svc-results-export@campus-demo.iam"
        self.findings = prototype.analyze_scenario(self.scenario)

    def tearDown(self):
        prototype.DB = self.old_db
        prototype.EXPORT_DIR = self.old_exports
        self.temp.cleanup()

    def _excess_finding_ids(self):
        return [f["finding_id"] for f in self.findings
                if f["principal"] == self.principal and f["rule_id"] == "EXCESS_ROLE"]

    def test_fixture_loads_and_contains_resource_bindings(self):
        identity = prototype.get_identity(self.scenario, self.principal)
        self.assertEqual(identity["identity_type"], "SERVICE_ACCOUNT")
        self.assertEqual(len(identity["bindings"]), 4)
        self.assertEqual(identity["baseline"]["approval_state"], "APPROVED")

    def test_analyser_finds_excess_unknown_owner_and_stale_review(self):
        rules = {f["rule_id"] for f in self.findings}
        self.assertIn("EXCESS_ROLE", rules)
        self.assertIn("MISSING_OWNER", rules)
        self.assertIn("STALE_ACCESS_REVIEW", rules)
        self.assertIn("BROAD_RESOURCE_SCOPE", rules)

    def test_finding_has_explainable_evidence_and_confidence(self):
        finding = next(f for f in self.findings if f["rule_id"] == "EXCESS_ROLE")
        self.assertIn("binding_source", finding["evidence"])
        self.assertIn(finding["severity"], {"LOW", "MEDIUM", "HIGH", "CRITICAL"})
        self.assertIn(finding["confidence"], {"LOW", "MEDIUM", "HIGH"})
        self.assertTrue(finding["finding_id"].startswith("RG-"))

    def test_finding_transition_rejects_invalid_state_change(self):
        finding = self.findings[0]
        with self.assertRaises(ValueError):
            prototype.update_finding_status(
                finding["finding_id"], "RETESTED", "analyst", "invalid direct transition"
            )

    def test_plan_requires_two_person_approval_and_executes_permission_reduction(self):
        fids = self._excess_finding_ids()
        case_id = prototype.create_case(
            self.scenario, "Overprivileged export identity", "analyst", fids
        )
        plan_id = prototype.create_action_plan(
            case_id, self.principal, "REMOVE_EXCESS",
            "Remove grants not present in approved baseline.", "analyst", fids
        )
        with self.assertRaises(ValueError):
            prototype.approve_action_plan(plan_id, "analyst", "APPROVED", "self-approval")
        with self.assertRaises(ValueError):
            prototype.execute_action_plan(plan_id, "operator")
        prototype.approve_action_plan(plan_id, "reviewer", "APPROVED", "Reviewed policy diff.")
        result = prototype.execute_action_plan(plan_id, "operator")
        self.assertTrue(result["simulated"])
        verified = prototype.verify_action_plan(plan_id, "verifier")
        self.assertEqual(verified["result"], "VERIFIED")
        updated = prototype.get_identity(self.scenario, self.principal)
        self.assertEqual(len(updated["bindings"]), 1)
        self.assertEqual(updated["lifecycle_state"], "ACTIVE")
        self.assertTrue(all(f["status"] == "RESOLVED"
                            for f in prototype.list_findings(self.scenario)
                            if f["principal"] == self.principal and f["rule_id"] == "EXCESS_ROLE"))

    def test_quarantine_is_separate_from_permission_removal(self):
        case_id = prototype.create_case(
            self.scenario, "Quarantine review", "analyst", self._excess_finding_ids()
        )
        before = prototype.get_identity(self.scenario, self.principal)
        plan_id = prototype.create_action_plan(
            case_id, self.principal, "QUARANTINE",
            "Isolate synthetic identity pending review.", "analyst"
        )
        prototype.approve_action_plan(plan_id, "reviewer", "APPROVED", "Approved isolation.")
        prototype.execute_action_plan(plan_id, "operator")
        verified = prototype.verify_action_plan(plan_id, "verifier")
        after = prototype.get_identity(self.scenario, self.principal)
        self.assertEqual(verified["result"], "VERIFIED")
        self.assertEqual(after["lifecycle_state"], "QUARANTINED")
        self.assertEqual(len(after["bindings"]), len(before["bindings"]))

    def test_rejecting_plan_prevents_execution(self):
        case_id = prototype.create_case(
            self.scenario, "Rejected response", "analyst", self._excess_finding_ids()
        )
        plan_id = prototype.create_action_plan(
            case_id, self.principal, "REMOVE_EXCESS", "Test rejection.", "analyst"
        )
        prototype.approve_action_plan(plan_id, "reviewer", "REJECTED", "Need owner confirmation.")
        with self.assertRaises(ValueError):
            prototype.execute_action_plan(plan_id, "operator")

    def test_export_creates_json_csv_and_sha256_manifest(self):
        fids = self._excess_finding_ids()
        case_id = prototype.create_case(self.scenario, "Evidence case", "analyst", fids)
        paths = prototype.export_case_bundle(case_id, self.temp.name)
        for path in paths.values():
            self.assertTrue(Path(path).exists())
        manifest = json.loads(Path(paths["manifest"]).read_text())
        self.assertEqual(manifest["algorithm"], "SHA-256")
        self.assertEqual(len(manifest["files"]), 2)
        payload = json.loads(Path(paths["json"]).read_text())
        self.assertEqual(payload["case"]["case_id"], case_id)
        self.assertTrue(payload["simulation_notice"].startswith("Synthetic local simulation"))

    def test_malformed_fixture_is_rejected_before_database_mutation(self):
        fixture = Path(self.temp.name) / "bad.json"
        fixture.write_text(json.dumps({
            "scenario_id": "bad", "name": "Bad", "version": "1",
            "resources": [], "identities": [{"principal": "x"}], "bindings": []
        }))
        with self.assertRaises(ValueError):
            prototype.load_scenario(str(fixture))
        self.assertFalse(any(s["scenario_id"] == "bad" for s in prototype.list_scenarios()))

    def test_unknown_principal_binding_is_rejected(self):
        fixture = Path(self.temp.name) / "bad-ref.json"
        fixture.write_text(json.dumps({
            "scenario_id": "bad-ref", "name": "Bad", "version": "1",
            "resources": [{"resource_id": "r", "resource_type": "bucket", "name": "R"}],
            "identities": [{"principal": "known", "identity_type": "SERVICE_ACCOUNT",
                            "environment": "demo", "lifecycle_state": "ACTIVE"}],
            "bindings": [{"principal": "unknown", "role": "storage.admin",
                          "resource_id": "r", "source": "fixture"}]
        }))
        with self.assertRaises(ValueError):
            prototype.load_scenario(str(fixture))

    def test_finding_state_changes_are_audited(self):
        finding_id = self._excess_finding_ids()[0]
        case_id = prototype.create_case(
            self.scenario, "Finding audit case", "analyst", [finding_id]
        )
        prototype.update_finding_status(
            finding_id, "ACCEPTED", "reviewer", "Owner confirmed temporary exception."
        )
        history = prototype.list_finding_history(finding_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["old_status"], "TRIAGED")
        self.assertEqual(history[0]["new_status"], "ACCEPTED")
        events = prototype.list_events(case_id)
        self.assertTrue(any(event["event_type"] == "FINDING_STATE_CHANGE" for event in events))

    def test_quarantine_requires_remediation_before_reactivation(self):
        finding_ids = self._excess_finding_ids()
        case_id = prototype.create_case(
            self.scenario, "Quarantine then remediate", "analyst", finding_ids
        )
        quarantine = prototype.create_action_plan(
            case_id, self.principal, "QUARANTINE", "Contain pending review.", "analyst"
        )
        prototype.approve_action_plan(quarantine, "reviewer", "APPROVED", "Approved quarantine.")
        prototype.execute_action_plan(quarantine, "operator")
        self.assertEqual(prototype.verify_action_plan(quarantine, "verifier")["result"], "VERIFIED")
        self.assertEqual(
            prototype.get_identity(self.scenario, self.principal)["lifecycle_state"],
            "QUARANTINED"
        )
        self.assertTrue(any(
            f["status"] == "CONTAINED" for f in prototype.list_findings(self.scenario)
            if f["principal"] == self.principal and f["rule_id"] == "EXCESS_ROLE"
        ))
        with self.assertRaises(ValueError):
            prototype.create_action_plan(
                case_id, self.principal, "REACTIVATE",
                "Attempt early reactivation.", "analyst"
            )
        removal = prototype.create_action_plan(
            case_id, self.principal, "REMOVE_EXCESS",
            "Remove excess grants while still quarantined.", "analyst", finding_ids
        )
        prototype.approve_action_plan(removal, "reviewer2", "APPROVED", "Approved role reduction.")
        prototype.execute_action_plan(removal, "operator")
        self.assertEqual(prototype.verify_action_plan(removal, "verifier")["result"], "VERIFIED")
        reactivate = prototype.create_action_plan(
            case_id, self.principal, "REACTIVATE",
            "Reactivate after excess grants have been removed.", "analyst"
        )
        prototype.approve_action_plan(reactivate, "reviewer3", "APPROVED", "Baseline confirmed.")
        prototype.execute_action_plan(reactivate, "operator")
        self.assertEqual(prototype.verify_action_plan(reactivate, "verifier")["result"], "VERIFIED")
        self.assertEqual(
            prototype.get_identity(self.scenario, self.principal)["lifecycle_state"],
            "ACTIVE"
        )

    def test_evidence_export_redacts_principals(self):
        case_id = prototype.create_case(
            self.scenario, "Redacted evidence", "analyst", self._excess_finding_ids()
        )
        paths = prototype.export_case_bundle(case_id, self.temp.name, redact=True)
        payload = Path(paths["json"]).read_text()
        self.assertNotIn("svc-results-export@campus-demo.iam", payload)
        self.assertIn("[REDACTED-PRINCIPAL]", payload)
        self.assertNotIn("project:campus-demo", payload)
        self.assertIn("[REDACTED-RESOURCE]", payload)
        self.assertTrue(any(
            identity.get("baseline") and "required_roles" in identity["baseline"]
            for identity in json.loads(payload)["identities"]
        ))

    def test_plan_rejects_findings_for_another_principal(self):
        target_finding = self._excess_finding_ids()[0]
        other_finding = next(
            f["finding_id"] for f in self.findings
            if f["principal"] != self.principal
        )
        case_id = prototype.create_case(
            self.scenario, "Scoped response case", "analyst", [target_finding]
        )
        with self.assertRaises(ValueError):
            prototype.create_action_plan(
                case_id, self.principal, "REMOVE_EXCESS",
                "Try to attach unrelated finding.", "analyst", [other_finding]
            )

    def test_stale_plan_is_rejected_after_state_changes(self):
        finding_ids = self._excess_finding_ids()
        case_id = prototype.create_case(
            self.scenario, "Stale plan case", "analyst", finding_ids
        )
        plan_id = prototype.create_action_plan(
            case_id, self.principal, "REMOVE_EXCESS",
            "Test stale snapshot protection.", "analyst", finding_ids
        )
        prototype.approve_action_plan(plan_id, "reviewer", "APPROVED", "Reviewed original state.")
        with prototype._connect() as con:
            con.execute(
                "UPDATE rg_identities SET owner=? WHERE scenario_id=? AND principal=?",
                ("Changed Owner", self.scenario, self.principal)
            )
        with self.assertRaises(ValueError):
            prototype.execute_action_plan(plan_id, "operator")

    def test_dashboard_summary_reports_loaded_state(self):
        summary = prototype.dashboard_summary(self.scenario)
        self.assertEqual(summary["identities"], 4)
        self.assertGreaterEqual(summary["findings"], 5)
        self.assertGreaterEqual(summary["critical"], 1)


if __name__ == "__main__":
    unittest.main()
