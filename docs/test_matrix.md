# Test Matrix — RogueGuard

## A. Project review tests (T01–T08)

| ID | Test | Expected result | Evidence to capture | Result |
|---|---|---|---|---|
| T01 | Inventory identifies principal, roles, owner and resource scope | Account details are visible and attributable to synthetic fixture source | Identity explorer screenshot | Pending manual execution |
| T02 | Each retained permission has a documented purpose | Required roles and baseline rationale are visible | Baseline and binding screenshot | Pending manual execution |
| T03 | Contain a synthetic identity with excess grants | Excess grants removed in local simulation; status follows chosen response | Before/after screenshots | Pending manual execution |
| T04 | Verify required and unrelated access after response | State matches reviewed policy diff; verification result is explicit | Policy diff and verification screenshot | Pending manual execution |
| T05 | Containment preserves evidence | Case timeline and exported event record preserve before/after state | Case timeline and JSON export | Pending manual execution |
| T06 | Trigger a controlled unexpected error | Safe failure; no real state changed and no sensitive data exposed | Redacted output/log | Pending manual execution |
| T07 | Inspect source, output and logs for sensitive data | No real credentials or personal data present; export redaction is enabled where applicable | Sanitised source/export review | Pending manual execution |
| T08 | Repeat the complete test set | Results are reproducible; limitations and environment recorded | Completed test matrix | Pending manual execution |

## B. Automated v0.9 regression coverage

The following behaviours are covered by `tests/test_prototype.py`. The CI run must pass on the commit intended for review; the table does not replace manual T01–T08 evidence.

| ID | Automated behaviour | Test coverage |
|---|---|---|
| V09-01 | Load valid scenario fixture and resource-level bindings | Yes |
| V09-02 | Reject malformed fixtures before mutation | Yes |
| V09-03 | Reject bindings to unknown principals/resources | Yes |
| V09-04 | Detect excess grants, broad scope, missing owner and stale review | Yes |
| V09-05 | Findings include evidence, severity, confidence and stable IDs | Yes |
| V09-06 | Reject invalid finding state transitions | Yes |
| V09-07 | Record analyst state changes in finding and case history | Yes |
| V09-08 | Require an independent reviewer | Yes |
| V09-09 | Prevent execution of a pending or rejected plan | Yes |
| V09-10 | Simulate permission reduction and verify the resulting snapshot | Yes |
| V09-11 | Keep quarantine separate from permission reduction | Yes |
| V09-12 | Require excess permissions to be removed before reactivation | Yes |
| V09-13 | Preserve case export as JSON, CSV and SHA-256 manifest | Yes |
| V09-14 | Redact synthetic principal identifiers when requested | Yes |
| V09-15 | Provide scenario-level summary counts | Yes |

## C. Manual error and safety scenarios

| ID | Scenario | Expected safe result |
|---|---|---|
| M01 | Attempt to approve a plan as its creator | Approval rejected |
| M02 | Change an identity after creating a dry-run plan, then execute stale plan | Plan execution rejected because current state differs |
| M03 | Attempt to reactivate identity with excess bindings | Reactivation plan rejected |
| M04 | Reject a proposed response plan | No simulated state change occurs |
| M05 | Reload a scenario that already has case history | Reload rejected so case history is not silently discarded |
| M06 | Export case evidence with redaction | Principal identifiers and token-like values are masked; manifest clearly warns hashes are not immutable storage |

**Important:** Automated regression coverage is not proof of a secure production system. Mark T01–T08 PASS only after performing the manual checks and capturing evidence. Cloud-side tests require explicit sandbox access and mentor approval.
