# Final Prototype and Submission Plan

**Project:** RogueGuard  
**Historical foundation:** v0.1  
**Current workbench:** v0.9 final-prototype implementation  
**Last prototype review target:** v0.9  
**Final submission release:** v1.0

This is the finite delivery plan for the last review and final submission. The current v0.9 workbench has implemented the central analyst workflow in a local synthetic environment. The remaining work is validation, closing acceptance gaps, and packaging evidence—not unlimited feature expansion.

## 1. Release strategy

| Stage | Meaning | Rule |
|---|---|---|
| v0.1 — Foundation | Original synthetic permission-audit and containment simulator | Historical starting point; retain its core tests and behaviour |
| v0.9 — Final prototype | Current review candidate | Complete the acceptance scope below, demonstrate it end to end, and collect reviewer feedback |
| v1.0 — Final product | Final academic submission | Freeze features; correct defects; complete tests, documentation, evidence, report, and demo |

After the v0.9 review, new ideas move to a post-submission backlog unless they are required to fix a defect or meet an agreed acceptance criterion.

## 2. Current v0.9 implementation status

The following features are present in the current branch. They still require local end-to-end review and evidence capture.

| Capability | Current status | Evidence / code |
|---|---|---|
| Versioned synthetic fixtures | Implemented | `fixtures/scenarios/*.json`, fixture validation in `prototype.py` |
| Identity/resource/binding model | Implemented | Identity, resource, baseline, relationship, and role-binding tables |
| Baseline provenance fields | Implemented | Version, owner, rationale, approval state and required-role list in fixtures |
| Rule-based findings | Implemented | Excess, missing, unknown role, broad scope, missing owner, stale review, invalid review date |
| Explainable finding lifecycle | Implemented | Stable IDs, rule, resource, evidence, severity, confidence, recommendation and state |
| Finding search and filters | Implemented | State, severity, owner, identity and rule search in Streamlit |
| Identity relationship view | Implemented | Synthetic fixture relationship graph; no live discovery or graph traversal |
| Dry-run response plan | Implemented | Before/after snapshot with binding-level policy comparison |
| Independent reviewer decision | Implemented | Reviewer label must differ from creator; labels are not enterprise-authenticated |
| Separate response actions | Implemented | Remove excess permissions, quarantine, and gated reactivation |
| Stale-plan protection | Implemented | Execute is rejected when current snapshot differs from reviewed plan |
| Post-action verification | Implemented | VERIFIED/FAILED comparison against expected snapshot |
| Case and decision history | Implemented | Case timeline, approval events, finding transition history |
| Evidence export | Implemented | JSON, CSV, SHA-256 manifest, optional principal/resource/token-like redaction |
| Reset/evidence protection | Partially implemented | UI has no destructive reset; scenario reload with existing case history is rejected |
| Automated tests and syntax check | Implemented in CI | `tests/test_core.py`, `tests/test_database.py`, `tests/test_prototype.py`; CI compiles modules and runs unittest |

### Remaining v0.9 gaps

- Run the Streamlit interface locally and walk through the entire operator journey.
- Capture manual T01–T08 evidence; CI tests do not replace screenshots or observed UI behaviour.
- Verify case exports are readable and properly redacted for every scenario.
- Review invalid inputs and unexpected errors from the UI, not only the Python functions.
- Confirm the final test matrix and findings register match the final checked-in code.
- Add a clean-clone walkthrough and record Python/Streamlit versions for the review environment.

The following remain deliberately outside v0.9 unless the review requires them: live cloud discovery/writes, credential revocation, authenticated enterprise approvers, immutable log storage, advanced anomaly detection, full transitive attack-path analysis, real-time monitoring, and multi-tenant production controls.

## 3. v0.9 — final prototype acceptance scope

The final prototype should provide one coherent local analyst workflow using synthetic data.

### 3.1 Required workflow

