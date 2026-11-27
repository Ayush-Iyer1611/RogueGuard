"""RogueGuard v0.9 prototype domain and persistence layer.

Local synthetic simulation only. No cloud APIs are called.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

DB = Path(__file__).with_name("rogueguard.db")
FIXTURE_DIR = Path(__file__).with_name("fixtures") / "scenarios"
EXPORT_DIR = Path(__file__).with_name("evidence") / "exports"

KNOWN_ROLES = {
    "storage.objectViewer", "storage.objectCreator", "storage.objectAdmin",
    "storage.admin", "secretmanager.secretAccessor",
    "iam.serviceAccountTokenCreator", "iam.serviceAccountAdmin",
}
HIGH_IMPACT_ROLES = {
    "storage.admin", "iam.serviceAccountAdmin",
    "iam.serviceAccountTokenCreator",
}
MEDIUM_HIGH_ROLES = {"storage.objectAdmin", "secretmanager.secretAccessor"}

FINDING_TRANSITIONS = {
    "NEW": {"TRIAGED", "ACCEPTED", "FALSE_POSITIVE"},
    "TRIAGED": {"ACCEPTED", "FALSE_POSITIVE", "REMEDIATION_PLANNED"},
    "ACCEPTED": {"TRIAGED", "REMEDIATION_PLANNED"},
    "FALSE_POSITIVE": {"TRIAGED"},
    "REMEDIATION_PLANNED": {"TRIAGED", "RESOLVED", "CONTAINED"},
    "CONTAINED": {"TRIAGED", "RETESTED"},
    "RESOLVED": {"RETESTED", "TRIAGED"},
    "RETESTED": {"TRIAGED"},
}
CASE_TRANSITIONS = {
    "OPEN": {"IN_REVIEW", "CLOSED"},
    "IN_REVIEW": {"OPEN", "CLOSED"},
    "CLOSED": {"OPEN"},
}

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def initialize_prototype() -> None:
    """Create v0.9 tables without altering the original v0.1 tables."""
    with _connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS rg_scenarios (
          scenario_id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT,
          version TEXT NOT NULL, loaded_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rg_resources (
          scenario_id TEXT NOT NULL, resource_id TEXT NOT NULL,
          resource_type TEXT NOT NULL, name TEXT NOT NULL,
          environment TEXT NOT NULL, sensitivity TEXT NOT NULL,
          PRIMARY KEY (scenario_id, resource_id)
        );
        CREATE TABLE IF NOT EXISTS rg_identities (
          scenario_id TEXT NOT NULL, principal TEXT NOT NULL,
          identity_type TEXT NOT NULL, owner TEXT, purpose TEXT,
          environment TEXT NOT NULL, lifecycle_state TEXT NOT NULL,
          created_at TEXT, last_observed_at TEXT, review_due_at TEXT,
          PRIMARY KEY (scenario_id, principal)
        );
        CREATE TABLE IF NOT EXISTS rg_baselines (
          scenario_id TEXT NOT NULL, principal TEXT NOT NULL,
          version TEXT NOT NULL, owner TEXT, purpose TEXT,
          rationale TEXT, approval_state TEXT NOT NULL,
          approved_by TEXT, approved_at TEXT,
          required_roles_json TEXT NOT NULL,
          PRIMARY KEY (scenario_id, principal)
        );
        CREATE TABLE IF NOT EXISTS rg_bindings (
          binding_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL,
          principal TEXT NOT NULL, role TEXT NOT NULL,
          resource_id TEXT NOT NULL, source TEXT NOT NULL,
          condition_text TEXT, inherited INTEGER NOT NULL DEFAULT 0,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rg_relationships (
          relationship_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL,
          source_principal TEXT NOT NULL, target_principal TEXT NOT NULL,
          relationship_type TEXT NOT NULL, description TEXT
        );
        CREATE TABLE IF NOT EXISTS rg_findings (
          finding_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL,
          rule_id TEXT NOT NULL, principal TEXT NOT NULL,
          resource_id TEXT, role TEXT, title TEXT NOT NULL,
          description TEXT NOT NULL, severity TEXT NOT NULL,
          confidence TEXT NOT NULL, status TEXT NOT NULL,
          recommendation TEXT NOT NULL, evidence_json TEXT NOT NULL,
          created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rg_cases (
          case_id TEXT PRIMARY KEY, scenario_id TEXT NOT NULL,
          title TEXT NOT NULL, status TEXT NOT NULL,
          created_by TEXT NOT NULL, created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rg_case_findings (
          case_id TEXT NOT NULL, finding_id TEXT NOT NULL,
          PRIMARY KEY (case_id, finding_id)
        );
        CREATE TABLE IF NOT EXISTS rg_action_plans (
          plan_id TEXT PRIMARY KEY, case_id TEXT NOT NULL,
          scenario_id TEXT NOT NULL, principal TEXT NOT NULL,
          action_type TEXT NOT NULL, reason TEXT NOT NULL,
          created_by TEXT NOT NULL, before_json TEXT NOT NULL,
          after_json TEXT NOT NULL, status TEXT NOT NULL,
          created_at TEXT NOT NULL, executed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS rg_finding_history (
          history_id TEXT PRIMARY KEY, finding_id TEXT NOT NULL,
          actor TEXT NOT NULL, old_status TEXT NOT NULL,
          new_status TEXT NOT NULL, reason TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rg_approvals (
          approval_id TEXT PRIMARY KEY, plan_id TEXT NOT NULL,
          reviewer TEXT NOT NULL, decision TEXT NOT NULL,
          reason TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS rg_events (
          event_id TEXT PRIMARY KEY, case_id TEXT NOT NULL,
          plan_id TEXT, principal TEXT NOT NULL, actor TEXT NOT NULL,
          event_type TEXT NOT NULL, reason TEXT NOT NULL,
          before_json TEXT, after_json TEXT, outcome TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """)

