"""Shared utilities for NetOps Skills."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def get_config_dir() -> Path:
    """Get the config directory path."""
    return Path(__file__).parent.parent / "config"


def load_defaults() -> dict[str, Any]:
    """Load defaults from defaults.yaml."""
    defaults_path = get_config_dir() / "defaults.yaml"
    with open(defaults_path) as f:
        return yaml.safe_load(f)


def load_profiles() -> dict[str, Any]:
    """Load profiles from profiles.yaml."""
    profiles_path = get_config_dir() / "profiles.yaml"
    with open(profiles_path) as f:
        return yaml.safe_load(f)


def load_yaml_input(file_path: str | Path) -> dict[str, Any]:
    """Load input from a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary of input values
    """
    with open(file_path) as f:
        return yaml.safe_load(f) or {}


def merge_with_defaults(
    user_input: dict[str, Any], defaults: dict[str, Any]
) -> dict[str, Any]:
    """Merge user input with defaults, user input takes precedence.

    Args:
        user_input: User-provided values
        defaults: Default values

    Returns:
        Merged dictionary
    """
    result = defaults.copy()
    for key, value in user_input.items():
        if value is not None and value != "":
            result[key] = value
    return result


def get_current_timestamp() -> str:
    """Get current timestamp in standard format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def get_options_for_field(
    skill: str, field_name: str, defaults: dict[str, Any] | None = None
) -> list[str]:
    """Get selectable options for a field.

    Args:
        skill: Skill name ('incident', 'runbook', 'fcr')
        field_name: Name of the field
        defaults: Pre-loaded defaults (optional)

    Returns:
        List of options for the field
    """
    if defaults is None:
        defaults = load_defaults()

    skill_defaults = defaults.get(skill, {})
    options = skill_defaults.get("options", {})
    return options.get(field_name, [])


def get_default_value(
    skill: str, field_name: str, defaults: dict[str, Any] | None = None
) -> Any:
    """Get default value for a field.

    Args:
        skill: Skill name ('incident', 'runbook', 'fcr')
        field_name: Name of the field
        defaults: Pre-loaded defaults (optional)

    Returns:
        Default value for the field
    """
    if defaults is None:
        defaults = load_defaults()

    skill_defaults = defaults.get(skill, {})
    return skill_defaults.get(field_name)