1. Load a versioned synthetic scenario.
2. Inspect an identity, owner, purpose, environment, resources, bindings, and declared baseline.
3. Run detection rules and review structured findings.
4. Inspect evidence, severity, confidence, and recommended next action.
5. Create a case from selected findings.
6. Generate a dry-run response plan and inspect the exact before/after bindings and impact summary.
7. Select permission reduction, quarantine, or eligible reactivation as distinct actions.
8. Record the operator's reason and obtain independent reviewer approval.
9. Execute the action against the local synthetic simulator only.
10. Verify the resulting state and export a case evidence bundle.

### 3.2 Acceptance criteria

| ID | Feature | Acceptance condition |
|---|---|---|
| P09-01 | Synthetic fixture import | Documented fixtures load; malformed fields and unknown references are rejected safely |
| P09-02 | Identity/resource model | Each binding identifies principal, role, resource, source, and optional condition/inheritance metadata |
| P09-03 | Baseline context | Expected access contains purpose, owner, version, rationale, approval state, and required roles |
| P09-04 | Finding engine | Detects excess/missing grants, unknown roles, broad scope, missing owner, and stale/invalid review metadata |
| P09-05 | Explainable findings | Stable finding ID, rule ID, principal/resource, evidence, severity, confidence, and recommendation |
| P09-06 | Finding review | Search/filter by state, severity, owner and identity/rule; controlled lifecycle; state changes are audited |
| P09-07 | Policy diff | Reviewer can inspect exact before/after identity and role-binding snapshots before execution |
| P09-08 | Dry-run response | Plan creation does not mutate the active identity/bindings |
| P09-09 | Separate response controls | Permission reduction, quarantine, and reactivation are independent actions |
| P09-10 | Reason and confirmation | Plan requires operator reason; approval and execution require explicit actions |
| P09-11 | Independent approval | Reviewer must differ from plan creator; rejected or pending plans cannot execute |
| P09-12 | Stale-plan protection | Execution is rejected if current state differs from the reviewed precondition |
| P09-13 | Reactivation gate | Only quarantined identities with no excess bindings can be reactivated; removed grants are not restored |
| P09-14 | Post-action verification | Expected state is compared with actual local state; result is VERIFIED or FAILED |
| P09-15 | Case and audit context | Findings, plans, approvals, and response events are linked to a case ID |
| P09-16 | Evidence export | JSON and CSV exports plus SHA-256 manifest; redaction option is available |
| P09-17 | Evidence/reset safety | No UI action silently clears case history; scenario reload is blocked where case history exists |
| P09-18 | Automated verification | Unit tests cover rules, transitions, approvals, stale plans, rollback/rejection, exports and fixture validation |
| P09-19 | Operator usability | Reviewer can perform the core workflow from Streamlit without editing Python or SQLite manually |

## 4. v0.9 review demonstration

Use a deterministic synthetic scenario and follow this sequence:

1. **State the boundary:** this is a local synthetic identity-security workbench.
2. **Load a scenario:** show the identity inventory, resource scope, and baseline provenance.
3. **Investigate a finding:** show the excessive grant, rule ID, evidence, severity, confidence, and recommendation.
4. **Review relationships:** explain that any graph edges come from synthetic fixture assertions.
5. **Open a case:** associate the relevant finding(s) with an investigation.
6. **Plan a response:** show before/after bindings and explain the expected impact.
7. **Approve:** demonstrate that the plan creator cannot approve their own plan.
8. **Simulate:** execute only after approval; show that no cloud resource is touched.
9. **Verify:** demonstrate a successful verification and a stale-plan rejection.
10. **Preserve evidence:** export JSON/CSV and inspect the manifest and redaction.
11. **State limitations:** identify unsupported and unverified cloud operations.

The review should show both the successful path and at least one safely rejected action.

## 5. v1.0 — final product acceptance

v1.0 is the final academic submission build. It is not a claim of enterprise production readiness.

### Functional acceptance

