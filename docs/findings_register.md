# Findings Register — Synthetic Demonstration

> These are findings in versioned local training fixtures. They are not findings from a real campus, cloud project, or production environment.

## RG-SYN-001 — Overprivileged results exporter

| Field | Detail |
|---|---|
| Scenario | `overprivileged-exporter` |
| Principal | `svc-results-export@campus-demo.iam` |
| Finding | Three role grants exceed the approved synthetic baseline for exporting examination reports |
| Demonstration severity | CRITICAL for service-account token creation; HIGH for object administration and secret access |
| Evidence | Fixture baseline requires `storage.objectViewer`; bindings also include `storage.objectAdmin`, `secretmanager.secretAccessor`, and `iam.serviceAccountTokenCreator` |
| Potential impact in the synthetic model | Unnecessary write/administrative access, access to secrets, and identity delegation capability |
| Recommended action | Confirm workload owner and baseline; review the binding-level policy diff; remove excess grants in the local simulator; separately consider quarantine |
| Retest | Verify the local bindings match the declared baseline and record post-action verification |

## RG-SYN-002 — Unknown role and broad resource scope

| Field | Detail |
|---|---|
| Scenario | `unknown-role-and-delegation` |
| Principal | `svc-etl-worker@research-demo.iam` |
| Finding | An unrecognised role is attached at project scope in addition to the declared dataset viewer role |
| Demonstration severity | HIGH |
| Evidence | Synthetic fixture includes `research.datasetSuperuser` at `project:research-demo` while the approved baseline lists only `storage.objectViewer` |
| Potential impact in the synthetic model | The role definition and effective access are unknown to the prototype; broad scope increases uncertainty |
| Recommended action | Validate the role against the authoritative provider role catalogue and inspect the actual policy binding in an authorised environment before any change |
| Retest | Confirm the fixture no longer contains the unknown binding, or document an owner-approved exception |

## RG-SYN-003 — Ownerless legacy reporting identity

| Field | Detail |
|---|---|
| Scenario | `overprivileged-exporter` |
| Principal | `svc-reporting-old@campus-demo.iam` |
| Finding | The identity has no owner, an overdue access review, and a project-level administrative role despite an empty declared baseline |
| Demonstration severity | HIGH for broad administrative access; MEDIUM for ownership and review hygiene |
| Evidence | Fixture fields show no owner, review date in the past, empty required roles, and a `storage.admin` project binding |
| Potential impact in the synthetic model | No accountable owner is available to justify the identity or the access; the role is broader than the declared requirement |
| Recommended action | Confirm whether the workload is retired; obtain an owner decision; remove excess binding and/or quarantine only through an approved response plan |
| Retest | Confirm the binding is absent after simulation, case evidence is retained, and lifecycle status matches the approved decision |

## Interpretation and caveats

- All principals, grants, resources, relationships, and owners in these records are synthetic.
- Severity is an illustrative rule output, not a calibrated likelihood or cloud-provider rating.
- The prototype does not establish who granted a role, who used it, whether an identity was compromised, or whether an attacker exists.
- A local response simulation is not evidence of a cloud-side permission change.
- Any real finding would require verified principal identity, policy binding, resource scope, owner approval, and provider audit evidence.

## Evidence capture checklist

- [ ] Scenario ID and fixture version recorded.
- [ ] Baseline and owner metadata captured.
- [ ] Finding details and source evidence captured.
- [ ] Dry-run before/after policy diff captured.
- [ ] Independent review decision captured.
- [ ] Simulated action and verification result captured.
- [ ] Case JSON/CSV export and SHA-256 manifest retained.
- [ ] Redaction and limitations reviewed.
- [ ] Any sandbox observations recorded separately from synthetic results.
