# RogueGuard — Project Synopsis

## Problem statement
Service accounts are non-human identities used by applications and automated workloads. Over time, their permissions may exceed operational requirements. An overprivileged or compromised identity can increase the blast radius of an incident by enabling unauthorised access to storage, secrets, or identity-management operations. Teams need a repeatable way to inventory service identities, justify permissions, detect excessive grants, and contain suspicious identities without destroying investigation evidence.

## Objectives
1. Inventory service identities, granted roles, owners, purpose, and resource scope.
2. Compare granted permissions against documented operational requirements.
3. Identify and prioritise excess privileges.
4. Recommend least-privilege access and demonstrate controlled containment.
5. Preserve timestamped, minimal audit evidence and verify outcomes with repeatable tests.

## Proposed solution
RogueGuard is a Python-based defensive dashboard. A synthetic identity inventory is reviewed by an analysis engine that compares granted roles with declared required roles. Excess grants are flagged and assigned a transparent demonstration risk score. An operator can simulate containment: excess grants are removed from the local model, the identity is marked quarantined, and an audit event is recorded. Reactivation does not restore removed permissions and requires human review.

## Proposed architecture
Dashboard → Identity inventory → Permission analysis → Least-privilege policy comparison → Containment workflow → Audit/evidence store.

## Technology
Python, Streamlit, SQLite, structured audit events. Google Cloud IAM, IAM Credentials, Cloud Storage, Secret Manager, and Cloud Logging are integration targets to verify in the assigned Floci environment; they are not claimed as connected in the local prototype.

## Scope and safety
Synthetic identities and data only. Testing is restricted to the local application or an explicitly assigned sandbox. No real college systems, production credentials, or third-party resources are tested.

## Verification
Use the handbook's T01–T08 matrix. Capture baseline and post-containment results, confirm required access remains available in the model, confirm unrelated access is removed, inspect audit events, and document unverified cloud operations.

## Expected outcome
A repeatable demonstration that identifies excess permissions, applies a least-privilege recommendation in a controlled synthetic environment, preserves evidence, and produces a defensible release recommendation.
