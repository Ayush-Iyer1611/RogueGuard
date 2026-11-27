# RogueGuard

**Identity Exposure · Permission Intelligence · Response Planning**

<sub>Final prototype candidate · v0.9 workbench · Intended submission release: v1.0</sub>

RogueGuard is a defensive identity-security workbench for reviewing non-human identities, detecting risky permission assignments, planning least-privilege responses, and preserving evidence around analyst decisions.

The project is moving through its **last prototype cycle**. v0.9 is intended to be the final prototype reviewed before v1.0, the final academic submission product. The objective is to deliver one coherent, tested, evidence-backed analyst workflow—not an endless feature expansion.

> [!IMPORTANT]
> **Current scope:** RogueGuard runs locally with synthetic JSON fixtures, Python, Streamlit, and SQLite. The v0.9 workbench simulates response actions; it does not discover live identities, read or modify cloud IAM policies, revoke credentials, ingest provider audit logs, or change cloud resources. Some v0.9 capabilities remain under development and must pass the review gates in [the final submission plan](docs/final_submission_plan.md).

<p align="center">
  <img src="https://img.shields.io/badge/RELEASE-v0.9%20FINAL%20PROTOTYPE-8250df?style=for-the-badge" alt="RogueGuard v0.9 final prototype">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/SQLite-Local%20Store-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/Cloud%20Integration-Not%20Implemented-lightgrey" alt="Cloud integration not implemented">
</p>

---

## 01 / Why RogueGuard?

Service accounts and workload identities often accumulate permissions as workloads and systems evolve. An identity may retain an old administrative role, have no accountable owner, or possess an ability to access secrets or impersonate another principal that its current purpose does not require.

A role comparison alone is not enough. An analyst also needs context:

- **Identity:** who owns the principal, what workload uses it, and whether it is still active.
- **Access:** which role is assigned to which resource, and from what source.
- **Baseline:** why the permission is required and whether the baseline has been reviewed.
- **Finding:** what rule was triggered, what evidence supports it, and how confident the system is.
- **Response:** what a proposed change will do before it is applied.
- **Verification:** whether the resulting state matches the reviewed plan.
- **Evidence:** who made a decision, why it was made, and what changed.

RogueGuard explores this workflow in a controlled, reproducible synthetic environment.

## 02 / What is implemented in the v0.9 workbench?

| Capability | Current implementation |
|---|---|
| Scenario fixtures | Versioned JSON scenarios with identity, resource, baseline, binding, and relationship data |
| Fixture validation | Rejects missing required fields, duplicate principals, and bindings to unknown principals/resources |
| Identity explorer | Displays owner, purpose, type, environment, lifecycle state, review date, baseline, and resource-level bindings |
| Permission model | Represents a principal + role + resource binding, including source, optional condition, and inheritance flag |
| Finding engine | Detects excess roles, missing required roles, unknown roles, broad project/folder scope, missing owner, stale review, and invalid review date |
| Explainable findings | Stable finding IDs, rule IDs, evidence details, severity, confidence, recommendation, and lifecycle state |
| Analyst workflow | Finding inbox, state transitions, cases, and a case timeline |
| Dry-run response | Stores before/after snapshots without changing the active scenario |
| Independent review | Requires an approver different from the plan creator |
| Response simulator | Separates excess-permission removal from identity quarantine |
| Reactivation gate | Requires a quarantined identity and removal of excess bindings before reactivation |
| Verification | Compares actual post-action state against the reviewed plan |
| Evidence export | JSON case bundle, CSV findings, SHA-256 manifest, and optional identifier/token-like redaction |
| Relationship view | Displays relationship edges supplied by the synthetic scenario |
| Automated tests | Unit, database, v0.9 workflow regression, and Streamlit startup smoke tests in GitHub Actions |

### Current synthetic scenarios

**Overprivileged Results Exporter** includes four fictional service identities, resource-level bindings, owner/baseline metadata, an intentionally overprivileged exporter, and an older unowned reporting identity.

**Unknown Role and Delegation Chain** includes a deliberately unknown role, broad-scope access, missing ownership, and a synthetic delegation relationship.

