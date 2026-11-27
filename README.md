# RogueGuard

**Identity Exposure, Permission Intelligence & Response Planning — an evolving defensive security prototype.**

RogueGuard is a learning-focused security workbench for investigating non-human identities, understanding excessive access, planning least-privilege changes, and preserving evidence around response decisions.

The project began as a local service-account permission auditor and containment simulator. The next prototype iteration expands the concept into a more complete identity-security workflow: **discover → understand → prioritise → plan → approve → simulate → verify → preserve evidence**.

> [!IMPORTANT]
> **Prototype status:** the current implementation remains a local synthetic simulation built with Python, Streamlit, and SQLite. The expanded capabilities in the roadmap are design targets, not completed features. RogueGuard does not currently discover live identities, read cloud IAM policies, ingest provider audit logs, revoke credentials, or modify cloud resources. All cloud-facing work must be separately implemented and verified in an explicitly authorised sandbox.

<p align="center">
  <img src="https://img.shields.io/badge/STATUS-EVOLVING%20PROTOTYPE-1f6feb?style=for-the-badge" alt="Evolving prototype">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Tests-unittest-2E8B57" alt="Python unittest">
  <img src="https://img.shields.io/badge/Cloud%20integration-NOT%20IMPLEMENTED-lightgrey" alt="Cloud integration not implemented">
</p>

---

## 01 / The problem RogueGuard is exploring

Service accounts and other workload identities often accumulate permissions as systems evolve. A role that was useful during initial setup may remain long after the workload changes. An identity may have no clear owner, a stale purpose, a broad resource scope, or the ability to impersonate another identity.

A simple role comparison can expose obvious excess grants, but it is not enough to understand the full security picture. A useful identity review also needs to answer:

- **Who is this identity?** What workload uses it, who owns it, and is it still required?
- **What can it access?** Which roles are granted, at what resource scope, and through which policy path?
- **Why does it have that access?** Is there a current, approved purpose and a traceable baseline?
- **What could go wrong?** Could the identity access sensitive data, create resources, or impersonate another principal?
- **What should happen next?** Can access be reduced safely, should the identity be quarantined, and who must approve the action?
- **How do we prove it?** What was observed, what changed, what was tested, and what remains unverified?

RogueGuard is being developed to explore these questions in a controlled, evidence-led workflow.

## 02 / Current prototype: what works today

The current codebase provides a small but testable local foundation.

| Capability | Current behaviour |
|---|---|
| Synthetic identity inventory | Four seeded service-account records with purpose, owner, resource labels, granted roles, and declared required roles |
| Permission comparison | Computes excess and missing roles by comparing granted roles with the declared baseline |
| Risk score | Applies fixed, documented role weights and caps the illustrative score at 100 |
| Containment simulation | Retains selected required roles and marks the synthetic account as QUARANTINED |
| Reactivation | Reactivates a quarantined record without restoring removed grants |
| Local audit events | Records before/after roles, status, removed roles, outcome, and UTC timestamp |
| Demo reset | Recreates the synthetic seed dataset and clears local audit events |
| Automated tests | 17 standard-library unit and database tests |
| Dashboard | Inventory, containment console, summary metrics, and local audit trail |

### Seeded scenario

The demo contains four fictional identities. One is intentionally overprivileged.

| Synthetic identity | Declared purpose | Seeded condition |
|---|---|---|
| svc-library-reader | Read approved library catalogue files | Matches declared role baseline |
| svc-results-export | Export approved examination result reports | Three excess grants beyond the declared viewer role |
| svc-backup-agent | Read backup metadata and write backup archives | Matches declared role baseline |
| svc-reporting-old | Legacy reporting integration | No active permissions declared |

The intentionally overprivileged account has these extra grants:

- storage.objectAdmin
- secretmanager.secretAccessor
- iam.serviceAccountTokenCreator

