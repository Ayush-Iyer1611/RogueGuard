# RogueGuard — Project Synopsis

## Project overview

RogueGuard is a defensive identity-security workbench focused on the risks created by excessive permissions assigned to non-human identities. Its final prototype (v0.9) demonstrates a controlled analyst workflow using versioned synthetic records: load an identity scenario, evaluate permissions, investigate findings, plan a response, obtain a separate reviewer decision, simulate the action, verify the result, and preserve case evidence.

## Problem statement

Service accounts and workload identities can accumulate privileges that exceed their intended purpose. A role may remain after a workload changes, an identity may lose its owner, or a broad permission may create unnecessary access to resources or other identities. A simple granted-role comparison is useful but does not provide sufficient context for response decisions. Analysts also need to know why a finding exists, what a proposed change would do, who reviewed it, and what evidence supports the outcome.

## Objectives

1. Represent synthetic identities, owners, purposes, resources, permission bindings, and approved or unreviewed baselines.
2. Detect excess/missing grants, unknown roles, broad resource scope, missing ownership, and overdue access reviews in fixture data.
3. Generate explainable findings with stable IDs, evidence, severity, confidence, and recommended actions.
4. Support finding triage, case creation, and response planning.
5. Preview before/after changes before a simulated action.
6. Separate permission reduction, identity quarantine, and gated reactivation.
7. Require a different reviewer from the plan creator for approval.
8. Verify simulated outcomes and retain actor/reason/timestamp evidence.
9. Export case evidence as JSON and CSV with a SHA-256 manifest.
10. Validate important workflows through automated tests and a manual evidence matrix.

## Proposed final-prototype workflow

Load fixture → inspect identity/resource bindings → run detection rules → triage a finding → create a case → preview dry-run plan → independent review → simulate response → verify outcome → export evidence.

## Architecture and technology

- **Presentation:** Streamlit.
- **Application and security logic:** Python.
- **Persistence:** SQLite.
- **Scenario data:** versioned JSON fixtures.
- **Tests:** Python standard-library `unittest`.
- **Version control and CI:** Git and GitHub Actions.

The v0.9 prototype is provider-neutral at its core. Its current adapter/data source is synthetic fixture input. Google Cloud IAM, IAM Credentials, Cloud Storage, Secret Manager, Cloud Logging, and Floci are possible integration targets only after their exact operations are confirmed and tested in the assigned authorised sandbox.

## Scope and safety

All current identities, resources, grants, relationships, approvals, and response actions are synthetic. RogueGuard does not connect to or modify real cloud identities, roles, tokens, resources, or secrets. The two-person approval and response workflow is a simulation. No cloud operation is claimed as verified unless independently observed and documented.

## Verification strategy

Run the automated suite and execute the applicable T01–T08 manual tests. Capture baseline and post-action screenshots, finding details, policy diffs, approval decisions, verification results, case exports, redacted logs, and environment information. Mark tests PASS only after observed evidence exists. Record unsupported or blocked cloud operations explicitly.

## Release strategy

- **v0.1:** initial local permission-audit and containment foundation.
- **v0.9:** last prototype and final review candidate.
- **v1.0:** final, tested, documented, evidence-backed academic submission.

After the v0.9 review, freeze feature scope. The remaining work is defect correction, acceptance testing, documentation, evidence capture, and packaging—not another open-ended prototype cycle.