The fixtures are designed to demonstrate configuration deviations. They do not prove an intruder exists, establish who changed a policy, or determine malicious intent.

### Detection rules

| Rule ID | What it detects |
|---|---|
| `EXCESS_ROLE` | A granted role not present in the declared required-role baseline |
| `MISSING_REQUIRED_ROLE` | A baseline role with no matching binding |
| `UNKNOWN_ROLE` | A role outside the prototype's recognised role catalogue |
| `BROAD_RESOURCE_SCOPE` | A selected non-viewer permission attached to project or folder scope |
| `MISSING_OWNER` | No accountable owner is recorded |
| `STALE_ACCESS_REVIEW` | The identity's review date is in the past |
| `INVALID_REVIEW_DATE` | Review metadata is not a valid ISO date |

Severity and confidence are separate fields. Confidence currently reflects the fixture baseline approval state; it is not a statistical confidence interval. Detection uses declared fixture data and does not measure actual permission usage.

## 03 / End-to-end analyst workflow

~~~mermaid
flowchart TD
    A[Load synthetic scenario] --> B[Inspect identity and resource bindings]
    B --> C[Run finding rules]
    C --> D[Review evidence and severity]
    D --> E[Create case]
    E --> F[Generate dry-run plan]
    F --> G[Independent reviewer decision]
    G --> H{Approved?}
    H -- No --> I[No response executed]
    H -- Yes --> J[Simulate local response]
    J --> K[Verify post-action state]
    K --> L[Export case evidence]
~~~

1. Load a scenario fixture.
2. Inspect the selected identity and its resource-level bindings.
3. Analyse the scenario and triage relevant findings.
4. Create a case from one or more findings.
5. Generate a dry-run plan and compare before/after snapshots.
6. Obtain an independent reviewer decision.
7. Execute the approved action against the local synthetic dataset.
8. Verify the resulting state.
9. Export the case evidence.

### Separate response operations

- **REMOVE_EXCESS:** removes bindings not present in the declared required-role baseline. It does not quarantine the identity.
- **QUARANTINE:** changes the synthetic identity lifecycle state to QUARANTINED. It does not remove any role bindings.
- **REACTIVATE:** reactivates a quarantined identity only after its remaining bindings fit the declared baseline. Removed permissions are never silently restored.

The simulator checks that the live local state still matches the plan's original snapshot before execution. If the state has changed since review, the plan must be recreated.

## 04 / Current limitations and risks

These limitations are deliberately visible so the project does not overclaim what it proves.

| Limitation | Why it matters | Current treatment |
|---|---|---|
| Fixture baselines are trusted | The declared required roles may be wrong or stale | Baseline approval state and rationale are shown; independent validation is future work |
| No live identity discovery | Unknown cloud principals cannot be found | Versioned synthetic fixture import only |
| No cloud policy evaluator | Inheritance, conditions, provider-specific permissions, and real policy semantics are not evaluated | Resource/role bindings are simplified synthetic records |
| Small role catalogue | An unrecognised role may need provider-specific validation | Flagged as UNKNOWN_ROLE; not automatically treated as benign |
| Heuristic severity | It is not a probability, provider rating, or calibrated incident likelihood | Severity and confidence are shown separately, with evidence |
| Relationship edges are supplied | A graph edge is not proof of a real privilege-escalation path | Graph is clearly labelled synthetic fixture context |
| Reviewer identity is a label | Two-person approval is not enterprise authentication | Separate reviewer field is required, but not authenticated |
| SQLite is local and mutable | Local audit is not immutable evidence storage | Event history and export manifest help with review; independent retention is future work |
| Export hash limitations | A hash manifest alone does not protect the manifest or prove trusted time | Export explicitly warns that hashes are not immutable storage |
| Limited UI automation coverage | CI verifies the Streamlit app starts, but does not automate every operator interaction | Manual T01–T08 and end-to-end interaction review remain part of the release gate |

## 05 / Final prototype v0.9 — scope freeze