This demonstrates a configuration deviation in synthetic data. It does **not** prove an intruder exists, identify who changed an IAM policy, or establish malicious intent.

### Current architecture

~~~mermaid
flowchart TD
    A[Synthetic seed records] --> B[Streamlit dashboard]
    B --> C[Identity inventory]
    C --> D[Permission comparison]
    D --> E[Illustrative risk score]
    E --> F[Operator confirmation]
    F --> G[Local containment simulation]
    G --> H[(SQLite account store)]
    G --> I[(SQLite audit table)]
    H --> B
    I --> B
    J[unittest suite] -. tests .-> D
    J -. tests .-> G
~~~

| Component | Current responsibility |
|---|---|
| app.py | Streamlit interface and operator actions |
| core.py | Role comparison, risk heuristic, remediation calculation, and simulated access decisions |
| database.py | SQLite seed data, persistence, transactional containment, reactivation, audit events, and reset |
| tests/ | Core logic and database workflow tests |

See [architecture and threat model](docs/architecture.md), [test matrix](docs/test_matrix.md), and [findings register](docs/findings_register.md).

---

## 03 / What is going wrong — current limitations to address

These are design and implementation gaps observed in the current repository. They are not claims of vulnerabilities in a live cloud environment.

| Current limitation | Why it matters | Direction for the next prototype |
|---|---|---|
| Baseline is trusted seed data | The system cannot tell whether the declared required roles are correct or approved | Add baseline provenance, owner review, versioning, and approval history |
| No live identity discovery | Unknown or newly created service accounts cannot be found | Introduce a source-adapter interface, beginning with synthetic JSON fixtures |
| Roles are not attached to individual resource bindings | A role name alone does not explain whether access is project-wide, bucket-wide, inherited, or conditional | Model principal–role–resource bindings and policy inheritance explicitly |
| No identity relationship graph | Impersonation and service-account delegation paths are invisible | Add a graph of principals, workloads, resources, and trust relationships |
| Detection is limited to excess and missing roles | Dormant, ownerless, orphaned, unknown, or suspicious identities are not detected | Add independent finding rules with evidence and confidence |
| Risk is a fixed heuristic | A few role weights can saturate the score; the result is not a probability or provider rating | Show score components, impact, confidence, and the reasons behind every score |
| Containment combines two different actions | Removing excessive grants and disabling an identity have different operational effects | Separate permission reduction from full identity quarantine |
| No dry-run policy diff | The operator cannot inspect a structured change plan before applying it | Preview before/after policy, affected resources, and expected workload impact |
| Reactivation is immediate | A warning appears after reactivation rather than requiring review before it | Add a reactivation gate, owner approval, and post-restore verification |
| Reset deletes local audit events | Useful demo evidence can disappear with the reset | Export or snapshot evidence before destructive resets; preserve case history |
| Local audit data is mutable | SQLite evidence is not an independent or tamper-proof record | Add event IDs, actor/reason fields, integrity checks, export manifests, and an external evidence target later |
| Minimal dashboard and test coverage | There is no search, filtering, case workflow, UI-level verification, or provider integration testing | Add analyst workflow views, structured fixtures, and expanded tests |

### Important risk-model caveats

The current role weights are a prioritisation aid only. They are not calibrated against incident outcomes. Unknown roles currently receive a default weight, and account status affects the displayed score. The next iteration should keep **finding severity**, **identity status**, and **confidence in the evidence** as separate values rather than compressing them into one number.

The current comparison also treats role names as a set. It does not evaluate conditional bindings, inherited grants, resource-level scope, permission-level differences within a role, or the actual use of a permission.

---

## 04 / Next prototype: RogueGuard 0.2 concept

The target is not an enterprise-ready IAM platform. It is a richer, modular prototype that can demonstrate the complete analyst decision process using synthetic records and replayable evidence.

### A. Identity intelligence

