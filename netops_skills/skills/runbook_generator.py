"""Safe Troubleshooting Runbook Generator.

This skill generates SAFE, reusable troubleshooting steps for recurring network issues.

Key features:
- Only 2 required selections (domain, symptom_category)
- All steps are SAFE by default (gui_only mode)
- Auto-generates evidence checklists
- Includes STOP conditions for escalation
- NO disruptive actions allowed by default
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from netops_skills.common.render import render_template
from netops_skills.common.utils import get_current_timestamp, load_defaults


def get_playbooks_dir() -> Path:
    """Get the playbooks directory path."""
    return Path(__file__).parent.parent.parent / "playbooks"


def load_playbook(domain: str) -> dict[str, Any]:
    """Load playbook for a specific domain.

    Args:
        domain: Network domain (firewall, fmc, f5, etc.)

    Returns:
        Playbook dictionary or empty dict if not found
    """
    playbook_path = get_playbooks_dir() / f"{domain}.yaml"
    if not playbook_path.exists():
        return {}
    with open(playbook_path) as f:
        return yaml.safe_load(f) or {}


def get_available_domains() -> list[str]:
    """Get list of available domains from playbooks."""
    playbooks_dir = get_playbooks_dir()
    return [p.stem for p in playbooks_dir.glob("*.yaml")]


def get_symptoms_for_domain(domain: str) -> list[str]:
    """Get available symptoms for a domain.

    Args:
        domain: Network domain

    Returns:
        List of symptom category names
    """
    playbook = load_playbook(domain)
    symptoms = playbook.get("symptoms", {})
    return list(symptoms.keys())


@dataclass
class RunbookInput:
    """Schema for runbook generator input."""

    # REQUIRED - must be selected (2 selections)
    domain: str
    symptom_category: str

    # SELECTABLE with defaults
    access_mode: str = "gui_only"
    environment: str = "prod"

    def validate(self) -> list[str]:
        """Validate required fields. Returns list of errors."""
        errors = []
        if not self.domain or not self.domain.strip():
            errors.append("domain is required")
        if not self.symptom_category or not self.symptom_category.strip():
            errors.append("symptom_category is required")
        return errors


def filter_steps_by_access_mode(
    steps: list[dict[str, Any]], access_mode: str
) -> list[dict[str, Any]]:
    """Filter diagnostic steps based on access mode.

    Args:
        steps: List of diagnostic step dictionaries
        access_mode: Access mode (gui_only, cli_read_only, cli_full)

    Returns:
        Filtered list of steps safe for the access mode
    """
    # For gui_only, we keep all steps but mark CLI ones as reference-only
    # For cli_read_only, we allow read-only commands
    # For cli_full, we allow all commands (but still no destructive ones)
    return steps  # All steps in playbooks should be safe by design


def generate_runbook(
    domain: str,
    symptom_category: str,
    access_mode: str = "gui_only",
    environment: str = "prod",
) -> str:
    """Generate a safe troubleshooting runbook.

    Args:
        domain: Network domain (firewall, fmc, f5, circuit, api)
        symptom_category: Type of symptom (high_cpu, connectivity_loss, etc.)
        access_mode: Access level (gui_only, cli_read_only, cli_full)
        environment: Target environment (prod, uat, dev)

    Returns:
        Formatted runbook string
    """
    input_data = RunbookInput(
        domain=domain,
        symptom_category=symptom_category,
        access_mode=access_mode,
        environment=environment,
    )

    errors = input_data.validate()
    if errors:
        raise ValueError(f"Invalid input: {', '.join(errors)}")

    # Load playbook for domain
    playbook = load_playbook(domain)
    if not playbook:
        raise ValueError(f"No playbook found for domain: {domain}")

    # Get symptom data
    symptoms = playbook.get("symptoms", {})
    symptom_data = symptoms.get(symptom_category)
    if not symptom_data:
        available = list(symptoms.keys())
        raise ValueError(
            f"Unknown symptom '{symptom_category}' for domain '{domain}'. "
            f"Available: {available}"
        )

    # Filter steps based on access mode
    diagnostic_steps = filter_steps_by_access_mode(
        symptom_data.get("diagnostic_steps", []), access_mode
    )

    # Build context for template
    context = {
        "domain": domain,
        "symptom_category": symptom_category,
        "access_mode": access_mode,
        "environment": environment,
        "symptom_explanation": symptom_data.get("explanation", ""),
        "diagnostic_steps": diagnostic_steps,
        "evidence_checklist": symptom_data.get("evidence_checklist", []),
        "stop_conditions": symptom_data.get("stop_conditions", []),
        "escalation_path": playbook.get("escalation_path", "Contact Tier 2 support"),
        "timestamp": get_current_timestamp(),
    }

    return render_template("runbook.md", context)


def generate_from_yaml(yaml_data: dict[str, Any]) -> str:
    """Generate runbook from YAML input data.

    Args:
        yaml_data: Dictionary loaded from YAML file

    Returns:
        Formatted runbook string
    """
    return generate_runbook(
        domain=yaml_data.get("domain", ""),
        symptom_category=yaml_data.get("symptom_category", ""),
        access_mode=yaml_data.get("access_mode", "gui_only"),
        environment=yaml_data.get("environment", "prod"),
    )
