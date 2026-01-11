"""FCR Section Autofill - Generate GNOC-ready content for FCR sections.

Only 1 required typed field (purpose). Everything else defaults.
Does NOT replace the official Word FCR form - generates CONTENT only.
"""

from dataclasses import dataclass
from typing import Any

from netops_skills.common.render import render_template
from netops_skills.common.utils import get_current_timestamp, load_defaults


@dataclass
class FCRInput:
    """Schema for FCR autofill input."""
    purpose: str
    change_type: str = "firewall_rule"
    rule_count: str = "single"
    direction: str = "inbound"
    risk_level: str = "low"
    environment: str = "prod"

    def validate(self) -> list[str]:
        errors = []
        if not self.purpose or not self.purpose.strip():
            errors.append("purpose is required")
        return errors


# Content generators based on change_type
TECHNICAL_DESCRIPTIONS = {
    "firewall_rule": "Add firewall rule to {direction} traffic for {purpose}. Rule count: {rule_count}.",
    "nat_change": "Configure NAT translation for {purpose}. Direction: {direction}.",
    "f5_ssl": "Update F5 SSL profile/certificate for {purpose}.",
    "routing_change": "Modify routing configuration for {purpose}. Direction: {direction}.",
    "acl_update": "Update access control list for {purpose}. Direction: {direction}.",
    "vpn_config": "Configure VPN settings for {purpose}.",
}

TESTS_BY_TYPE = {
    "firewall_rule": [
        "Verify rule syntax in staging/lab environment",
        "Confirm source/destination objects exist",
        "Test connectivity with rule in place (lab)",
        "Verify logging is enabled for new rule",
    ],
    "nat_change": [
        "Verify NAT translation in lab environment",
        "Confirm IP addresses are not in use elsewhere",
        "Test end-to-end connectivity through NAT",
    ],
    "f5_ssl": [
        "Validate certificate chain completeness",
        "Verify certificate expiry date",
        "Test SSL handshake in staging",
        "Confirm cipher suite compatibility",
    ],
    "routing_change": [
        "Verify route does not conflict with existing routes",
        "Test reachability in lab environment",
        "Confirm BGP/OSPF adjacencies stable after change",
    ],
    "acl_update": [
        "Verify ACL syntax",
        "Test ACL in lab environment",
        "Confirm no unintended traffic blocked",
    ],
    "vpn_config": [
        "Verify tunnel parameters match peer",
        "Test tunnel establishment in lab",
        "Confirm encryption settings are compliant",
    ],
}

ROLLBACK_BY_TYPE = {
    "firewall_rule": [
        "Remove newly added rule(s)",
        "Restore previous rule configuration if modified",
        "Verify traffic flow returns to pre-change state",
    ],
    "nat_change": [
        "Remove NAT translation entry",
        "Restore original NAT configuration",
        "Verify connectivity restored",
    ],
    "f5_ssl": [
        "Revert to previous SSL profile",
        "Restore previous certificate",
        "Verify SSL termination functional",
    ],
    "routing_change": [
        "Remove added route(s)",
        "Restore previous routing configuration",
        "Verify routing table stable",
    ],
    "acl_update": [
        "Revert ACL to previous version",
        "Verify traffic flow restored",
    ],
    "vpn_config": [
        "Disable new VPN configuration",
        "Restore previous VPN settings",
        "Verify tunnel stability",
    ],
}

IMPACT_BY_RISK = {
    "low": "Minimal impact expected. Change affects limited scope with no service disruption.",
    "medium": "Moderate impact possible. Brief connectivity interruption may occur during implementation.",
    "high": "Significant impact possible. Service disruption expected during maintenance window.",
}

ROLLBACK_TIME = {"low": "< 5 minutes", "medium": "5-15 minutes", "high": "15-30 minutes"}

CHECKLIST_ITEMS = [
    "Change reviewed and approved by team lead",
    "Rollback procedure documented and tested",
    "Maintenance window scheduled (if required)",
    "Stakeholders notified",
    "Monitoring alerts configured",
]

EVIDENCE_CHECKLIST = [
    "Pre-change configuration backup",
    "Screenshot of change implementation",
    "Post-change verification results",
    "Test results documentation",
]


def generate_fcr_content(
    purpose: str,
    change_type: str = "firewall_rule",
    rule_count: str = "single",
    direction: str = "inbound",
    risk_level: str = "low",
    environment: str = "prod",
) -> str:
    """Generate FCR section content."""
    input_data = FCRInput(
        purpose=purpose,
        change_type=change_type,
        rule_count=rule_count,
        direction=direction,
        risk_level=risk_level,
        environment=environment,
    )

    errors = input_data.validate()
    if errors:
        raise ValueError(f"Invalid input: {', '.join(errors)}")

    # Build technical description
    tech_template = TECHNICAL_DESCRIPTIONS.get(change_type, TECHNICAL_DESCRIPTIONS["firewall_rule"])
    technical_description = tech_template.format(
        purpose=purpose, direction=direction, rule_count=rule_count
    )

    context = {
        "purpose": purpose,
        "change_type": change_type,
        "rule_count": rule_count,
        "direction": direction,
        "risk_level": risk_level,
        "environment": environment,
        "technical_description": technical_description,
        "tests_conducted": TESTS_BY_TYPE.get(change_type, TESTS_BY_TYPE["firewall_rule"]),
        "rollback_options": ROLLBACK_BY_TYPE.get(change_type, ROLLBACK_BY_TYPE["firewall_rule"]),
        "rollback_time": ROLLBACK_TIME.get(risk_level, "< 5 minutes"),
        "impact_statement": IMPACT_BY_RISK.get(risk_level, IMPACT_BY_RISK["low"]),
        "affected_systems": [f"{environment.upper()} {change_type.replace('_', ' ').title()} infrastructure"],
        "checklist_justification": CHECKLIST_ITEMS,
        "evidence_checklist": EVIDENCE_CHECKLIST,
        "timestamp": get_current_timestamp(),
    }

    return render_template("fcr_sections.md", context)


def generate_from_yaml(yaml_data: dict[str, Any]) -> str:
    """Generate FCR content from YAML input."""
    return generate_fcr_content(
        purpose=yaml_data.get("purpose", ""),
        change_type=yaml_data.get("change_type", "firewall_rule"),
        rule_count=yaml_data.get("rule_count", "single"),
        direction=yaml_data.get("direction", "inbound"),
        risk_level=yaml_data.get("risk_level", "low"),
        environment=yaml_data.get("environment", "prod"),
    )
