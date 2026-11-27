import json
from pathlib import Path

import streamlit as st
import prototype as rg


st.set_page_config(
    page_title="RogueGuard v0.9 | Identity Security Workbench",
    page_icon="🛡️",
    layout="wide",
)

rg.initialize_prototype()
available = rg.available_scenarios()
loaded = rg.list_scenarios()

if not available:
    st.error("No synthetic scenario fixtures were found in fixtures/scenarios.")
    st.stop()

available_ids = {x["scenario_id"] for x in available}
if "rg_scenario_id" not in st.session_state or st.session_state.rg_scenario_id not in available_ids:
    st.session_state.rg_scenario_id = (
        loaded[0]["scenario_id"] if loaded else available[0]["scenario_id"]
    )

st.title("RogueGuard")
st.caption("Identity Exposure · Permission Intelligence · Response Planning")
st.warning(
    "LOCAL SYNTHETIC SIMULATION — this workbench does not connect to or modify "
    "Google Cloud IAM, credentials, storage, secrets, or production resources."
)

with st.sidebar:
    st.header("Workspace")
    selected_scenario = st.selectbox(
        "Scenario fixture",
        options=[x["scenario_id"] for x in available],
        index=[x["scenario_id"] for x in available].index(st.session_state.rg_scenario_id),
        format_func=lambda sid: next(x["name"] for x in available if x["scenario_id"] == sid),
    )
    loaded_ids = {x["scenario_id"] for x in rg.list_scenarios()}
    if st.button("Load / analyse scenario", type="primary", use_container_width=True):
        try:
            if selected_scenario not in loaded_ids:
                info = rg.load_scenario(selected_scenario)
                st.success(f"Loaded {info['name']}")
            findings = rg.analyze_scenario(selected_scenario)
            st.session_state.rg_scenario_id = selected_scenario
            st.session_state.rg_selected_finding = None
            st.success(f"Analysis complete: {len(findings)} findings.")
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    st.divider()
    st.markdown("**Prototype boundary**")
    st.caption("All identities, bindings, actions, approvals, and evidence in this workspace are synthetic.")
    st.caption("Response actions are simulated in the local SQLite model only.")
    st.caption("A generated hash manifest detects changes; it is not immutable storage.")

sid = st.session_state.rg_scenario_id
loaded_now = {x["scenario_id"] for x in rg.list_scenarios()}
if sid not in loaded_now:
    try:
        rg.load_scenario(sid)
    except Exception as exc:
        st.error(f"Could not load scenario: {exc}")
        st.stop()

if not rg.list_findings(sid):
    rg.analyze_scenario(sid)

summary = rg.dashboard_summary(sid)
scenario_record = next((x for x in rg.list_scenarios() if x["scenario_id"] == sid), {})
findings = rg.list_findings(sid)

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Identities", summary["identities"])
m2.metric("Open findings", sum(f["status"] not in {"RESOLVED", "RETESTED", "FALSE_POSITIVE"} for f in findings))
m3.metric("Critical", summary["critical"])
m4.metric("High", summary["high"])
m5.metric("Open cases", summary["open_cases"])

st.caption(
    f"Scenario: **{scenario_record.get('name', sid)}** · "
    f"Fixture version: **{scenario_record.get('version', 'unknown')}** · "
    f"Environment: **synthetic demo**"
)

overview, identities_tab, findings_tab, response_tab, cases_tab = st.tabs([
    "Overview", "Identity explorer", "Findings", "Response lab", "Cases & evidence"
])

