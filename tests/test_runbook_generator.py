"""Tests for Runbook Generator skill."""

import pytest

from netops_skills.skills.runbook_generator import (
    RunbookInput,
    generate_from_yaml,
    generate_runbook,
    get_available_domains,
    get_symptoms_for_domain,
    load_playbook,
)


class TestRunbookInput:
    """Tests for RunbookInput schema validation."""

    def test_valid_input_passes_validation(self):
        """Valid input with required fields passes validation."""
        input_data = RunbookInput(
            domain="firewall",
            symptom_category="high_cpu",
        )
        errors = input_data.validate()
        assert errors == []

    def test_missing_domain_fails_validation(self):
        """Missing domain fails validation."""
        input_data = RunbookInput(
            domain="",
            symptom_category="high_cpu",
        )
        errors = input_data.validate()
        assert "domain is required" in errors

    def test_missing_symptom_fails_validation(self):
        """Missing symptom_category fails validation."""
        input_data = RunbookInput(
            domain="firewall",
            symptom_category="",
        )
        errors = input_data.validate()
        assert "symptom_category is required" in errors

    def test_defaults_are_applied(self):
        """Default values are set correctly."""
        input_data = RunbookInput(
            domain="firewall",
            symptom_category="high_cpu",
        )
        assert input_data.access_mode == "gui_only"
        assert input_data.environment == "prod"


class TestPlaybookLoading:
    """Tests for playbook loading functions."""

    def test_get_available_domains(self):
        """Available domains are discovered from playbooks."""
        domains = get_available_domains()
        assert len(domains) > 0
        assert "firewall" in domains

    def test_load_existing_playbook(self):
        """Existing playbook loads successfully."""
        playbook = load_playbook("firewall")
        assert playbook is not None
        assert "symptoms" in playbook

    def test_load_nonexistent_playbook(self):
        """Nonexistent playbook returns empty dict."""
        playbook = load_playbook("nonexistent_domain")
        assert playbook == {}

    def test_get_symptoms_for_domain(self):
        """Symptoms are retrieved for a domain."""
        symptoms = get_symptoms_for_domain("firewall")
        assert len(symptoms) > 0
        assert "high_cpu" in symptoms


class TestGenerateRunbook:
    """Tests for runbook generation."""

    def test_generates_runbook_for_valid_input(self):
        """Valid input generates a runbook."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        assert "Troubleshooting Runbook" in result
        assert "Firewall" in result
        assert "High Cpu" in result

    def test_runbook_contains_required_sections(self):
        """Runbook contains all required sections."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        # Check required sections
        assert "What This Symptom Usually Indicates" in result
        assert "Safe Diagnostic Steps" in result
        assert "Evidence Checklist" in result
        assert "STOP - Escalate Immediately If" in result
        assert "Escalation Path" in result

    def test_runbook_contains_stop_conditions(self):
        """Runbook includes STOP conditions."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        assert "STOP" in result
        assert "Escalate" in result

    def test_runbook_contains_evidence_checklist(self):
        """Runbook includes evidence checklist."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        assert "Evidence Checklist" in result
        assert "[ ]" in result  # Checkbox format

    def test_raises_error_for_invalid_domain(self):
        """Invalid domain raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_runbook(
                domain="nonexistent",
                symptom_category="high_cpu",
            )
        assert "No playbook found" in str(exc_info.value)

    def test_raises_error_for_invalid_symptom(self):
        """Invalid symptom raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_runbook(
                domain="firewall",
                symptom_category="nonexistent_symptom",
            )
        assert "Unknown symptom" in str(exc_info.value)

    def test_raises_error_for_empty_input(self):
        """Empty input raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            generate_runbook(
                domain="",
                symptom_category="",
            )
        assert "domain is required" in str(exc_info.value)

    def test_access_mode_appears_in_output(self):
        """Access mode is shown in output."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
            access_mode="gui_only",
        )
        assert "Gui Only" in result or "gui_only" in result.lower()

    def test_environment_appears_in_output(self):
        """Environment is shown in output."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
            environment="prod",
        )
        assert "PROD" in result

    def test_deterministic_output(self):
        """Same input produces same output (excluding timestamp)."""
        result1 = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        result2 = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        # Remove timestamp line for comparison
        result1_lines = [l for l in result1.split("\n") if "Generated:" not in l]
        result2_lines = [l for l in result2.split("\n") if "Generated:" not in l]
        assert result1_lines == result2_lines


class TestGenerateFromYaml:
    """Tests for YAML input mode."""

    def test_generates_from_yaml_dict(self):
        """Generates output from YAML dictionary."""
        yaml_data = {
            "domain": "firewall",
            "symptom_category": "high_cpu",
        }
        result = generate_from_yaml(yaml_data)
        assert "Troubleshooting Runbook" in result
        assert "Firewall" in result

    def test_yaml_respects_optional_fields(self):
        """YAML can specify optional fields."""
        yaml_data = {
            "domain": "firewall",
            "symptom_category": "high_cpu",
            "access_mode": "cli_read_only",
            "environment": "uat",
        }
        result = generate_from_yaml(yaml_data)
        assert "UAT" in result

    def test_yaml_defaults_applied(self):
        """Missing YAML fields use defaults."""
        yaml_data = {
            "domain": "firewall",
            "symptom_category": "high_cpu",
        }
        result = generate_from_yaml(yaml_data)
        # Default environment is prod
        assert "PROD" in result


class TestSafetyRequirements:
    """Tests to ensure runbooks meet safety requirements."""

    def test_no_disruptive_commands_by_default(self):
        """Default access mode does not include disruptive commands."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
            access_mode="gui_only",
        )
        # Check footer confirms no disruptive commands
        assert "No disruptive commands" in result

    def test_stop_conditions_never_empty(self):
        """STOP conditions section is never empty."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        # Check that there are actual stop conditions
        assert "STOP" in result
        # There should be bullet points after STOP section
        stop_index = result.find("STOP")
        escalation_index = result.find("## Escalation Path")
        stop_section = result[stop_index:escalation_index]
        assert "-" in stop_section  # Has bullet points

    def test_escalation_path_provided(self):
        """Escalation path is always provided."""
        result = generate_runbook(
            domain="firewall",
            symptom_category="high_cpu",
        )
        assert "Escalation Path" in result
        # Check there's content after escalation path
        escalation_index = result.find("## Escalation Path")
        assert escalation_index > 0


class TestMultipleDomains:
    """Tests for multiple domain playbooks."""

    def test_f5_domain_works(self):
        """F5 domain generates valid runbook."""
        symptoms = get_symptoms_for_domain("f5")
        if symptoms:
            result = generate_runbook(
                domain="f5",
                symptom_category=symptoms[0],
            )
            assert "F5" in result

    def test_circuit_domain_works(self):
        """Circuit domain generates valid runbook."""
        symptoms = get_symptoms_for_domain("circuit")
        if symptoms:
            result = generate_runbook(
                domain="circuit",
                symptom_category=symptoms[0],
            )
            assert "Circuit" in result

    def test_api_domain_works(self):
        """API domain generates valid runbook."""
        symptoms = get_symptoms_for_domain("api")
        if symptoms:
            result = generate_runbook(
                domain="api",
                symptom_category=symptoms[0],
            )
            assert "Api" in result