- **Expanded identity registry:** service accounts, workload identities, human principals, service principals, and unknown principals as distinct entity types.
- **Ownership and lifecycle:** owner, team, purpose, environment, creation time, last observed time, lifecycle state, and review date.
- **Identity health checks:** missing owner, missing purpose, stale identity, expired review, disabled-but-still-referenced identity, and orphaned resource references.
- **Permission inventory:** individual role bindings with principal, role, resource, source, condition, and inheritance metadata.
- **Baseline provenance:** baseline owner, source, version, rationale, approval state, and last review timestamp.
- **Unknown-grant detection:** identify grants that do not map to the prototype's recognised role catalogue; never silently treat an unknown role as harmless.
- **Least-privilege comparison:** detect excess and missing permissions without automatically granting missing access.
- **Resource scope analysis:** distinguish project, folder, bucket, and object-level assignments in the data model.
- **Identity relationship map:** visualise service-to-service trust, impersonation, delegation, and token-creation relationships.
- **Blast-radius preview:** show which synthetic resources and connected identities could be affected by a principal's permissions.

### B. Finding and risk engine

- **Rule-based findings:** excessive role, broad resource scope, unknown role, missing owner, stale identity, expired review, risky role combination, and suspicious trust relationship.
- **Finding lifecycle:** NEW → TRIAGED → ACCEPTED / FALSE POSITIVE → REMEDIATION PLANNED → RESOLVED → RETESTED.
- **Evidence-backed findings:** each finding should include a rule ID, principal, affected resource, observed grant, expected baseline, evidence source, timestamp, and confidence.
- **Explainable score breakdown:** show which factors increased impact and why, rather than displaying only a number.
- **Risk dimensions:** separate impact, likelihood estimate, exposure, confidence, and operational criticality.
- **Policy drift detection:** compare two synthetic snapshots and highlight newly added, removed, or changed bindings.
- **Exception handling:** allow a time-limited, justified exception with owner, approver, expiry, and review status.
- **False-positive workflow:** record analyst rationale and preserve the original evidence instead of deleting the finding.

### C. Response planning and containment

- **Read-only review mode:** inspect findings without changing the synthetic environment.
- **Dry-run remediation:** build a proposed policy diff and show exactly which grants would be changed.
- **Split response actions:** remove an excess grant, quarantine an identity, suspend a relationship, or request a review as separate operations.
- **Impact preview:** show affected synthetic workloads and resources before a proposed change.
- **Approval workflow:** require an operator reason and owner approval for sensitive actions; support a two-person approval concept for high-impact actions.
- **Response playbooks:** guided steps for overprivileged identities, abandoned identities, suspicious delegation, and unknown grants.
- **Safe simulator:** apply proposed changes to a copy or fixture dataset before touching the active demo state.
- **Rollback plan:** store the prior policy snapshot and a proposed reversal; require review before replaying it.
- **Post-action verification:** compare the resulting state with the intended policy and mark the action VERIFIED, FAILED, or NOT VERIFIED.
- **Reactivation gate:** require a review checklist and explicit approval before a quarantined identity can become active again.

### D. Evidence, audit, and case management

- **Case workspace:** group findings, affected identities, response plans, approvals, and evidence under a case ID.
- **Richer audit events:** actor, action, reason, timestamp, case ID, before/after state, approval reference, and outcome.
- **Evidence snapshots:** preserve the inventory and policy state used to make a decision.
- **Integrity manifest:** calculate hashes for exported evidence files and record a manifest to help detect later modification.
- **Evidence export:** JSON and CSV initially; a compact report format can follow.
- **Redaction controls:** mask secrets, tokens, personal data, and sensitive resource identifiers in exports.
- **Evidence retention controls:** make reset, archive, and deletion explicit actions with clear warnings.
- **Audit review:** filter events by principal, action, outcome, case, and date range.

A local hash or SQLite audit table is **not** equivalent to immutable storage. Independent retention and access controls would still be required for a production-grade evidence system.

### E. Analyst experience