- The agreed v0.9 workflow works from a fresh clone and clean local database.
- Every review-critical feature is implemented and tested or explicitly removed from scope with a recorded reason.
- No critical or high-severity known defect remains open without a documented disposition.
- Invalid input, unsupported actions, stale plans, and failed simulations produce safe outcomes.
- The app never presents a simulated cloud action as a verified cloud change.

### Testing acceptance

- Compile the app and all Python modules.
- Run the complete unit/database test suite.
- Walk through the Streamlit UI for scenario load, identity review, finding filters, plan preview, approval, simulated response, verification, and export.
- Execute applicable T01–T08 manual checks in `test_matrix.md`.
- Capture evidence for each executed test.
- Mark tests PASS only when the expected result was observed; use FAIL, BLOCKED, or NOT APPLICABLE where appropriate.
- Record environment details and deviations.

### Documentation and submission acceptance

- README describes only implemented features as current.
- Architecture and threat-model diagrams match the shipped code.
- Findings register includes evidence, impact, remediation, and retest outcome.
- Setup, test, and demo instructions work from a fresh clone.
- Prepare a short demo script, redacted screenshots, final report, limitations, and release recommendation.
- Verify that secrets, credentials, personal data, local databases, and sensitive unredacted evidence are not committed.
- Create a v1.0 release/tag only after acceptance checks are complete.

## 6. Cloud sandbox decision rule

Cloud integration is a separately verified capability.

- Use only the explicitly assigned and approved sandbox.
- Confirm project, endpoint, permissions, service support, and exact operation before testing.
- Start with read-only operations.
- Keep cloud writes disabled unless separately approved.
- Record operation, time, environment, observed result, and evidence.
- Label every operation SIMULATED, READ, WRITE, VERIFIED, FAILED, BLOCKED, or NOT SUPPORTED.
- If access or support is unavailable, preserve the local simulation and document the limitation. Do not claim cloud integration works.

An enabled service or reachable API endpoint does not prove that a specific IAM, credentials, storage, secret, or logging operation is supported.

## 7. T01–T08 evidence tracker

This tracker is intentionally unmarked until manual evidence is captured.

| Test | Final evidence expected | Result |
|---|---|---|
| T01 — Inventory | Identity, role, owner, and resource-scope view | Pending execution |
| T02 — Permission purpose | Baseline rationale and required/granted comparison | Pending execution |
| T03 — Containment | Before/after policy state and resulting identity status | Pending execution |
| T04 — Access verification | Required access retained in simulator; unrelated access removed or denied as expected | Pending execution |
| T05 — Evidence preservation | Case timeline and exported evidence bundle | Pending execution |
| T06 — Controlled error | Safe failure with unchanged state and no sensitive data in output | Pending execution |
| T07 — Sensitive-data review | Source, logs, screenshots, and exports reviewed/redacted | Pending execution |
| T08 — Repeatability | Full test set rerun with recorded environment and outcomes | Pending execution |

## 8. Feature freeze and change control

After the v0.9 review:

- Freeze feature development.
- Fix reproducible defects and safety issues.
- Close acceptance gaps and collect missing evidence.
- Improve documentation where reviewers found ambiguity.
- Do not add optional features unless required to meet an agreed acceptance criterion.
- Re-run affected tests after every fix and the full suite before v1.0.

## 9. Final release decision

The v1.0 release decision should be one of:

- **READY FOR SUBMISSION:** required workflows, tests, documentation, and evidence are complete; limitations are explicit.
- **READY WITH DOCUMENTED LIMITATIONS:** the core local demonstration is complete, but an authorised cloud operation is blocked or unsupported and accurately documented.
- **NOT READY:** a critical workflow or evidence gap remains.

The release report must justify the decision using observed tests and retained evidence, not assumptions.

---

**Delivery principle:** v0.9 is the last prototype. v1.0 is the final, tested, documented, and evidence-backed submission. After the final review, finish and stabilise; do not restart the feature roadmap.
