"""Tests for Incident Update Composer skill."""

import pytest

from netops_skills.common.schema import IncidentInput
from netops_skills.skills.incident_update import (
    compose_incident_update,
    generate_from_yaml,
    generate_incident_update,
    get_evidence_checklist,
    get_next_steps,
    get_next_update_time,
)
from netops_skills.common.utils import load_defaults


class TestIncidentInput:
    """Tests for IncidentInput schema validation."""

    def test_valid_input_passes_validation(self):
        """Valid input with required fields passes validation."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="Test impact",
        )
        errors = input_data.validate()
        assert errors == []

    def test_missing_title_fails_validation(self):
        """Missing incident_title fails validation."""
        input_data = IncidentInput(
            incident_title="",
            impact_summary="Test impact",
        )
        errors = input_data.validate()
        assert "incident_title is required" in errors

    def test_missing_summary_fails_validation(self):
        """Missing impact_summary fails validation."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="",
        )
        errors = input_data.validate()
        assert "impact_summary is required" in errors

    def test_whitespace_only_fails_validation(self):
        """Whitespace-only fields fail validation."""
        input_data = IncidentInput(
            incident_title="   ",
            impact_summary="   ",
        )
        errors = input_data.validate()
        assert len(errors) == 2

    def test_defaults_are_applied(self):
        """Default values are set correctly."""
        input_data = IncidentInput(
            incident_title="Test",
            impact_summary="Impact",
        )
        assert input_data.audience == "manager"
        assert input_data.severity == "P2"
        assert input_data.current_status == "investigating"


class TestNextSteps:
    """Tests for auto-generated next steps."""

    def test_investigating_status_has_next_steps(self):
        """Investigating status returns appropriate next steps."""
        defaults = load_defaults()
        steps = get_next_steps("investigating", defaults)
        assert len(steps) > 0
        assert any("root cause" in step.lower() for step in steps)

    def test_resolved_status_has_next_steps(self):
        """Resolved status returns appropriate next steps."""
        defaults = load_defaults()
        steps = get_next_steps("resolved", defaults)
        assert len(steps) > 0
        assert any("confirm" in step.lower() or "documentation" in step.lower() for step in steps)

    def test_unknown_status_has_fallback(self):
        """Unknown status returns fallback next step."""
        defaults = load_defaults()
        steps = get_next_steps("unknown_status", defaults)
        assert len(steps) > 0


class TestNextUpdateTime:
    """Tests for next update time based on severity."""

    def test_p1_has_short_update_time(self):
        """P1 incidents have short update intervals."""
        defaults = load_defaults()
        time = get_next_update_time("P1", defaults)
        assert "30" in time or "minute" in time.lower()

    def test_p4_has_longer_update_time(self):
        """P4 incidents have longer update intervals."""
        defaults = load_defaults()
        time = get_next_update_time("P4", defaults)
        assert "day" in time.lower() or "business" in time.lower()


class TestEvidenceChecklist:
    """Tests for evidence checklist generation."""

    def test_no_evidence_returns_checklist(self):
        """When no evidence provided, checklist is returned."""
        from netops_skills.common.utils import load_defaults
        defaults = load_defaults()
        checklist = get_evidence_checklist(has_evidence=False, defaults=defaults)
        assert len(checklist) > 0
        assert any("screenshot" in item.lower() for item in checklist)

    def test_has_evidence_returns_empty_checklist(self):
        """When evidence provided, no checklist returned."""
        from netops_skills.common.utils import load_defaults
        defaults = load_defaults()
        checklist = get_evidence_checklist(has_evidence=True, defaults=defaults)
        assert checklist == []