def _validate_fixture(data: dict[str, Any]) -> None:
    for key in ("scenario_id", "name", "version", "resources", "identities", "bindings"):
        if key not in data:
            raise ValueError(f"Fixture missing required field: {key}")
    if not isinstance(data["identities"], list) or not data["identities"]:
        raise ValueError("Fixture must contain at least one identity.")
    principals = set()
    resources = {r.get("resource_id") for r in data["resources"]}
    for identity in data["identities"]:
        for key in ("principal", "identity_type", "environment", "lifecycle_state"):
            if not identity.get(key):
                raise ValueError(f"Identity missing required field: {key}")
        if identity["principal"] in principals:
            raise ValueError(f"Duplicate principal: {identity['principal']}")
        principals.add(identity["principal"])
    for binding in data["bindings"]:
        for key in ("principal", "role", "resource_id", "source"):
            if not binding.get(key):
                raise ValueError(f"Binding missing required field: {key}")
        if binding["principal"] not in principals:
            raise ValueError(f"Binding refers to unknown principal: {binding['principal']}")
        if binding["resource_id"] not in resources:
            raise ValueError(f"Binding refers to unknown resource: {binding['resource_id']}")
    for baseline in data.get("baselines", []):
        if baseline.get("principal") not in principals:
            raise ValueError("Baseline refers to an unknown principal.")
        if not isinstance(baseline.get("required_roles", []), list):
            raise ValueError("required_roles must be a list.")

