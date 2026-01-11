"""Input validation schemas for NetOps Skills."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IncidentInput:
    """Schema for incident update input."""

    # REQUIRED - must be typed (2 fields max)
    incident_title: str
    impact_summary: str

    # SELECTABLE with defaults
    audience: str = "manager"
    severity: str = "P2"
    current_status: str = "investigating"

    # OPTIONAL
    next_update_time: Optional[str] = None
    checks_done: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        """Validate required fields. Returns list of errors."""
        errors = []
        if not self.incident_title or not self.incident_title.strip():
            errors.append("incident_title is required")
        if not self.impact_summary or not self.impact_summary.strip():
            errors.append("impact_summary is required")
        return errors


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


@dataclass
class FCRInput:
    """Schema for FCR autofill input."""

    # REQUIRED - must be typed (1 field)
    purpose: str

    # SELECTABLE with defaults
    change_type: str = "firewall_rule"
    rule_count: str = "single"
    direction: str = "inbound"
    risk_level: str = "low"
    environment: str = "prod"

    def validate(self) -> list[str]:
        """Validate required fields. Returns list of errors."""
        errors = []
        if not self.purpose or not self.purpose.strip():
            errors.append("purpose is required")
        return errors