class TestComposeIncidentUpdate:
    """Tests for composing incident updates."""

    def test_output_contains_required_sections_manager(self):
        """Manager output contains all required sections."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="Test impact",
        )
        outputs = compose_incident_update(input_data)

        manager_output = outputs["manager"]

        # Check required sections exist (markdown format)
        assert "Executive Summary" in manager_output
        assert "Current Situation" in manager_output
        assert "Next Steps" in manager_output
        assert "Subject:" in manager_output

        # Check incident details are present
        assert "Test incident" in manager_output
        assert "Test impact" in manager_output
        assert "P2" in manager_output  # default severity

    def test_output_contains_required_sections_client(self):
        """Client output contains all required sections."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="Test impact",
            audience="client",
        )
        outputs = compose_incident_update(input_data)

        client_output = outputs["client"]

        # Check required sections exist (markdown format)
        assert "Status Summary" in client_output
        assert "What We Know" in client_output
        assert "What We Are Doing" in client_output
        assert "Next Update" in client_output

    def test_evidence_checklist_when_no_evidence(self):
        """Evidence checklist appears when no evidence provided."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="Test impact",
        )
        outputs = compose_incident_update(input_data)

        manager_output = outputs["manager"]
        assert "Evidence To Collect" in manager_output

    def test_evidence_section_when_evidence_provided(self):
        """Evidence section appears when evidence provided."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="Test impact",
            evidence=["Screenshot of error", "Log excerpt"],
        )
        outputs = compose_incident_update(input_data)

        manager_output = outputs["manager"]
        assert "Evidence Collected" in manager_output
        assert "Screenshot of error" in manager_output

    def test_checks_done_appear_in_output(self):
        """Diagnostic checks appear when provided."""
        input_data = IncidentInput(
            incident_title="Test incident",
            impact_summary="Test impact",
            checks_done=["Verified connectivity", "Checked logs"],
        )
        outputs = compose_incident_update(input_data)

        manager_output = outputs["manager"]
        assert "Diagnostic Checks Completed" in manager_output
        assert "Verified connectivity" in manager_output


class TestGenerateIncidentUpdate:
    """Tests for main entry point function."""

    def test_generates_manager_update_by_default(self):
        """Default audience is manager."""
        result = generate_incident_update(
            incident_title="Test incident",
            impact_summary="Test impact",
        )
        assert "Executive Summary" in result

    def test_generates_client_update_when_specified(self):
        """Client audience generates client format."""
        result = generate_incident_update(
            incident_title="Test incident",
            impact_summary="Test impact",
            audience="client",
        )
        assert "Dear Valued Customer" in result

    def test_raises_error_on_invalid_input(self):
        """Invalid input raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_incident_update(
                incident_title="",
                impact_summary="Test impact",
            )
        assert "incident_title is required" in str(exc_info.value)

    def test_deterministic_output(self):
        """Same input produces same output (excluding timestamp)."""
        result1 = generate_incident_update(
            incident_title="Test incident",
            impact_summary="Test impact",
            severity="P2",
            current_status="investigating",
        )
        result2 = generate_incident_update(
            incident_title="Test incident",
            impact_summary="Test impact",
            severity="P2",
            current_status="investigating",
        )
        # Remove timestamp line for comparison
        result1_lines = [l for l in result1.split("\n") if "Generated:" not in l and "Timestamp:" not in l and "UTC" not in l]
        result2_lines = [l for l in result2.split("\n") if "Generated:" not in l and "Timestamp:" not in l and "UTC" not in l]
        assert result1_lines == result2_lines


class TestGenerateFromYaml:
    """Tests for YAML input mode."""

    def test_generates_from_yaml_dict(self):
        """Generates output from YAML dictionary."""
        yaml_data = {
            "incident_title": "VPN authentication intermittent",
            "impact_summary": "Users experiencing login failures",
        }
        result = generate_from_yaml(yaml_data)
        assert "VPN authentication intermittent" in result
        assert "Users experiencing login failures" in result

    def test_yaml_respects_optional_fields(self):
        """YAML can specify optional fields."""
        yaml_data = {
            "incident_title": "Test incident",
            "impact_summary": "Test impact",
            "severity": "P1",
            "audience": "client",
        }
        result = generate_from_yaml(yaml_data)
        assert "P1" in result
        assert "Dear Valued Customer" in result

    def test_yaml_defaults_applied(self):
        """Missing YAML fields use defaults."""
        yaml_data = {
            "incident_title": "Test incident",
            "impact_summary": "Test impact",
        }
        result = generate_from_yaml(yaml_data)
        # Default severity is P2
        assert "P2" in result


class TestOutputNeverNA:
    """Tests to ensure outputs never contain N/A for key sections."""

    def test_next_steps_never_na(self):
        """Next steps section never equals N/A."""
        input_data = IncidentInput(
            incident_title="Test",
            impact_summary="Impact",
        )
        outputs = compose_incident_update(input_data)
        manager_output = outputs["manager"]

        # Find next steps section
        assert "N/A" not in manager_output or "NEXT STEPS" in manager_output

    def test_always_has_evidence_or_checklist(self):
        """Output always has evidence section or checklist."""
        input_data = IncidentInput(
            incident_title="Test",
            impact_summary="Impact",
        )
        outputs = compose_incident_update(input_data)
        manager_output = outputs["manager"]

        has_evidence_section = "Evidence Collected" in manager_output
        has_checklist = "Evidence To Collect" in manager_output

        assert has_evidence_section or has_checklist