def available_scenarios() -> list[dict[str, str]]:
    if not FIXTURE_DIR.exists():
        return []
    result = []
    for path in sorted(FIXTURE_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            result.append({"scenario_id": data["scenario_id"], "name": data["name"], "path": str(path)})
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            continue
    return result

def load_scenario(path_or_id: str) -> dict[str, Any]:
    """Validate and load a scenario fixture; old case/event history is retained."""
    candidate = Path(path_or_id)
    if not candidate.exists():
        candidate = FIXTURE_DIR / f"{path_or_id}.json"
    data = json.loads(candidate.read_text(encoding="utf-8"))
    _validate_fixture(data)
    initialize_prototype()
    sid = data["scenario_id"]
    with _connect() as con:
        existing_case = con.execute(
            "SELECT 1 FROM rg_cases WHERE scenario_id=? LIMIT 1", (sid,)
        ).fetchone()
        if existing_case:
            raise ValueError(
                "This scenario already has case history. Load a new scenario ID; "
                "export existing cases before any manual database reset."
            )
        # Replace only an unreviewed scenario snapshot. Case history is never silently deleted.
        for table in ("rg_findings", "rg_relationships", "rg_bindings", "rg_baselines",
                      "rg_identities", "rg_resources"):
            con.execute(f"DELETE FROM {table} WHERE scenario_id=?", (sid,))
        con.execute("""
          INSERT INTO rg_scenarios(scenario_id,name,description,version,loaded_at)
          VALUES(?,?,?,?,?)
          ON CONFLICT(scenario_id) DO UPDATE SET
            name=excluded.name, description=excluded.description,
            version=excluded.version, loaded_at=excluded.loaded_at
        """, (sid, data["name"], data.get("description", ""), data["version"], _utc()))
        for r in data["resources"]:
            con.execute("INSERT INTO rg_resources VALUES(?,?,?,?,?,?)",
                (sid, r["resource_id"], r["resource_type"], r["name"],
                 r.get("environment", "demo"), r.get("sensitivity", "INTERNAL")))
        for i in data["identities"]:
            con.execute("INSERT INTO rg_identities VALUES(?,?,?,?,?,?,?,?,?,?)",
                (sid, i["principal"], i["identity_type"], i.get("owner"),
                 i.get("purpose"), i["environment"], i["lifecycle_state"],
                 i.get("created_at"), i.get("last_observed_at"), i.get("review_due_at")))
        baselines = {b["principal"]: b for b in data.get("baselines", [])}
        for principal in (i["principal"] for i in data["identities"]):
            b = baselines.get(principal, {})
            con.execute("INSERT INTO rg_baselines VALUES(?,?,?,?,?,?,?,?,?,?)",
                (sid, principal, b.get("version", "unversioned"), b.get("owner"),
                 b.get("purpose"), b.get("rationale"), b.get("approval_state", "UNREVIEWED"),
                 b.get("approved_by"), b.get("approved_at"),
                 json.dumps(b.get("required_roles", []))))
        for b in data["bindings"]:
            con.execute("INSERT INTO rg_bindings VALUES(?,?,?,?,?,?,?,?,?)",
                (uuid.uuid4().hex, sid, b["principal"], b["role"], b["resource_id"],
                 b["source"], b.get("condition"), int(bool(b.get("inherited", False))), _utc()))
        for rel in data.get("relationships", []):
            con.execute("INSERT INTO rg_relationships VALUES(?,?,?,?,?,?)",
                (uuid.uuid4().hex, sid, rel["source"], rel["target"],
                 rel["relationship_type"], rel.get("description", "")))
    return {"scenario_id": sid, "name": data["name"], "identities": len(data["identities"]),
            "bindings": len(data["bindings"]), "resources": len(data["resources"])}

def list_scenarios() -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM rg_scenarios ORDER BY loaded_at DESC")]

def list_identities(scenario_id: str) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM rg_identities WHERE scenario_id=? ORDER BY principal", (scenario_id,))]

def get_identity(scenario_id: str, principal: str) -> dict[str, Any] | None:
    initialize_prototype()
    with _connect() as con:
        row = con.execute("SELECT * FROM rg_identities WHERE scenario_id=? AND principal=?",
                          (scenario_id, principal)).fetchone()
        if row is None:
            return None
        identity = dict(row)
        identity["baseline"] = con.execute(
            "SELECT * FROM rg_baselines WHERE scenario_id=? AND principal=?",
            (scenario_id, principal)).fetchone()
        if identity["baseline"] is not None:
            identity["baseline"] = dict(identity["baseline"])
            identity["baseline"]["required_roles"] = json.loads(identity["baseline"]["required_roles_json"])
        identity["bindings"] = [dict(r) for r in con.execute(
            "SELECT b.binding_id,b.scenario_id,b.principal,b.role,b.resource_id,b.source, "
            "b.condition_text AS condition,b.inherited,b.created_at, "
            "r.name AS resource_name, r.resource_type, r.sensitivity "
            "FROM rg_bindings b LEFT JOIN rg_resources r "
            "ON b.scenario_id=r.scenario_id AND b.resource_id=r.resource_id "
            "WHERE b.scenario_id=? AND b.principal=? ORDER BY b.role",
            (scenario_id, principal))]
        return identity

def _finding_id(sid: str, rule: str, principal: str, resource: str | None, role: str | None) -> str:
    raw = "|".join([sid, rule, principal, resource or "", role or ""])
    return "RG-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()

def analyze_scenario(scenario_id: str) -> list[dict[str, Any]]:
    """Run deterministic, explainable rules against the loaded synthetic snapshot."""
    initialize_prototype()
    findings: list[dict[str, Any]] = []
    with _connect() as con:
        identities = [dict(r) for r in con.execute(
            "SELECT * FROM rg_identities WHERE scenario_id=?", (scenario_id,))]
        resources = {r["resource_id"]: dict(r) for r in con.execute(
            "SELECT * FROM rg_resources WHERE scenario_id=?", (scenario_id,))}
        for identity in identities:
            principal = identity["principal"]
            baseline = con.execute(
                "SELECT * FROM rg_baselines WHERE scenario_id=? AND principal=?",
                (scenario_id, principal)).fetchone()
            baseline = dict(baseline) if baseline else {}
            required = set(json.loads(baseline.get("required_roles_json", "[]")))
            bindings = [dict(r) for r in con.execute(
                "SELECT * FROM rg_bindings WHERE scenario_id=? AND principal=?",
                (scenario_id, principal))]
            granted = {b["role"] for b in bindings}
            confidence = "HIGH" if baseline.get("approval_state") == "APPROVED" else "MEDIUM"

            def add(rule: str, resource: str | None, role: str | None, title: str,
                    description: str, severity: str, recommendation: str, evidence: dict):
                fid = _finding_id(scenario_id, rule, principal, resource, role)
                findings.append({
                    "finding_id": fid, "scenario_id": scenario_id, "rule_id": rule,
                    "principal": principal, "resource_id": resource, "role": role,
                    "title": title, "description": description, "severity": severity,
                    "confidence": confidence, "status": "NEW",
                    "recommendation": recommendation, "evidence": evidence
                })

            for role in sorted(granted - required):
                matching = [b for b in bindings if b["role"] == role]
                for binding in matching:
                    severity = "CRITICAL" if role in HIGH_IMPACT_ROLES else (
                        "HIGH" if role in MEDIUM_HIGH_ROLES else "MEDIUM")
                    add("EXCESS_ROLE", binding["resource_id"], role,
                        "Permission exceeds declared baseline",
                        f"{role} is granted to {principal} but is not listed in its declared required roles.",
                        severity, "Review ownership and remove the grant if it is not required.",
                        {"granted_role": role, "required_roles": sorted(required),
                         "binding_source": binding["source"], "condition": binding["condition_text"]})
            for role in sorted(required - granted):
                add("MISSING_REQUIRED_ROLE", None, role, "Required permission is missing",
                    f"{role} is part of the declared baseline but no matching binding is present.",
                    "MEDIUM", "Confirm the baseline with the owner; do not auto-grant access.",
                    {"required_roles": sorted(required), "observed_roles": sorted(granted)})
            for binding in bindings:
                if binding["role"] not in KNOWN_ROLES:
                    add("UNKNOWN_ROLE", binding["resource_id"], binding["role"],
                        "Role is outside the recognised catalogue",
                        f"{binding['role']} is not present in this prototype's role catalogue.",
                        "HIGH", "Validate the role against the provider's official role definition.",
                        {"role": binding["role"], "binding_source": binding["source"]})
                resource = resources.get(binding["resource_id"], {})
                if resource.get("resource_type") in {"project", "folder"} and binding["role"] not in {"storage.objectViewer"}:
                    add("BROAD_RESOURCE_SCOPE", binding["resource_id"], binding["role"],
                        "Permission is assigned at a broad resource scope",
                        f"{binding['role']} is attached to {resource.get('resource_type')} scope.",
                        "HIGH" if binding["role"] in HIGH_IMPACT_ROLES | MEDIUM_HIGH_ROLES else "MEDIUM",
                        "Review whether a narrower resource-level binding is sufficient.",
                        {"resource_type": resource.get("resource_type"),
                         "resource_name": resource.get("name")})
            if not identity.get("owner"):
                add("MISSING_OWNER", None, None, "Identity has no accountable owner",
                    "No owner is recorded for this non-human identity.", "MEDIUM",
                    "Assign an accountable team or owner before approving access changes.",
                    {"owner": identity.get("owner"), "identity_type": identity["identity_type"]})
            due = identity.get("review_due_at")
            if due:
                try:
                    if date.fromisoformat(due) < date.today():
                        add("STALE_ACCESS_REVIEW", None, None, "Access review is overdue",
                            f"The recorded review date {due} is in the past.", "LOW",
                            "Request an owner review and update the review date after approval.",
                            {"review_due_at": due})
                except ValueError:
                    add("INVALID_REVIEW_DATE", None, None, "Review date is invalid",
                        f"The review date {due} is not a valid ISO date.", "LOW",
                        "Correct the fixture metadata and rerun analysis.", {"review_due_at": due})
        # Upsert findings while preserving analyst workflow state for unchanged finding IDs.
        for f in findings:
            con.execute("""
              INSERT INTO rg_findings VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
              ON CONFLICT(finding_id) DO UPDATE SET
                title=excluded.title, description=excluded.description,
                severity=excluded.severity, confidence=excluded.confidence,
                recommendation=excluded.recommendation, evidence_json=excluded.evidence_json,
                updated_at=excluded.updated_at
            """, (f["finding_id"], f["scenario_id"], f["rule_id"], f["principal"],
                  f["resource_id"], f["role"], f["title"], f["description"], f["severity"],
                  f["confidence"], f["status"], f["recommendation"],
                  json.dumps(f["evidence"], sort_keys=True), _utc(), _utc()))
    return list_findings(scenario_id)

def list_findings(scenario_id: str, statuses: list[str] | None = None) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        sql = "SELECT * FROM rg_findings WHERE scenario_id=?"
        params: list[Any] = [scenario_id]
        if statuses:
            sql += " AND status IN (" + ",".join("?" for _ in statuses) + ")"
            params.extend(statuses)
        sql += " ORDER BY CASE severity WHEN 'CRITICAL' THEN 0 WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END, created_at"
        rows = [dict(r) for r in con.execute(sql, params)]
        for row in rows:
            row["evidence"] = json.loads(row.pop("evidence_json"))
        return rows

def update_finding_status(finding_id: str, new_status: str, actor: str, reason: str) -> None:
    initialize_prototype()
    if not actor.strip() or not reason.strip():
        raise ValueError("Actor and reason are required.")
    with _connect() as con:
        row = con.execute("SELECT * FROM rg_findings WHERE finding_id=?", (finding_id,)).fetchone()
        if row is None:
            raise ValueError("Finding does not exist.")
        if new_status not in FINDING_TRANSITIONS.get(row["status"], set()):
            raise ValueError(f"Invalid finding transition: {row['status']} -> {new_status}")
        now = _utc()
        con.execute("UPDATE rg_findings SET status=?,updated_at=? WHERE finding_id=?",
                    (new_status, now, finding_id))
        con.execute("INSERT INTO rg_finding_history VALUES(?,?,?,?,?,?,?)",
                    ("FH-" + uuid.uuid4().hex[:12].upper(), finding_id,
                     actor.strip(), row["status"], new_status, reason.strip(), now))
        linked_cases = [r["case_id"] for r in con.execute(
            "SELECT case_id FROM rg_case_findings WHERE finding_id=?", (finding_id,))]
        for case_id in linked_cases:
            con.execute("INSERT INTO rg_events VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                ("EVT-" + uuid.uuid4().hex[:12].upper(), case_id, None,
                 row["principal"], actor.strip(), "FINDING_STATE_CHANGE",
                 reason.strip(), json.dumps({"status": row["status"]}),
                 json.dumps({"status": new_status}), "RECORDED", now))