- **Security overview:** counts by finding state, severity, identity type, and environment.
- **Finding inbox:** searchable, filterable, sortable list with owner and next action.
- **Identity detail view:** metadata, roles, resource bindings, baseline, related findings, and event history.
- **Policy diff viewer:** side-by-side before/after grants and resource scopes.
- **Relationship visualisation:** interactive identity and resource graph.
- **Timeline:** correlate synthetic policy changes, findings, approvals, and response actions.
- **Evidence panel:** inspect source records and export a case bundle.
- **Scenario library:** load named scenarios such as overprivileged exporter, abandoned service account, risky impersonation chain, or broad storage access.
- **Demo mode:** reset to a known fixture while keeping exported evidence outside the resettable dataset.

### F. Provider integration boundary — future work

The prototype should be provider-neutral at the core and provider-specific at the edges.

- Define an identity-provider adapter contract for inventory, policy reads, resource metadata, and audit-event retrieval.
- Implement a mock adapter first, backed by versioned JSON fixtures.
- Add a read-only adapter for the explicitly assigned Google Cloud / Floci sandbox only after access, supported operations, and mentor approval are confirmed.
- Record the provider, project, endpoint, timestamp, and operation result for every integration test.
- Label each operation as SIMULATED, READ, WRITE, VERIFIED, FAILED, or NOT SUPPORTED.
- Keep cloud writes disabled by default; require a separate approval gate for any sandbox response action.
- Never infer that a service is integrated merely because it is enabled or an API endpoint exists.

### G. Engineering quality

- Add schema versioning and controlled SQLite migrations.
- Add unit tests for every finding rule and response transition.
- Add fixture-based adapter contract tests.
- Add tests for malformed data, unknown roles, empty baselines, duplicate grants, invalid transitions, reset evidence preservation, and transaction rollback.
- Add UI smoke tests for the highest-value operator flows.
- Add coverage reporting, linting, dependency review, and static checks in CI.
- Add structured application logs with secret redaction.
- Keep test fixtures synthetic and prevent real credentials or database files from entering Git.

---

## 05 / Proposed target architecture

The architecture below is a **design target**, not the current code layout.

~~~mermaid
flowchart LR
    A[Synthetic fixtures] --> B[Provider adapter interface]
    A2[Future authorised sandbox adapter] -. later .-> B
    B --> C[Normalisation and validation]
    C --> D[Identity and resource registry]
    D --> E[Relationship graph]
    D --> F[Baseline and policy evaluator]
    E --> G[Finding engine]
    F --> G
    G --> H[Finding inbox and risk explanation]
    H --> I[Case workspace]
    I --> J[Dry-run response planner]
    J --> K[Approval gate]
    K --> L[Local response simulator]
    K -. future, separately approved .-> M[Sandbox response adapter]
    L --> N[Evidence and audit service]
    M --> N
    N --> O[Case export and verification]
~~~

### Proposed core data objects

| Object | What it represents |
|---|---|
| Identity | Principal, type, owner, purpose, environment, and lifecycle |
| Resource | Project, bucket, service, or other protected asset |
| RoleBinding | Principal, role, resource, condition, source, and inheritance path |
| Baseline | Expected access, rationale, owner, version, and approval |
| Finding | Rule, severity, confidence, evidence, state, and recommended action |
| Case | Related findings, identities, owners, approvals, and timeline |
| ActionPlan | Proposed changes, impact preview, prerequisites, and rollback |
| Approval | Reviewer, decision, reason, and timestamp |
| AuditEvent | Actor, action, target, outcome, before/after references, and case |
| EvidenceArtifact | Snapshot, export, hash, source, timestamp, and redaction state |

---

## 06 / Increment plan

The work is deliberately staged. The goal is to build a credible prototype, not claim production readiness.

