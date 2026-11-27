# Final Prototype and Submission Plan

**Project:** RogueGuard  
**Current code baseline:** v0.1  
**Last prototype review:** v0.9  
**Final submission release:** v1.0

This document defines the remaining delivery path. It is intentionally finite: one final prototype review, followed by a feature freeze and final submission release. It does not commit the project to becoming a production cloud-security platform.

## 1. Release strategy

| Stage | Meaning | Rule |
|---|---|---|
| v0.1 — Foundation | Current checked-in implementation | Preserve as the verified starting point |
| v0.9 — Final prototype | Last reviewable prototype | Implement only the agreed acceptance scope; demonstrate end to end |
| v1.0 — Final product | Submission-ready release | No new feature cycle; fix defects, complete tests, package evidence, and document limitations |

After the v0.9 review, new ideas go into a post-submission backlog unless they are required to fix a defect or satisfy a final acceptance criterion.

## 2. v0.9 — Final prototype scope

The final prototype should provide one coherent local analyst workflow using synthetic data.

### 2.1 Required workflow

1. Load a versioned synthetic scenario.
2. Inspect an identity, its owner, purpose, environment, resources, and permission bindings.
3. Review structured findings and understand their evidence, severity, and confidence.
4. Compare the observed policy state with the declared baseline.
5. Generate a dry-run response plan and inspect the exact before/after difference.
6. Choose permission reduction and identity quarantine as distinct actions.
7. Record the operator's reason and explicit confirmation.
8. Apply the response to the local simulator only.
9. Verify the resulting state against the proposed plan.
10. Export a case bundle containing the relevant snapshots, findings, actions, approvals, audit events, and integrity manifest.

### 2.2 Required feature set

| ID | Feature | Acceptance condition |
|---|---|---|
| P09-01 | Synthetic fixture import | A documented fixture can be loaded and validated; malformed fields are rejected safely |
| P09-02 | Identity/resource model | Each permission binding identifies a principal, role, resource, and source |
| P09-03 | Baseline provenance | Expected access records include purpose, owner, version, rationale, and review state |
| P09-04 | Finding engine | At minimum, detects excess grants, missing grants, unknown roles, and missing ownership where fixture data supports the rule |
| P09-05 | Explainable findings | Each finding has a stable ID, rule ID, evidence, affected identity/resource, severity, confidence, and recommended next step |
| P09-06 | Finding review | Findings can be searched/filtered and moved through a controlled lifecycle without deleting the original evidence |
| P09-07 | Policy diff | The user can inspect exactly what changed between baseline/current state and proposed state |
| P09-08 | Dry-run response | A plan can be generated without changing the active synthetic dataset |
| P09-09 | Separate response controls | Permission reduction and identity quarantine are independent, explicit actions |
| P09-10 | Action reason and confirmation | A response requires an operator reason and confirmation |
| P09-11 | Post-action verification | The system reports VERIFIED, FAILED, or NOT VERIFIED against the intended result |
| P09-12 | Reactivation gate | Reactivation requires a review decision; removed excess roles are not silently restored |
| P09-13 | Case and audit context | Findings, action plans, approvals, and events can be associated with a case ID |
| P09-14 | Evidence export | JSON and CSV case exports are available, with a SHA-256 manifest and redaction |
| P09-15 | Reset safety | Demo reset cannot silently destroy the only copy of relevant evidence; export/backup or explicit acknowledgement is required |
| P09-16 | Automated verification | New rules, transitions, rollback, malformed fixtures, exports, and reset safety have tests |
| P09-17 | Operator usability | A reviewer can complete the workflow without editing source code or manually changing SQLite records |

The identity relationship graph, advanced anomaly detection, real-time monitoring, and live cloud response are optional extensions. Do not sacrifice stability or evidence quality to add them.

## 3. v0.9 review demonstration

The review should use deterministic synthetic scenarios and follow this sequence:

1. **Show the system boundary:** explain that the current run is a local synthetic security workbench.
2. **Load a scenario:** show the identity inventory and the source of its synthetic baseline.
3. **Investigate a finding:** identify the excessive permission and show the evidence supporting the finding.
4. **Explain risk:** show the contributing factors, severity, and confidence; do not present a heuristic score as a probability.
5. **Plan the response:** show the policy diff and affected synthetic resources before executing anything.
6. **Approve and simulate:** enter an operator reason and choose the intended action.
7. **Verify:** demonstrate that the post-action state matches the plan, or show a clear failure/unverified state.
8. **Preserve evidence:** open the case timeline and export the evidence bundle.
9. **State limitations:** identify which operations are simulated, unsupported, or not verified in the assigned sandbox.