def create_case(scenario_id: str, title: str, actor: str, finding_ids: list[str]) -> str:
    initialize_prototype()
    if not title.strip() or not actor.strip() or not finding_ids:
        raise ValueError("Case title, actor, and at least one finding are required.")
    case_id = "CASE-" + uuid.uuid4().hex[:10].upper()
    with _connect() as con:
        for fid in finding_ids:
            exists = con.execute("SELECT 1 FROM rg_findings WHERE finding_id=? AND scenario_id=?",
                                 (fid, scenario_id)).fetchone()
            if not exists:
                raise ValueError(f"Finding does not belong to this scenario: {fid}")
        now = _utc()
        con.execute("INSERT INTO rg_cases VALUES(?,?,?,?,?,?,?)",
                    (case_id, scenario_id, title.strip(), "OPEN", actor.strip(), now, now))
        con.executemany("INSERT INTO rg_case_findings VALUES(?,?)",
                        [(case_id, fid) for fid in finding_ids])
        for fid in finding_ids:
            con.execute("UPDATE rg_findings SET status='TRIAGED',updated_at=? WHERE finding_id=? AND status='NEW'",
                        (now, fid))
    return case_id

def list_cases(scenario_id: str | None = None) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        if scenario_id:
            rows = con.execute("SELECT * FROM rg_cases WHERE scenario_id=? ORDER BY created_at DESC",
                               (scenario_id,))
        else:
            rows = con.execute("SELECT * FROM rg_cases ORDER BY created_at DESC")
        return [dict(r) for r in rows]

