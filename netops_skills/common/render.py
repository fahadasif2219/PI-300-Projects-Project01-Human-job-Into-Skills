"""Template rendering utilities for NetOps Skills."""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


def get_template_env() -> Environment:
    """Get Jinja2 environment configured for templates directory."""
    templates_dir = Path(__file__).parent.parent.parent / "templates"
    return Environment(
        loader=FileSystemLoader(templates_dir),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render a template with the given context.

    Args:
        template_name: Name of the template file (e.g., 'incident_update_manager.md')
        context: Dictionary of variables to pass to the template

    Returns:
        Rendered template string
    """
    env = get_template_env()
    template = env.get_template(template_name)
    return template.render(**context)


def format_bullet_list(items: list[str], indent: int = 0) -> str:
    """Format a list of items as markdown bullets.

    Args:
        items: List of strings to format
        indent: Number of spaces to indent

    Returns:
        Formatted bullet list string
    """
    if not items:
        return ""
    prefix = " " * indent
    return "\n".join(f"{prefix}- {item}" for item in items)


def format_numbered_list(items: list[str], start: int = 1) -> str:
    """Format a list of items as numbered list.

    Args:
        items: List of strings to format
        start: Starting number

    Returns:
        Formatted numbered list string
    """
    if not items:
        return ""
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=start))


def format_section_header(title: str, level: int = 2) -> str:
    """Format a section header.

    Args:
        title: Header title
        level: Header level (1-6)

    Returns:
        Formatted header string
    """
    return f"{'#' * level} {title}"