| Increment | Scope | Exit criteria |
|---|---|---|
| **0.1 — Foundation (current)** | Synthetic inventory, basic role comparison, illustrative scoring, local containment, SQLite audit, baseline tests | Existing demo runs locally and current tests pass |
| **0.2 — Analyst prototype** | Rich identity/resource schema, fixture importer, finding rules, searchable finding inbox, explainable severity, policy diff, dry-run plans, split containment actions, case evidence export | A reviewer can load a scenario, explain a finding, preview a response, simulate it, and export evidence |
| **0.3 — Relationship intelligence** | Identity graph, impersonation paths, blast-radius view, snapshot drift, baseline approval and exceptions | A reviewer can trace why an identity is risky and what connected resources may be affected |
| **0.4 — Controlled sandbox validation** | Read-only provider adapter, operation-level verification, integration tests, explicit sandbox approval gates | Every claimed cloud read is repeatable and documented; unsupported operations are clearly marked |
| **0.5 — Response and monitoring experiments** | Approved sandbox response experiments, rollback checks, audit-event ingestion, alert prototypes | Every response has a reviewable plan, approval, recorded result, and post-action verification |

### Prototype 0.2 — recommended build order

1. Introduce versioned fixture data for identities, resources, role bindings, and baselines.
2. Add a rule engine and a structured finding model.
3. Build the finding inbox and identity detail page.
4. Add a dry-run response plan and policy-diff view.
5. Separate permission removal from full quarantine.
6. Add case IDs, richer audit events, and evidence export.
7. Add tests for each rule, invalid transition, rollback, and evidence-preservation path.

This sequence improves the current prototype without prematurely building cloud automation.

---

## 07 / Run locally

### 1. Clone the repository

~~~bash
git clone https://github.com/Ayush-Iyer1611/RogueGuard.git
cd RogueGuard
~~~

### 2. Create and activate a virtual environment

Linux / macOS:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

Windows PowerShell:

~~~powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
~~~

### 3. Install dependencies

~~~bash
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

### 4. Run the current dashboard

~~~bash
streamlit run app.py
~~~

Open the local URL printed by Streamlit, usually http://localhost:8501.

### 5. Run the current test suite

~~~bash
python -m unittest discover -s tests -v
~~~

The repository currently contains 17 unit and database tests. A passing suite verifies only the paths covered by those tests; it does not establish production security, cloud integration, or comprehensive UI correctness.

---

## 08 / Repository map

~~~text
RogueGuard/
├── app.py
├── core.py
├── database.py
├── requirements.txt
├── docs/
│   ├── architecture.md
│   ├── project_synopsis.md
│   ├── test_matrix.md
│   └── findings_register.md
├── tests/
│   ├── test_core.py
│   └── test_database.py
└── .github/
    ├── workflows/
    │   └── tests.yml
    ├── ISSUE_TEMPLATE/
    └── pull_request_template.md
~~~

## 09 / Safety and scope

- Use synthetic identities, resources, and event fixtures during local development.
- Use only localhost or an explicitly assigned and approved training sandbox.
- Do not import real student data, personal data, production secrets, or credentials.
- Do not attempt to discover or modify identities in systems without authorisation.
- Keep cloud integration read-only until the exact operation, scope, and approval are established.
- Do not claim an operation is verified unless its result has been observed and recorded.
- Keep local databases, generated evidence containing sensitive data, tokens, and credentials out of Git.
- See [SECURITY.md](SECURITY.md) for the project's security reporting and safe-use guidance.

## 10 / Project status

RogueGuard is an evolving cybersecurity prototype and research-learning project. The current implementation proves a narrow local workflow. The next iteration is intended to test whether identity inventory, policy context, explainable findings, safe response planning, and evidence preservation can be brought together in one coherent analyst experience.

**The objective is not to automate every security action. It is to make each decision explainable, reviewable, testable, and safe.**

---

[Architecture](docs/architecture.md) · [Test matrix](docs/test_matrix.md) · [Findings register](docs/findings_register.md) · [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)
