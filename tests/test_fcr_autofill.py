"""Tests for FCR Autofill skill."""

import pytest

from netops_skills.skills.fcr_autofill import (
    FCRInput,
    generate_fcr_content,
    generate_from_yaml,
)


class TestFCRInput:
    """Tests for FCRInput schema."""

    def test_valid_input_passes(self):
        input_data = FCRInput(purpose="management access")
        assert input_data.validate() == []

    def test_missing_purpose_fails(self):
        input_data = FCRInput(purpose="")
        errors = input_data.validate()
        assert "purpose is required" in errors

    def test_defaults_applied(self):
        input_data = FCRInput(purpose="test")
        assert input_data.change_type == "firewall_rule"
        assert input_data.rule_count == "single"
        assert input_data.direction == "inbound"
        assert input_data.risk_level == "low"
        assert input_data.environment == "prod"


class TestGenerateFCRContent:
    """Tests for FCR content generation."""

    def test_generates_content(self):
        result = generate_fcr_content(purpose="management access")
        assert "FCR Content" in result
        assert "management access" in result

    def test_contains_required_sections(self):
        result = generate_fcr_content(purpose="test")
        assert "Technical Description" in result
        assert "Tests Conducted" in result
        assert "Rollback Options" in result
        assert "Impact Statement" in result
        assert "Ready-to-Go Checklist" in result
        assert "Evidence Checklist" in result

    def test_tests_never_na(self):
        result = generate_fcr_content(purpose="test")
        assert "N/A" not in result
        # Should have numbered tests
        assert "1." in result

    def test_rollback_never_na(self):
        result = generate_fcr_content(purpose="test")
        # Rollback should have steps
        assert "Rollback Options" in result
        rollback_idx = result.find("Rollback Options")
        impact_idx = result.find("Impact Statement")
        rollback_section = result[rollback_idx:impact_idx]
        assert "1." in rollback_section

    def test_raises_error_empty_purpose(self):
        with pytest.raises(ValueError) as exc:
            generate_fcr_content(purpose="")
        assert "purpose is required" in str(exc.value)

    def test_different_change_types(self):
        for ctype in ["firewall_rule", "nat_change", "f5_ssl", "routing_change"]:
            result = generate_fcr_content(purpose="test", change_type=ctype)
            assert ctype.replace("_", " ").title() in result

    def test_risk_levels_affect_impact(self):
        low = generate_fcr_content(purpose="test", risk_level="low")
        high = generate_fcr_content(purpose="test", risk_level="high")
        assert "LOW" in low
        assert "HIGH" in high
        assert "Minimal impact" in low
        assert "Significant impact" in high

    def test_deterministic_output(self):
        r1 = generate_fcr_content(purpose="test")
        r2 = generate_fcr_content(purpose="test")
        # Remove timestamp for comparison
        r1_lines = [l for l in r1.split("\n") if "Generated:" not in l]
        r2_lines = [l for l in r2.split("\n") if "Generated:" not in l]
        assert r1_lines == r2_lines


class TestGenerateFromYaml:
    """Tests for YAML input mode."""

    def test_generates_from_yaml(self):
        yaml_data = {"purpose": "management access"}
        result = generate_from_yaml(yaml_data)
        assert "management access" in result

    def test_yaml_respects_options(self):
        yaml_data = {
            "purpose": "test",
            "change_type": "nat_change",
            "risk_level": "high",
        }
        result = generate_from_yaml(yaml_data)
        assert "Nat Change" in result
        assert "HIGH" in result

    def test_yaml_defaults(self):
        yaml_data = {"purpose": "test"}
        result = generate_from_yaml(yaml_data)
        assert "PROD" in result
        assert "Firewall Rule" in result


class TestOutputQuality:
    """Tests for output quality requirements."""

    def test_has_evidence_checklist(self):
        result = generate_fcr_content(purpose="test")
        assert "Evidence Checklist" in result
        assert "[ ]" in result

    def test_has_checklist_justification(self):
        result = generate_fcr_content(purpose="test")
        assert "Ready-to-Go Checklist" in result
        assert "[x]" in result

    def test_rollback_time_present(self):
        result = generate_fcr_content(purpose="test")
        assert "Rollback Time" in result