v0.9 is the **last prototype before submission**. The target is one complete analyst experience, not every possible IAM feature.

### Review-critical acceptance

- A reviewer can load a known fixture and understand identity ownership, purpose, and resource scope.
- Findings explain the rule, evidence, severity, confidence, and next action.
- An analyst can create a case and review the policy change before execution.
- Permission removal and quarantine are independent actions.
- A second reviewer must approve the plan.
- Execution is blocked for pending/rejected or stale plans.
- Post-action verification records whether the intended state was achieved.
- Reactivation is blocked while excess grants remain.
- Case export includes findings, identity/resource context, response plans, approvals, events, and integrity manifest.
- Automated tests and manual review evidence are complete.

### Stretch features only if the required workflow is stable

- Interactive graph traversal and transitive delegation-path calculation.
- Snapshot drift comparison between arbitrary historical policy versions.
- Additional scenario templates.
- UI smoke tests and coverage reporting.

These are not reasons to delay the core workflow or mislabel an unfinished feature as complete.

## 06 / Release path — last prototype, then final product

| Release | Purpose | Exit gate |
|---|---|---|
| **v0.9 — Final prototype** | Last review candidate | Review-critical workflows operate locally; CI and review evidence are available; limitations are explicit |
| **v1.0 — Final product** | Final academic submission | Feature freeze; defect fixes complete; T01–T08 executed where applicable; tests, documentation, screenshots, report, demo, and release notes complete |

After the v0.9 review, only fix defects, close acceptance gaps, improve clarity, and collect evidence. Do not start another feature-expansion cycle.

See [Final Prototype and Submission Plan](docs/final_submission_plan.md) for the complete acceptance criteria, review demo sequence, evidence tracker, and release decision gates.

## 07 / Architecture and project files

- [Architecture and threat model](docs/architecture.md)
- [Project synopsis](docs/project_synopsis.md)
- [Test matrix](docs/test_matrix.md)
- [Findings register](docs/findings_register.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

~~~text
RogueGuard/
├── app.py
├── core.py
├── database.py
├── prototype.py
├── fixtures/
│   └── scenarios/
│       ├── overprivileged-exporter.json
│       └── unknown-role-and-delegation.json
├── docs/
├── tests/
│   ├── test_core.py
│   ├── test_database.py
│   └── test_prototype.py
├── evidence/
│   └── exports/       # generated locally; ignored by Git
└── .github/
    └── workflows/
        └── tests.yml
~~~

## 08 / Run locally

### 1. Clone the repository

~~~bash
git clone https://github.com/Ayush-Iyer1611/RogueGuard.git
cd RogueGuard
~~~

### 2. Create a virtual environment

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

### 3. Install and launch

~~~bash
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
~~~

Open the local address printed by Streamlit, usually http://localhost:8501.

### 4. Run automated tests

~~~bash
python -m unittest discover -s tests -v
~~~

A passing test suite verifies only the covered behaviours. It is not proof of production security, live cloud integration, or comprehensive UI correctness.

## 09 / Safety and evidence boundaries

- Use synthetic identities, resources, roles, and relationships for local development.
- Use only localhost or an explicitly assigned and approved training sandbox.
- Do not import real student data, production credentials, secrets, or third-party resources.
- Do not attempt to discover or modify identities in systems without authorisation.
- Cloud writes and credential operations remain out of scope unless separately approved and independently verified.
- Keep local databases, generated exports, tokens, and credentials out of Git.
- A simulated response must never be described as a verified cloud-side change.
- See [SECURITY.md](SECURITY.md) for reporting and safe-use guidance.

## 10 / Project status

**Current phase: v0.9 final prototype implementation and verification.**  
**Next release: v1.0 final product and academic submission.**

RogueGuard now has a broader local analyst workbench, but the final prototype must still pass its review-critical acceptance checks and manual evidence matrix. The v1.0 submission should be a stable, reproducible, tested, documented, and evidence-backed release within the verified project scope—not a claim of production-ready cloud security.

**Build deliberately. Review honestly. Verify the evidence. Freeze scope. Ship v1.0.**
