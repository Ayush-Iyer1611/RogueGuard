# RogueGuard — The Rogue Service Account

A defensive, local demonstration for identifying overprivileged service identities, recommending least-privilege access, simulating containment, and retaining an audit trail.

## Important scope
This is a **synthetic local simulation**. It does not connect to or modify real Google Cloud IAM, IAM Credentials, Cloud Storage, Secret Manager, or Cloud Logging resources. Use only the assigned Floci workspace for any cloud verification, and only after mentor approval.

## Run locally
Requires Python 3.10+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (normally http://localhost:8501).

## Demo flow
1. Open **Identity inventory** and inspect the four synthetic service accounts.
2. Show `svc-results-export` and `svc-reporting-old` with excess grants.
3. Explain why broad storage, secret-access, and service-account administration permissions increase blast radius.
4. Open **Containment console**, select a synthetic identity, tick the confirmation box, and contain it.
5. Show that excess grants are removed, the account is marked QUARANTINED, and an audit event is recorded.
6. Explain that reactivation does not restore old grants; a human must review and approve the identity.
7. Re-run the inventory view and show the post-containment state.

## Detection model
The prototype compares each account's granted roles with the roles declared as required for its stated purpose. Roles outside that declared set are flagged as excess. A transparent heuristic score helps prioritise review; it is not a cloud-provider risk score and should not be represented as one.

## Architecture
Synthetic account inventory → access review → excess-grant detection → least-privilege recommendation → simulated containment → audit trail.

## Suggested team roles
- Security Architect: assets, trust boundaries, threat model.
- Cloud Security Engineer: Floci service availability and exact operation checks.
- Application Security Engineer: dashboard and remediation workflow.
- Identity & Data Security Engineer: role-to-purpose mapping and least privilege.
- Detection, Testing & Evidence Engineer: test matrix, audit evidence and report.

## Test checklist
- T01: Inventory identifies principal, roles and resource scope.
- T02: Every retained permission has a documented purpose.
- T03: Unneeded grants are removed only in an authorised sandbox (local prototype simulates this).
- T04: Required operation remains allowed and unrelated access is denied (policy comparison in local prototype).
- T05: Containment preserves evidence in the audit trail.
- T06: Controlled unexpected errors are handled safely.
- T07: Source, output and logs contain no secrets or real personal data.
- T08: Repeat tests and document results and limitations.

## Known limitations
- Data is seeded locally in SQLite.
- No actual cloud API calls are made.
- Risk score is illustrative and rule-based.
- Permission requirements are declared in synthetic seed data; a real deployment would need owner validation and resource-level IAM policy analysis.