with overview:
    st.subheader("Security overview")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("#### Finding distribution")
        distribution = {}
        for f in findings:
            distribution[f["severity"]] = distribution.get(f["severity"], 0) + 1
        if distribution:
            st.bar_chart(distribution)
        else:
            st.info("No findings. Run analysis or load another scenario.")
    with right:
        st.markdown("#### Finding queue")
        if findings:
            st.dataframe(
                [{"ID": f["finding_id"], "Severity": f["severity"],
                  "State": f["status"], "Rule": f["rule_id"],
                  "Identity": f["principal"]} for f in findings],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No findings to display.")

    st.markdown("#### Identity relationship context")
    relationships = rg.list_relationships(sid)
    if relationships:
        dot = ["digraph RogueGuard {", 'rankdir="LR";', 'node [shape=box, style="rounded,filled", fillcolor="#e8f1fa", color="#38546d"];']
        principals = {i["principal"] for i in rg.list_identities(sid)}
        for p in principals:
            dot.append(f'"{p}" [label="{p}"];')
        for r in relationships:
            dot.append(f'"{r["source_principal"]}" -> "{r["target_principal"]}" [label="{r["relationship_type"]}"];')
        dot.append("}")
        st.graphviz_chart("\n".join(dot), use_container_width=True)
        st.caption("Relationship edges are synthetic fixture assertions, not independently discovered trust paths.")
    else:
        st.info("This scenario has no relationship edges.")

    st.markdown("#### Release boundary")
    st.info(
        "v0.9 target: investigate a finding, preview a response, obtain a separate reviewer approval, "
        "simulate the response, verify the result, and export case evidence."
    )

with identities_tab:
    st.subheader("Identity explorer")
    identities = rg.list_identities(sid)
    principal = st.selectbox("Select an identity", [x["principal"] for x in identities], key="rg_identity")
    identity = rg.get_identity(sid, principal)
    if identity:
        a, b, c = st.columns(3)
        a.metric("Lifecycle", identity["lifecycle_state"])
        b.metric("Bindings", len(identity["bindings"]))
        c.metric("Baseline", identity["baseline"]["approval_state"] if identity["baseline"] else "MISSING")
        st.write("**Owner:**", identity.get("owner") or "Unassigned")
        st.write("**Purpose:**", identity.get("purpose") or "Not documented")
        st.write("**Identity type:**", identity["identity_type"])
        st.write("**Environment:**", identity["environment"])
        st.write("**Last observed:**", identity.get("last_observed_at") or "Unknown")
        st.write("**Review due:**", identity.get("review_due_at") or "Not set")
        st.markdown("#### Declared baseline")
        baseline = identity["baseline"] or {}
        st.write("**Version:**", baseline.get("version", "n/a"))
        st.write("**Rationale:**", baseline.get("rationale") or "No rationale supplied")
        st.write("**Required roles:**", ", ".join(baseline.get("required_roles", [])) or "None")
        st.markdown("#### Resource-level bindings")
        if identity["bindings"]:
            st.dataframe(
                [{"Role": x["role"], "Resource": x["resource_name"],
                  "Resource ID": x["resource_id"], "Scope": x["resource_type"],
                  "Sensitivity": x["sensitivity"], "Source": x["source"],
                  "Condition": x["condition"] or "None",
                  "Inherited": bool(x["inherited"])} for x in identity["bindings"]],
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No bindings are recorded for this identity.")

with findings_tab:
    st.subheader("Finding inbox")
    status_options = ["ALL", "NEW", "TRIAGED", "ACCEPTED", "FALSE_POSITIVE",
                      "REMEDIATION_PLANNED", "RESOLVED", "RETESTED"]
    chosen_status = st.selectbox("Filter by state", status_options)
    visible = findings if chosen_status == "ALL" else [f for f in findings if f["status"] == chosen_status]
    if visible:
        st.dataframe(
            [{"ID": f["finding_id"], "Severity": f["severity"],
              "Confidence": f["confidence"], "State": f["status"],
              "Rule": f["rule_id"], "Identity": f["principal"],
              "Resource": f["resource_id"] or "Identity metadata",
              "Finding": f["title"]} for f in visible],
            use_container_width=True, hide_index=True
        )
        finding_ids = [f["finding_id"] for f in visible]
        selected_fid = st.selectbox(
            "Inspect finding",
            finding_ids,
            format_func=lambda fid: next(
                f"{x['severity']} · {x['title']} · {x['principal']}"
                for x in visible if x["finding_id"] == fid
            ),
        )
        detail = next(x for x in visible if x["finding_id"] == selected_fid)
        st.markdown(f"### {detail['title']}")
        st.write(detail["description"])
        d1, d2, d3 = st.columns(3)
        d1.metric("Severity", detail["severity"])
        d2.metric("Evidence confidence", detail["confidence"])
        d3.metric("Workflow state", detail["status"])
        st.write("**Rule:**", detail["rule_id"])
        st.write("**Recommendation:**", detail["recommendation"])
        st.json(detail["evidence"])
        allowed = sorted(rg.FINDING_TRANSITIONS.get(detail["status"], set()))
        if allowed:
            with st.form("finding_transition_form"):
                next_state = st.selectbox("Move finding to", allowed)
                actor = st.text_input("Analyst", value="analyst")
                reason = st.text_input("Reason for state change")
                submitted = st.form_submit_button("Update finding state")
            if submitted:
                try:
                    rg.update_finding_status(selected_fid, next_state, actor, reason)
                    st.success("Finding state updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        else:
            st.caption("No further state transition is available from this state.")

        st.divider()
        st.markdown("#### Open a case from selected findings")
        selected_for_case = st.multiselect(
            "Findings to group into a case",
            [x["finding_id"] for x in findings if x["status"] not in {"FALSE_POSITIVE", "RETESTED"}],
            default=[selected_fid],
            format_func=lambda fid: next(
                f"{x['severity']} · {x['title']}" for x in findings if x["finding_id"] == fid
            ),
        )
        with st.form("create_case_form"):
            title = st.text_input("Case title", value=f"Review: {detail['principal']}")
            creator = st.text_input("Case creator", value="analyst")
            create_submitted = st.form_submit_button("Create case")
        if create_submitted:
            try:
                case_id = rg.create_case(sid, title, creator, selected_for_case)
                st.success(f"Created {case_id}")
            except Exception as exc:
                st.error(str(exc))
    else:
        st.info("No findings match this filter.")

with response_tab:
    st.subheader("Response planning lab")
    st.caption("Two-person approval is required. Execution changes only the local synthetic dataset.")
    cases = rg.list_cases(sid)
    if not cases:
        st.info("Create a case from one or more findings before planning a response.")
    else:
        case_ids = [x["case_id"] for x in cases]
        chosen_case = st.selectbox("Case", case_ids, format_func=lambda cid: next(
            f"{x['case_id']} · {x['title']} · {x['status']}" for x in cases if x["case_id"] == cid
        ), key="response_case")
        case = rg.get_case(chosen_case)
        case_principals = sorted({f["principal"] for f in case["findings"]})
        if not case_principals:
            case_principals = [x["principal"] for x in rg.list_identities(sid)]
        with st.form("create_plan_form"):
            target = st.selectbox("Target identity", case_principals)
            action = st.selectbox(
                "Response action",
                ["REMOVE_EXCESS", "QUARANTINE"],
                format_func=lambda x: "Remove excess permissions only" if x == "REMOVE_EXCESS" else "Quarantine identity only"
            )
            reason = st.text_area("Operator reason", placeholder="Explain why this simulated action is appropriate.")
            creator = st.text_input("Plan creator", value="analyst")
            plan_submitted = st.form_submit_button("Generate dry-run plan")
        if plan_submitted:
            try:
                related_ids = [f["finding_id"] for f in case["findings"] if f["principal"] == target]
                plan_id = rg.create_action_plan(chosen_case, target, action, reason, creator, related_ids)
                st.session_state.rg_plan_id = plan_id
                st.success(f"Dry-run plan created: {plan_id}")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

        plans = rg.list_plans(chosen_case)
        if plans:
            plan_ids = [p["plan_id"] for p in plans]
            default_plan = st.session_state.get("rg_plan_id")
            index = plan_ids.index(default_plan) if default_plan in plan_ids else 0
            chosen_plan = st.selectbox("Review existing plan", plan_ids, index=index, key="review_plan")
            plan = rg.get_plan(chosen_plan)
            st.write("**Action:**", plan["action_type"])
            st.write("**Status:**", plan["status"])
            st.write("**Reason:**", plan["reason"])
            before, after = st.columns(2)
            with before:
                st.markdown("#### Before")
                st.json(plan["before"])
            with after:
                st.markdown("#### Proposed after")
                st.json(plan["after"])

            if plan["status"] == "PENDING_APPROVAL":
                st.markdown("#### Independent review")
                with st.form("approval_form"):
                    reviewer = st.text_input("Reviewer (must differ from creator)", value="reviewer")
                    decision = st.selectbox("Decision", ["APPROVED", "REJECTED"])
                    approval_reason = st.text_input("Review rationale")
                    approval_submitted = st.form_submit_button("Record review decision")
                if approval_submitted:
                    try:
                        rg.approve_action_plan(chosen_plan, reviewer, decision, approval_reason)
                        st.success(f"Plan {decision.lower()}.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif plan["status"] == "APPROVED":
                operator = st.text_input("Execution operator", value="operator", key="execute_actor")
                if st.button("Execute simulated action", type="primary"):
                    try:
                        rg.execute_action_plan(chosen_plan, operator)
                        st.success("Local simulation action executed.")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif plan["status"] == "EXECUTED":
                verifier = st.text_input("Verifier", value="verifier", key="verify_actor")
                if st.button("Verify post-action state"):
                    try:
                        result = rg.verify_action_plan(chosen_plan, verifier)
                        st.success(f"Verification: {result['result']}")
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
            elif plan["status"] in {"VERIFIED", "FAILED", "REJECTED"}:
                st.info(f"Plan is finalised with status: {plan['status']}")
            if plan["approvals"]:
                st.markdown("#### Approval history")
                st.dataframe(plan["approvals"], use_container_width=True, hide_index=True)

with cases_tab:
    st.subheader("Cases and evidence")
    cases = rg.list_cases(sid)
    if not cases:
        st.info("No cases have been created for this scenario yet.")
    else:
        selected_case_id = st.selectbox("Select case", [x["case_id"] for x in cases],
            format_func=lambda cid: next(f"{x['case_id']} · {x['title']} · {x['status']}" for x in cases if x["case_id"] == cid),
            key="evidence_case")
        case = rg.get_case(selected_case_id)
        st.write("**Created by:**", case["created_by"])
        st.write("**Created:**", case["created_at"])
        st.write("**Current state:**", case["status"])
        st.markdown("#### Included findings")
        if case["findings"]:
            st.dataframe([{"ID":f["finding_id"],"Severity":f["severity"],"State":f["status"],
                "Rule":f["rule_id"],"Principal":f["principal"],"Title":f["title"]}
                for f in case["findings"]], use_container_width=True, hide_index=True)
        with st.expander("Case timeline"):
            events = rg.list_events(selected_case_id)
            if events:
                st.dataframe(events, use_container_width=True, hide_index=True)
            else:
                st.info("No response events have been recorded yet.")
        c1, c2 = st.columns(2)
        with c1:
            new_case_state = st.selectbox("Case state", sorted(rg.CASE_TRANSITIONS.get(case["status"], set())))
            if st.button("Update case state", disabled=not rg.CASE_TRANSITIONS.get(case["status"], set())):
                try:
                    rg.update_case_status(selected_case_id, new_case_state)
                    st.success("Case state updated.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        with c2:
            redact = st.checkbox("Redact sensitive strings in export", value=True)
            if st.button("Export case evidence bundle", type="primary"):
                try:
                    paths = rg.export_case_bundle(selected_case_id, redact=redact)
                    st.session_state.rg_export_paths = paths
                    st.success("Evidence bundle exported. Synthetic simulation notice included.")
                except Exception as exc:
                    st.error(str(exc))
        if st.session_state.get("rg_export_paths"):
            paths = st.session_state.rg_export_paths
            st.markdown("#### Download evidence")
            for label, key in [("Case JSON","json"),("Findings CSV","csv"),("SHA-256 manifest","manifest")]:
                path = paths.get(key)
                if path and Path(path).exists():
                    st.download_button(
                        f"Download {label}",
                        data=Path(path).read_bytes(),
                        file_name=Path(path).name,
                        mime="application/json" if key != "csv" else "text/csv",
                        key=f"download_{key}"
                    )

st.divider()
st.caption(
    "RogueGuard v0.9 final-prototype workbench · Synthetic data only · "
    "A local hash manifest is not immutable storage · Cloud integration is not implemented."
)