def update_case_status(case_id: str, new_status: str) -> None:
    initialize_prototype()
    with _connect() as con:
        row = con.execute("SELECT status FROM rg_cases WHERE case_id=?", (case_id,)).fetchone()
        if row is None:
            raise ValueError("Case does not exist.")
        if new_status not in CASE_TRANSITIONS.get(row["status"], set()):
            raise ValueError(f"Invalid case transition: {row['status']} -> {new_status}")
        con.execute("UPDATE rg_cases SET status=?,updated_at=? WHERE case_id=?",
                    (new_status, _utc(), case_id))

def _snapshot(con: sqlite3.Connection, scenario_id: str, principal: str) -> dict[str, Any]:
    identity = con.execute("SELECT * FROM rg_identities WHERE scenario_id=? AND principal=?",
                           (scenario_id, principal)).fetchone()
    if identity is None:
        raise ValueError("Identity does not exist in this scenario.")
    bindings = [dict(r) for r in con.execute(
        "SELECT binding_id,role,resource_id,source,condition_text AS condition,inherited FROM rg_bindings WHERE scenario_id=? AND principal=? ORDER BY role,resource_id",
        (scenario_id, principal))]
    return {"identity": dict(identity), "bindings": bindings}

def create_action_plan(case_id: str, principal: str, action_type: str,
                       reason: str, actor: str, finding_ids: list[str] | None = None) -> str:
    initialize_prototype()
    if action_type not in {"REMOVE_EXCESS", "QUARANTINE", "REACTIVATE"}:
        raise ValueError("Action must be REMOVE_EXCESS, QUARANTINE, or REACTIVATE.")
    if not reason.strip() or not actor.strip():
        raise ValueError("Action reason and actor are required.")
    with _connect() as con:
        case = con.execute("SELECT * FROM rg_cases WHERE case_id=?", (case_id,)).fetchone()
        if case is None:
            raise ValueError("Case does not exist.")
        before = _snapshot(con, case["scenario_id"], principal)
        after = json.loads(json.dumps(before))
        if action_type == "REMOVE_EXCESS":
            baseline = con.execute("SELECT required_roles_json FROM rg_baselines WHERE scenario_id=? AND principal=?",
                                   (case["scenario_id"], principal)).fetchone()
            required = set(json.loads(baseline["required_roles_json"])) if baseline else set()
            after["bindings"] = [b for b in before["bindings"] if b["role"] in required]
        elif action_type == "QUARANTINE":
            after["identity"]["lifecycle_state"] = "QUARANTINED"
        else:
            if before["identity"]["lifecycle_state"] != "QUARANTINED":
                raise ValueError("Only quarantined identities can be reactivated.")
            baseline = con.execute("SELECT required_roles_json FROM rg_baselines WHERE scenario_id=? AND principal=?",
                                   (case["scenario_id"], principal)).fetchone()
            required = set(json.loads(baseline["required_roles_json"])) if baseline else set()
            current_roles = {b["role"] for b in before["bindings"]}
            if not current_roles.issubset(required):
                raise ValueError("Remove excess permissions and verify them before reactivation.")
            after["identity"]["lifecycle_state"] = "ACTIVE"
        plan_id = "PLAN-" + uuid.uuid4().hex[:10].upper()
        now = _utc()
        con.execute("INSERT INTO rg_action_plans VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (plan_id, case_id, case["scenario_id"], principal, action_type,
                     reason.strip(), actor.strip(), json.dumps(before, sort_keys=True),
                     json.dumps(after, sort_keys=True), "PENDING_APPROVAL", now, None))
        for fid in (finding_ids or []):
            con.execute("INSERT OR IGNORE INTO rg_case_findings VALUES(?,?)", (case_id, fid))
            con.execute("UPDATE rg_findings SET status='REMEDIATION_PLANNED',updated_at=? WHERE finding_id=? AND status IN ('NEW','TRIAGED')",
                        (now, fid))
        con.execute("UPDATE rg_cases SET status='IN_REVIEW',updated_at=? WHERE case_id=? AND status='OPEN'",
                    (now, case_id))
    return plan_id

