"""Incident Update Composer - Generate ready-to-send incident updates from minimal input.

This skill reduces the time spent drafting incident communications by:
- Requiring only 2 typed fields (incident_title, impact_summary)
- Auto-filling all other fields with smart defaults
- Generating appropriate next steps based on status
- Creating audience-specific formatting (manager vs client)
"""

from dataclasses import asdict
from typing import Any

from netops_skills.common.render import (
    format_bullet_list,
    format_numbered_list,
    render_template,
)
from netops_skills.common.schema import IncidentInput
from netops_skills.common.utils import (
    get_current_timestamp,
    load_defaults,
    merge_with_defaults,
)


def get_next_steps(status: str, defaults: dict[str, Any]) -> list[str]:
    """Get auto-generated next steps based on current status.

    Args:
        status: Current incident status
        defaults: Loaded defaults configuration

    Returns:
        List of next step strings
    """
    incident_defaults = defaults.get("incident", {})
    next_steps_map = incident_defaults.get("next_steps", {})
    return next_steps_map.get(status, ["Continue investigation"])


def get_next_update_time(severity: str, defaults: dict[str, Any]) -> str:
    """Get default next update time based on severity.

    Args:
        severity: Incident severity (P1-P4)
        defaults: Loaded defaults configuration

    Returns:
        Next update time string
    """
    incident_defaults = defaults.get("incident", {})
    time_map = incident_defaults.get("next_update_time", {})
    return time_map.get(severity, "1 hour")


def get_evidence_checklist(has_evidence: bool, defaults: dict[str, Any]) -> list[str]:
    """Get evidence checklist when no evidence provided.

    Args:
        has_evidence: Whether evidence was provided
        defaults: Loaded defaults configuration

    Returns:
        List of evidence items to collect
    """
    if has_evidence:
        return []
    incident_defaults = defaults.get("incident", {})
    return incident_defaults.get("evidence_checklist", [
        "Screenshots of error messages/alerts",
        "Relevant log entries with timestamps",
        "Timeline of events",
    ])


def compose_incident_update(input_data: IncidentInput) -> dict[str, str]:
    """Compose incident update outputs for different audiences.

    Args:
        input_data: Validated incident input data

    Returns:
        Dictionary with 'manager' and 'client' formatted updates
    """
    defaults = load_defaults()

    # Merge input with defaults
    input_dict = asdict(input_data)
    incident_defaults = {
        "audience": defaults["incident"]["audience"],
        "severity": defaults["incident"]["severity"],
        "current_status": defaults["incident"]["current_status"],
    }
    merged = merge_with_defaults(input_dict, incident_defaults)

    # Auto-fill next update time if not provided
    if not merged.get("next_update_time"):
        merged["next_update_time"] = get_next_update_time(merged["severity"], defaults)

    # Auto-generate next steps
    next_steps = get_next_steps(merged["current_status"], defaults)

    # Get evidence or checklist
    has_evidence = bool(merged.get("evidence"))
    evidence_checklist = get_evidence_checklist(has_evidence, defaults)

    # Build context for template
    context = {
        "incident_title": merged["incident_title"],
        "impact_summary": merged["impact_summary"],
        "severity": merged["severity"],
        "current_status": merged["current_status"],
        "next_update_time": merged["next_update_time"],
        "checks_done": merged.get("checks_done", []),
        "checks_done_formatted": format_bullet_list(merged.get("checks_done", [])),
        "evidence": merged.get("evidence", []),
        "evidence_formatted": format_bullet_list(merged.get("evidence", [])),
        "evidence_checklist": evidence_checklist,
        "evidence_checklist_formatted": format_bullet_list(evidence_checklist),
        "next_steps": next_steps,
        "next_steps_formatted": format_numbered_list(next_steps),
        "timestamp": get_current_timestamp(),
        "has_evidence": has_evidence,
        "has_checks": bool(merged.get("checks_done")),
    }

    # Render templates for each audience
    result = {}

    # Manager update
    result["manager"] = render_template("incident_update_manager.md", context)

    # Client update
    result["client"] = render_template("incident_update_client.md", context)

    return result


def generate_incident_update(
    incident_title: str,
    impact_summary: str,
    audience: str = "manager",
    severity: str = "P2",
    current_status: str = "investigating",
    next_update_time: str | None = None,
    checks_done: list[str] | None = None,
    evidence: list[str] | None = None,
) -> str:
    """Generate an incident update from input parameters.

    This is the main entry point for the skill.

    Args:
        incident_title: Short title describing the incident (REQUIRED)
        impact_summary: Brief description of user/business impact (REQUIRED)
        audience: Target audience ('manager', 'client') - default: 'manager'
        severity: Incident severity (P1-P4) - default: 'P2'
        current_status: Current status - default: 'investigating'
        next_update_time: When next update will be provided (auto-filled if None)
        checks_done: List of diagnostic checks completed
        evidence: List of evidence collected

    Returns:
        Formatted incident update string for the specified audience
    """
    input_data = IncidentInput(
        incident_title=incident_title,
        impact_summary=impact_summary,
        audience=audience,
        severity=severity,
        current_status=current_status,
        next_update_time=next_update_time,
        checks_done=checks_done or [],
        evidence=evidence or [],
    )

    errors = input_data.validate()
    if errors:
        raise ValueError(f"Invalid input: {', '.join(errors)}")

    updates = compose_incident_update(input_data)
    return updates.get(audience, updates["manager"])


def generate_from_yaml(yaml_data: dict[str, Any]) -> str:
    """Generate incident update from YAML input data.

    Args:
        yaml_data: Dictionary loaded from YAML file

    Returns:
        Formatted incident update string
    """
    return generate_incident_update(
        incident_title=yaml_data.get("incident_title", ""),
        impact_summary=yaml_data.get("impact_summary", ""),
        audience=yaml_data.get("audience", "manager"),
        severity=yaml_data.get("severity", "P2"),
        current_status=yaml_data.get("current_status", "investigating"),
        next_update_time=yaml_data.get("next_update_time"),
        checks_done=yaml_data.get("checks_done", []),
        evidence=yaml_data.get("evidence", []),
    )
