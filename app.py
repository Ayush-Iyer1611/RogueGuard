
import json
import streamlit as st

from core import (
    assess_account,
    remediate_permissions,
)
from database import (
    init_db,
    get_accounts,
    get_account,
    contain_account,
    restore_account,
    audit_rows,
    reset_demo_data,
)


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="RogueGuard | Identity Security",
    page_icon="🛡️",
    layout="wide",
)

init_db()

st.title("🛡️ RogueGuard")
st.caption(
    "Service Account Security Auditor · Synthetic Campus Environment"
)

st.warning(
    "Training simulation only. This dashboard does not connect "
    "to or modify real Google Cloud identities."
)

# --------------------------------------------------
# DEMO ENVIRONMENT RESET
# --------------------------------------------------

with st.sidebar.expander("Demo Environment Controls"):

    st.warning(
        "Resetting will erase all demo account changes "
        "and audit events."
    )

    reset_confirm = st.checkbox(
        "I understand and want to reset the demo environment.",
        key="reset_demo_confirmation",
    )

    if st.button(
        "Reset Everything",
        type="primary",
        disabled=not reset_confirm,
        use_container_width=True,
    ):

        try:
            reset_demo_data()

            st.success("Demo environment successfully reset.")
            st.rerun()

        except Exception as error:
            st.error(f"Reset failed: {error}")


# --------------------------------------------------
# DATA AND SECURITY METRICS
# --------------------------------------------------

accounts = get_accounts()

assessments = {
    account["email"]: assess_account({
        "principal": account["email"],
        "granted_roles": json.loads(account["roles"]),
        "required_roles": json.loads(account["required_roles"]),
        "status": account["status"],
    })
    for account in accounts
}

active = [
    account for account in accounts
    if account["status"] == "ACTIVE"
]

flagged = [
    account for account in active
    if assessments[account["email"]]["risk_score"] >= 40
]

quarantined = [
    account for account in accounts
    if account["status"] == "QUARANTINED"
]


c1, c2, c3, c4 = st.columns(4)

c1.metric("Service identities", len(accounts))
c2.metric("Active identities", len(active))
c3.metric("High-risk identities", len(flagged))
c4.metric("Contained identities", len(quarantined))


# --------------------------------------------------
# DASHBOARD TABS
# --------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "Identity inventory",
    "Containment console",
    "Audit trail",
])


# --------------------------------------------------
# TAB 1: IDENTITY INVENTORY
# --------------------------------------------------

with tab1:

    st.subheader("Identity inventory and access review")

    for account in accounts:

        assessment = assessments[account["email"]]

        with st.expander(
            f"{account['email']} · "
            f"{account['status']} · "
            f"Risk {assessment['risk_score']}/100"
        ):

            st.write("**Purpose:**", account["purpose"])
            st.write("**Owner:**", account["owner"])

            resources = json.loads(account["resources"])
            granted = json.loads(account["roles"])
            required = json.loads(account["required_roles"])

            st.write(
                "**Resource scope:**",
                ", ".join(resources),
            )

            st.write(
                "**Granted roles:**",
                ", ".join(granted) or "None",
            )

            st.write(
                "**Required roles:**",
                ", ".join(required) or "None",
            )

            if assessment["excess_roles"]:

                st.error(
                    "Excess permissions: "
                    + ", ".join(assessment["excess_roles"])
                )

            else:

                st.success(
                    "No excess permissions detected "
                    "against the declared purpose."
                )

            if assessment["missing_roles"]:

                st.warning(
                    "Missing required permissions: "
                    + ", ".join(assessment["missing_roles"])
                )

            st.write(
                "**Risk classification:**",
                assessment["risk_level"],
            )


    st.subheader("Risk findings")

    findings = []

    for account in active:

        assessment = assessments[account["email"]]

        if assessment["excess_roles"]:

            findings.append({
                "Identity": account["email"],
                "Risk score": assessment["risk_score"],
                "Risk level": assessment["risk_level"],
                "Excess grants": ", ".join(
                    assessment["excess_roles"]
                ),
                "Owner": account["owner"],
            })

    if findings:

        st.dataframe(
            findings,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.success("No excess grants detected.")


# --------------------------------------------------
# TAB 2: CONTAINMENT CONSOLE
# --------------------------------------------------

with tab2:

    st.subheader("Containment console")

    st.write(
        "Review the synthetic identity, identify excessive grants, "
        "and simulate least-privilege containment."
    )

    candidates = [
        account for account in accounts
        if account["status"] == "ACTIVE"
    ]

    if candidates:

        chosen = st.selectbox(
            "Select an identity",
            [account["email"] for account in candidates],
        )

        selected = get_account(chosen)

        assessment = assessments[chosen]

        granted = json.loads(selected["roles"])
        required = json.loads(selected["required_roles"])

        retained = remediate_permissions(granted, required)

        st.write(
            f"Risk score: **{assessment['risk_score']}/100**"
        )

        st.write(
            "Risk level:",
            assessment["risk_level"],
        )

        st.write(
            "**Permissions to remove:**",
            ", ".join(assessment["excess_roles"]) or "None",
        )

        st.write(
            "**Permissions to retain:**",
            ", ".join(retained) or "None",
        )

        if assessment["missing_roles"]:

            st.warning(
                "Some required permissions are already missing. "
                "Containment will not automatically grant them."
            )

        confirm = st.checkbox(
            "I confirm this is a synthetic demo identity "
            "and want to contain it."
        )

        if st.button(
            "Contain selected identity",
            type="primary",
            disabled=not confirm,
        ):

            try:

                evidence = contain_account(chosen, retained)

                st.success(
                    "Containment simulated successfully. "
                    "Audit evidence recorded."
                )

                st.json(evidence)

                st.rerun()

            except ValueError as error:

                st.error(str(error))

    else:

        st.info("No active identities remain.")


    if quarantined:

        st.divider()
        st.markdown("**Quarantined identities**")

        for account in quarantined:

            st.write(account["email"])

            if st.button(
                f"Reactivate {account['email']}",
                key=f"restore_{account['email']}",
            ):

                try:

                    restore_account(account["email"])

                    st.warning(
                        "Account reactivated without restoring "
                        "previous excessive permissions. "
                        "Human review is required."
                    )

                    st.rerun()

                except ValueError as error:

                    st.error(str(error))


# --------------------------------------------------
# TAB 3: AUDIT TRAIL
# --------------------------------------------------

with tab3:

    st.subheader("Security audit trail")

    events = audit_rows()

    if events:

        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No events recorded yet. "
            "Containment and status changes will appear here."
        )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Risk score is a transparent demonstration heuristic, "
    "not a cloud-provider risk rating. "
    "Validate actual IAM permissions and service support "
    "in the assigned Floci sandbox before making operational claims."
)