The review should prove not only that the happy path works, but also that invalid requests fail safely and preserve the original state.

## 4. v1.0 — Final product acceptance

v1.0 is the final academic submission build. It is not a claim of enterprise production readiness.

### Functional acceptance

- The agreed v0.9 workflow works from a fresh clone and a clean local database.
- All required features in the v0.9 scope are either implemented and tested or explicitly removed from the agreed scope with a recorded reason.
- No critical or high-severity known defect remains open without an explicit disposition.
- Invalid input, unsupported actions, and failed response simulations produce safe, explainable outcomes.
- The app never presents a simulated cloud action as a verified cloud change.

### Testing acceptance

- Run the full Python unit/database test suite.
- Run UI smoke tests for scenario load, finding review, plan preview, simulated response, verification, and evidence export.
- Execute applicable T01–T08 checks in `test_matrix.md`.
- Capture evidence for each executed test.
- Mark a test PASS only when the expected result was observed; use FAIL, BLOCKED, or NOT APPLICABLE where appropriate.
- Record environment details and any deviations from expected results.

### Documentation and submission acceptance

- Update the README to describe only implemented features as current.
- Keep architecture and threat-model diagrams aligned with the shipped code.
- Complete the findings register with evidence, impact, remediation, and retest outcome.
- Include setup, test, and demo instructions.
- Prepare a concise demo script and redacted screenshots.
- Include limitations, scope boundaries, unverified operations, and release recommendation.
- Verify that secrets, credentials, personal data, local databases, and sensitive unredacted evidence are not committed.
- Create a v1.0 release/tag only after acceptance checks are complete.

## 5. Cloud sandbox decision rule

Cloud integration must be treated as a separately verified capability.

- Use only the explicitly assigned and approved sandbox.
- Confirm the project, endpoint, permissions, service support, and exact operation before testing.
- Start with read-only operations.
- Keep all cloud writes disabled unless separately approved.
- Record the operation, time, environment, observed result, and evidence.
- Label each operation as SIMULATED, READ, WRITE, VERIFIED, FAILED, BLOCKED, or NOT SUPPORTED.
- If access or support is unavailable, keep the local simulation and document the limitation. Do not claim that cloud integration works.

A service being enabled or an API endpoint being reachable does not prove that a particular IAM, credentials, storage, secret, or logging operation is implemented and supported.

## 6. T01–T08 evidence tracker

Use the existing [test matrix](test_matrix.md). This tracker does not pre-mark any result as passed.

| Test | Final evidence expected | Result |
|---|---|---|
| T01 — Inventory | Identity, role, owner, and resource-scope view | Pending execution |
| T02 — Permission purpose | Baseline rationale and required/granted comparison | Pending execution |
| T03 — Containment | Before/after policy state and resulting identity status | Pending execution |
| T04 — Access verification | Required access retained in the simulator; unrelated access denied/removed as expected | Pending execution |
| T05 — Evidence preservation | Case audit event and exported evidence bundle | Pending execution |
| T06 — Controlled error | Safe failure with unchanged state and no sensitive data in output | Pending execution |
| T07 — Sensitive-data review | Source, logs, screenshots, and exports reviewed/redacted | Pending execution |
| T08 — Repeatability | Full test set rerun with recorded environment and outcomes | Pending execution |

## 7. Feature freeze and change control

After the v0.9 review:

- Freeze feature development.
- Fix reproducible defects and security/safety issues.
- Complete missing acceptance evidence.
- Improve documentation where reviewers found ambiguity.
- Do not add optional features unless required to meet an agreed acceptance criterion.
- Re-run the affected tests after every fix and the full suite before v1.0.

## 8. Final release decision

The v1.0 release decision should be one of:

- **READY FOR SUBMISSION:** required workflows, tests, documentation, and evidence are complete; all limitations are explicit.
- **READY WITH DOCUMENTED LIMITATIONS:** core local demonstration is complete, but a cloud operation is blocked or unsupported and accurately documented.
- **NOT READY:** critical workflow or evidence gaps remain.

The release report should explain the decision using observed test results and retained evidence, not assumptions.

---

**Delivery principle:** v0.9 is the last prototype. v1.0 is the final, tested, documented, and evidence-backed submission. After the final review, finish and stabilise; do not restart the feature roadmap.
