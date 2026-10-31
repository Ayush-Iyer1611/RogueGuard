
"""
RogueGuard - Core Security Engine

This module analyses synthetic service-account permissions.
It does not connect to or modify any real cloud environment.
"""

ROLE_RISK = {
    "storage.objectViewer": 2,
    "storage.objectCreator": 3,
    "storage.objectAdmin": 7,
    "storage.admin": 9,
    "secretmanager.secretAccessor": 8,
    "iam.serviceAccountTokenCreator": 9,
    "iam.serviceAccountAdmin": 10,
}


def analyse_permissions(granted_roles, required_roles):
    """Identify excessive and missing permissions."""

    granted = set(granted_roles)
    required = set(required_roles)

    return {
        "excess_roles": sorted(granted - required),
        "missing_roles": sorted(required - granted),
        "compliant": granted == required,
    }


def calculate_risk(excess_roles):
    """Calculate a demonstrative risk score from excessive roles."""

    score = sum(ROLE_RISK.get(role, 5) for role in excess_roles)
    return min(score * 8, 100)


def get_risk_level(score):
    """Convert a numerical score into a risk classification."""

    if score >= 80:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "NONE"


def assess_account(account):
    """Assess one synthetic service account."""

    permissions = analyse_permissions(
        account.get("granted_roles", []),
        account.get("required_roles", []),
    )

    active = account.get("status", "ACTIVE") == "ACTIVE"

    score = calculate_risk(permissions["excess_roles"]) if active else 0

    return {
        "principal": account.get("principal", "UNKNOWN"),
        "status": account.get("status", "ACTIVE"),
        "excess_roles": permissions["excess_roles"],
        "missing_roles": permissions["missing_roles"],
        "risk_score": score,
        "risk_level": get_risk_level(score),
        "compliant": permissions["compliant"],
    }


def remediate_permissions(granted_roles, required_roles):
    """
    Return the least-privilege role set.

    This is a local simulation. It does not modify cloud IAM.
    """

    granted = set(granted_roles)
    required = set(required_roles)

    # Only remove excess permissions.
    # Missing permissions are not automatically granted.
    return sorted(granted - (granted - required))


def access_decision(account, requested_role):
    """Simulate an authorization decision for a service account."""

    if account.get("status", "ACTIVE") != "ACTIVE":
        return {
            "allowed": False,
            "reason": "Account is not active.",
        }

    if requested_role not in account.get("granted_roles", []):
        return {
            "allowed": False,
            "reason": "Requested permission is not granted.",
        }

    return {
        "allowed": True,
        "reason": "Permission is present and account is active.",
    }
