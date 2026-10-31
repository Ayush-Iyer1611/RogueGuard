# Findings Register — Synthetic Demonstration

> These are findings in the seeded local training scenario, not findings from a real campus or cloud environment.

| ID | Principal | Finding | Severity in demo | Evidence | Demonstrated remediation | Retest |
|---|---|---|---|---|---|---|
| RG-SYN-001 | `svc-results-export@campus-demo.iam` | Three roles exceed the declared requirement for exporting approved result reports | Critical (illustrative heuristic) | Seed record shows one required role and four granted roles | Retain `storage.objectViewer`, remove the three excess roles in the local model, and quarantine the synthetic identity | Confirm excess list is empty, status is QUARANTINED, and audit record contains before/after state |

## Interpretation

- Severity is the application's illustrative risk classification, not a calibrated likelihood or provider rating.
- The record is synthetic and intentionally seeded for demonstration.
- No unauthorised actor, policy-change event, or malicious intent has been independently identified.
- A production finding would require verified identity, policy, ownership, resource-scope, and event evidence.

## Evidence capture checklist

- [ ] Baseline inventory screenshot.
- [ ] Expanded synthetic identity showing granted and required roles.
- [ ] Containment confirmation and resulting account state.
- [ ] Audit record with before/after details.
- [ ] Test output from the current test suite.
- [ ] Record any cloud operations that remain unverified.