def approve_action_plan(plan_id: str, reviewer: str, decision: str, reason: str) -> None:
    initialize_prototype()
    if decision not in {"APPROVED", "REJECTED"}:
        raise ValueError("Decision must be APPROVED or REJECTED.")
    if not reviewer.strip() or not reason.strip():
        raise ValueError("Reviewer and approval reason are required.")
    with _connect() as con:
        plan = con.execute("SELECT * FROM rg_action_plans WHERE plan_id=?", (plan_id,)).fetchone()
        if plan is None:
            raise ValueError("Action plan does not exist.")
        if plan["status"] != "PENDING_APPROVAL":
            raise ValueError("Only pending plans can be reviewed.")
        if reviewer.strip() == plan["created_by"]:
            raise ValueError("Two-person review required: reviewer must differ from plan creator.")
        con.execute("INSERT INTO rg_approvals VALUES(?,?,?,?,?,?)",
                    ("APR-" + uuid.uuid4().hex[:10].upper(), plan_id,
                     reviewer.strip(), decision, reason.strip(), _utc()))
        con.execute("UPDATE rg_action_plans SET status=? WHERE plan_id=?",
                    ("APPROVED" if decision == "APPROVED" else "REJECTED", plan_id))

def execute_action_plan(plan_id: str, actor: str) -> dict[str, Any]:
    initialize_prototype()
    with _connect() as con:
        con.execute("BEGIN IMMEDIATE")
        plan = con.execute("SELECT * FROM rg_action_plans WHERE plan_id=?", (plan_id,)).fetchone()
        if plan is None:
            raise ValueError("Action plan does not exist.")
        if plan["status"] != "APPROVED":
            raise ValueError("Action plan must be approved before execution.")
        current = _snapshot(con, plan["scenario_id"], plan["principal"])
        before = json.loads(plan["before_json"])
        after = json.loads(plan["after_json"])
        if current != before:
            raise ValueError("Current state differs from the reviewed plan; create a new plan.")
        if plan["action_type"] == "REMOVE_EXCESS":
            con.execute("DELETE FROM rg_bindings WHERE scenario_id=? AND principal=?",
                        (plan["scenario_id"], plan["principal"]))
            for b in after["bindings"]:
                con.execute("INSERT INTO rg_bindings VALUES(?,?,?,?,?,?,?,?,?)",
                    (b["binding_id"], plan["scenario_id"], plan["principal"], b["role"],
                     b["resource_id"], b["source"], b["condition"], b["inherited"], _utc()))
        elif plan["action_type"] == "QUARANTINE":
            con.execute("UPDATE rg_identities SET lifecycle_state='QUARANTINED' WHERE scenario_id=? AND principal=?",
                        (plan["scenario_id"], plan["principal"]))
        else:
            con.execute("UPDATE rg_identities SET lifecycle_state='ACTIVE' WHERE scenario_id=? AND principal=?",
                        (plan["scenario_id"], plan["principal"]))
        now = _utc()
        con.execute("UPDATE rg_action_plans SET status='EXECUTED',executed_at=? WHERE plan_id=?",
                    (now, plan_id))
        con.execute("INSERT INTO rg_events VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("EVT-" + uuid.uuid4().hex[:12].upper(), plan["case_id"], plan_id,
             plan["principal"], actor, plan["action_type"], plan["reason"],
             json.dumps(before, sort_keys=True), json.dumps(_snapshot(con, plan["scenario_id"], plan["principal"]), sort_keys=True),
             "EXECUTED_SIMULATION", now))
        return {"plan_id": plan_id, "status": "EXECUTED", "simulated": True}

def verify_action_plan(plan_id: str, actor: str) -> dict[str, Any]:
    initialize_prototype()
    with _connect() as con:
        plan = con.execute("SELECT * FROM rg_action_plans WHERE plan_id=?", (plan_id,)).fetchone()
        if plan is None:
            raise ValueError("Action plan does not exist.")
        if plan["status"] != "EXECUTED":
            raise ValueError("Only executed plans can be verified.")
        actual = _snapshot(con, plan["scenario_id"], plan["principal"])
        expected = json.loads(plan["after_json"])
        passed = actual == expected
        result = "VERIFIED" if passed else "FAILED"
        con.execute("UPDATE rg_action_plans SET status=? WHERE plan_id=?",
                    (result, plan_id))
        con.execute("INSERT INTO rg_events VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ("EVT-" + uuid.uuid4().hex[:12].upper(), plan["case_id"], plan_id,
             plan["principal"], actor, "POST_ACTION_VERIFICATION", "Compare actual state with reviewed plan",
             plan["after_json"], json.dumps(actual, sort_keys=True), result, _utc()))
        if passed and plan["action_type"] == "REMOVE_EXCESS":
            con.execute("UPDATE rg_findings SET status='RESOLVED',updated_at=? WHERE finding_id IN (SELECT finding_id FROM rg_case_findings WHERE case_id=?) AND principal=? AND status='REMEDIATION_PLANNED'",
                        (_utc(), plan["case_id"], plan["principal"]))
        elif passed and plan["action_type"] == "QUARANTINE":
            con.execute("UPDATE rg_findings SET status='CONTAINED',updated_at=? WHERE finding_id IN (SELECT finding_id FROM rg_case_findings WHERE case_id=?) AND principal=? AND status='REMEDIATION_PLANNED'",
                        (_utc(), plan["case_id"], plan["principal"]))
        elif passed and plan["action_type"] == "REACTIVATE":
            con.execute("UPDATE rg_findings SET status='TRIAGED',updated_at=? WHERE finding_id IN (SELECT finding_id FROM rg_case_findings WHERE case_id=?) AND principal=? AND status='CONTAINED'",
                        (_utc(), plan["case_id"], plan["principal"]))
        return {"plan_id": plan_id, "result": result, "expected": expected, "actual": actual}

def list_plans(case_id: str | None = None) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        if case_id:
            rows = con.execute("SELECT * FROM rg_action_plans WHERE case_id=? ORDER BY created_at DESC", (case_id,))
        else:
            rows = con.execute("SELECT * FROM rg_action_plans ORDER BY created_at DESC")
        result = [dict(r) for r in rows]
        for p in result:
            p["before"] = json.loads(p.pop("before_json"))
            p["after"] = json.loads(p.pop("after_json"))
        return result

def list_events(case_id: str) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM rg_events WHERE case_id=? ORDER BY created_at", (case_id,))]

def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    if isinstance(value, str):
        value = re.sub(r"(?i)(token|secret|password|api[_-]?key)(\s*[:=]\s*)[^\s,;]+",
                       r"\1\2[REDACTED]", value)
        value = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
                       "[REDACTED-PRINCIPAL]", value)
        return value
    return value

def export_case_bundle(case_id: str, output_dir: str | Path | None = None,
                       redact: bool = True) -> dict[str, str]:
    initialize_prototype()
    output = Path(output_dir) if output_dir else EXPORT_DIR
    output.mkdir(parents=True, exist_ok=True)
    with _connect() as con:
        case = con.execute("SELECT * FROM rg_cases WHERE case_id=?", (case_id,)).fetchone()
        if case is None:
            raise ValueError("Case does not exist.")
        case_data = dict(case)
        finding_ids = [r["finding_id"] for r in con.execute(
            "SELECT finding_id FROM rg_case_findings WHERE case_id=?", (case_id,))]
        findings = []
        for fid in finding_ids:
            row = con.execute("SELECT * FROM rg_findings WHERE finding_id=?", (fid,)).fetchone()
            if row:
                item = dict(row)
                item["evidence"] = json.loads(item.pop("evidence_json"))
                findings.append(item)
        plans = [dict(r) for r in con.execute("SELECT * FROM rg_action_plans WHERE case_id=?", (case_id,))]
        approvals = [dict(r) for r in con.execute(
            "SELECT a.* FROM rg_approvals a JOIN rg_action_plans p ON a.plan_id=p.plan_id WHERE p.case_id=?",
            (case_id,))]
        events = [dict(r) for r in con.execute("SELECT * FROM rg_events WHERE case_id=?", (case_id,))]
        finding_history = []
        for fid in finding_ids:
            finding_history.extend([dict(r) for r in con.execute(
                "SELECT * FROM rg_finding_history WHERE finding_id=? ORDER BY created_at", (fid,))])
        resources = [dict(r) for r in con.execute(
            "SELECT * FROM rg_resources WHERE scenario_id=?", (case_data["scenario_id"],))]
        relationships = [dict(r) for r in con.execute(
            "SELECT * FROM rg_relationships WHERE scenario_id=?", (case_data["scenario_id"],))]
        scenario = con.execute("SELECT * FROM rg_scenarios WHERE scenario_id=?",
                                (case_data["scenario_id"],)).fetchone()
        principals = sorted({f["principal"] for f in findings} | {p["principal"] for p in plans})
        identities = []
        for principal in principals:
            snap = _snapshot(con, case_data["scenario_id"], principal)
            identities.append(snap)
        payload = {"case": case_data, "scenario": dict(scenario) if scenario else {},
                   "resources": resources, "relationships": relationships,
                   "identities": identities, "findings": findings,
                   "finding_history": finding_history, "action_plans": plans,
                   "approvals": approvals, "events": events,
                   "exported_at": _utc(), "simulation_notice": "Synthetic local simulation; not evidence of cloud-side changes."}
    if redact:
        payload = _redact(payload)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"{case_id.lower()}_{stamp}"
    json_path = output / f"{stem}.json"
    csv_path = output / f"{stem}_findings.csv"
    manifest_path = output / f"{stem}_manifest.json"
    json_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    json_path.write_bytes(json_bytes)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "finding_id", "rule_id", "principal", "resource_id", "role",
            "title", "severity", "confidence", "status", "recommendation"])
        writer.writeheader()
        for f in payload["findings"]:
            writer.writerow({k: f.get(k) for k in writer.fieldnames})
    manifest = {
        "case_id": case_id, "algorithm": "SHA-256",
        "files": {
            json_path.name: hashlib.sha256(json_path.read_bytes()).hexdigest(),
            csv_path.name: hashlib.sha256(csv_path.read_bytes()).hexdigest()
        },
        "redacted": redact,
        "warning": "Hashes detect changes relative to this manifest; they do not provide immutable storage."
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "manifest": str(manifest_path)}

def dashboard_summary(scenario_id: str) -> dict[str, int]:
    identities = list_identities(scenario_id)
    findings = list_findings(scenario_id)
    return {
        "identities": len(identities),
        "active": sum(i["lifecycle_state"] == "ACTIVE" for i in identities),
        "quarantined": sum(i["lifecycle_state"] == "QUARANTINED" for i in identities),
        "findings": len(findings),
        "critical": sum(f["severity"] == "CRITICAL" for f in findings),
        "high": sum(f["severity"] == "HIGH" for f in findings),
        "open_cases": sum(c["status"] != "CLOSED" for c in list_cases(scenario_id))
    }


def list_resources(scenario_id: str) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM rg_resources WHERE scenario_id=? ORDER BY resource_type,name",
            (scenario_id,))]

def list_relationships(scenario_id: str) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM rg_relationships WHERE scenario_id=? ORDER BY relationship_type",
            (scenario_id,))]

def get_case(case_id: str) -> dict[str, Any] | None:
    initialize_prototype()
    with _connect() as con:
        row=con.execute("SELECT * FROM rg_cases WHERE case_id=?", (case_id,)).fetchone()
        if row is None:
            return None
        case=dict(row)
        case["findings"]=[dict(r) for r in con.execute(
            "SELECT f.* FROM rg_findings f JOIN rg_case_findings cf ON cf.finding_id=f.finding_id "
            "WHERE cf.case_id=? ORDER BY f.severity,f.created_at",(case_id,))]
        for finding in case["findings"]:
            finding["evidence"]=json.loads(finding.pop("evidence_json"))
        return case

def get_plan(plan_id: str) -> dict[str, Any] | None:
    initialize_prototype()
    with _connect() as con:
        row=con.execute("SELECT * FROM rg_action_plans WHERE plan_id=?", (plan_id,)).fetchone()
        if row is None:
            return None
        plan=dict(row)
        plan["before"]=json.loads(plan.pop("before_json"))
        plan["after"]=json.loads(plan.pop("after_json"))
        plan["approvals"]=[dict(r) for r in con.execute(
            "SELECT * FROM rg_approvals WHERE plan_id=? ORDER BY created_at",(plan_id,))]
        return plan


def list_finding_history(finding_id: str) -> list[dict[str, Any]]:
    initialize_prototype()
    with _connect() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM rg_finding_history WHERE finding_id=? ORDER BY created_at",
            (finding_id,))]
