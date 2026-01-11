"""NetOps Skills CLI - Interactive command-line interface with minimal typing."""

import sys
from pathlib import Path

import click
import questionary
from questionary import Style

from netops_skills.common.utils import (
    get_options_for_field,
    load_defaults,
    load_yaml_input,
)
from netops_skills.skills.incident_update import (
    generate_from_yaml as generate_incident_from_yaml,
    generate_incident_update,
)
from netops_skills.skills.runbook_generator import (
    generate_from_yaml as generate_runbook_from_yaml,
    generate_runbook,
    get_available_domains,
    get_symptoms_for_domain,
)
from netops_skills.skills.fcr_autofill import (
    generate_from_yaml as generate_fcr_from_yaml,
    generate_fcr_content,
)

# Custom style for questionary prompts
custom_style = Style(
    [
        ("qmark", "fg:cyan bold"),
        ("question", "fg:white bold"),
        ("answer", "fg:green bold"),
        ("pointer", "fg:cyan bold"),
        ("highlighted", "fg:cyan bold"),
        ("selected", "fg:green"),
    ]
)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """NetOps Skills - Minimize typing for network operations tasks."""
    pass


# =============================================================================
# INCIDENT UPDATE COMPOSER
# =============================================================================


@main.command()
@click.argument("title", required=False)
@click.argument("impact", required=False)
@click.option(
    "--input",
    "-i",
    "input_file",
    type=click.Path(exists=True),
    help="YAML input file (skip interactive mode)",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(),
    help="Output file (default: stdout)",
)
@click.option(
    "-a", "--audience",
    type=click.Choice(["manager", "client", "internal", "executive"]),
    default="manager",
    help="Target audience (default: manager)",
)
@click.option(
    "-s", "--severity",
    type=click.Choice(["P1", "P2", "P3", "P4"]),
    default="P2",
    help="Incident severity (default: P2)",
)
@click.option(
    "--status",
    type=click.Choice(["investigating", "identified", "monitoring", "resolved", "escalated"]),
    default="investigating",
    help="Current status (default: investigating)",
)
@click.option(
    "--detailed", "-d",
    is_flag=True,
    help="Run detailed interactive mode (ask all questions)",
)
def incident(
    title: str | None,
    impact: str | None,
    input_file: str | None,
    output_file: str | None,
    audience: str,
    severity: str,
    status: str,
    detailed: bool,
):
    """Generate incident update from minimal input.

    \b
    QUICK MODE (2 args, all defaults):
      netops incident "VPN down" "Users cannot connect"

    \b
    WITH OPTIONS:
      netops incident "VPN down" "Users cannot connect" -s P1 -a client

    \b
    YAML MODE:
      netops incident -i examples/incident_p2.yaml

    \b
    DETAILED INTERACTIVE:
      netops incident -d
    """
    if input_file:
        # YAML file mode
        yaml_data = load_yaml_input(input_file)
        result = generate_incident_from_yaml(yaml_data)
    elif title and impact:
        # Quick mode - args provided, use defaults for rest
        result = generate_incident_update(
            incident_title=title,
            impact_summary=impact,
            audience=audience,
            severity=severity,
            current_status=status,
        )
    elif detailed or (not title and not impact):
        # Interactive mode
        result = run_incident_interactive(detailed=detailed)
    else:
        # Partial args - need both title and impact
        click.echo("Error: Both TITLE and IMPACT required for quick mode.", err=True)
        click.echo("Usage: netops incident \"title\" \"impact\"", err=True)
        sys.exit(1)

    # Output result
    if output_file:
        Path(output_file).write_text(result)
        click.echo(f"Output written to: {output_file}")
    else:
        click.echo("\n" + "=" * 80)
        click.echo(result)


def run_incident_interactive(detailed: bool = False) -> str:
    """Run interactive incident update composer.

    Args:
        detailed: If True, ask all optional questions. If False, only required + key selections.
    """
    defaults = load_defaults()

    click.echo("\n" + "=" * 60)
    click.echo("INCIDENT UPDATE COMPOSER")
    click.echo("=" * 60)
    if detailed:
        click.echo("Detailed mode: all options available\n")
    else:
        click.echo("Quick mode: 2 required fields + severity (use -d for all options)\n")

    # REQUIRED: incident_title (must type)
    incident_title = questionary.text(
        "Incident title:",
        style=custom_style,
    ).ask()

    if not incident_title:
        click.echo("Error: incident_title is required", err=True)
        sys.exit(1)

    # REQUIRED: impact_summary (must type)
    impact_summary = questionary.text(
        "Impact summary:",
        style=custom_style,
    ).ask()

    if not impact_summary:
        click.echo("Error: impact_summary is required", err=True)
        sys.exit(1)

    # QUICK: severity only (most commonly changed field)
    severity_options = get_options_for_field("incident", "severity", defaults)
    severity = questionary.select(
        "Severity:",
        choices=severity_options,
        default="P2",
        style=custom_style,
    ).ask()

    # Defaults for quick mode
    audience = "manager"
    current_status = "investigating"
    checks_done = []
    evidence = []

    # DETAILED mode: ask additional questions
    if detailed:
        audience_options = get_options_for_field("incident", "audience", defaults)
        audience = questionary.select(
            "Audience:",
            choices=audience_options,
            default="manager",
            style=custom_style,
        ).ask()

        status_options = get_options_for_field("incident", "current_status", defaults)
        current_status = questionary.select(
            "Current status:",
            choices=status_options,
            default="investigating",
            style=custom_style,
        ).ask()

        add_checks = questionary.confirm(
            "Add diagnostic checks done?",
            default=False,
            style=custom_style,
        ).ask()

        if add_checks:
            click.echo("Enter checks (empty line to finish):")
            while True:
                check = questionary.text("  - ", style=custom_style).ask()
                if not check:
                    break
                checks_done.append(check)

        add_evidence = questionary.confirm(
            "Add evidence collected?",
            default=False,
            style=custom_style,
        ).ask()

        if add_evidence:
            click.echo("Enter evidence items (empty line to finish):")
            while True:
                item = questionary.text("  - ", style=custom_style).ask()
                if not item:
                    break
                evidence.append(item)

    # Generate output
    return generate_incident_update(
        incident_title=incident_title,
        impact_summary=impact_summary,
        audience=audience,
        severity=severity,
        current_status=current_status,
        checks_done=checks_done,
        evidence=evidence,
    )


# =============================================================================
# RUNBOOK GENERATOR
# =============================================================================


@main.command()
@click.argument("domain", required=False)
@click.argument("symptom", required=False)
@click.option(
    "--input",
    "-i",
    "input_file",
    type=click.Path(exists=True),
    help="YAML input file (skip interactive mode)",
)
@click.option(
    "--output",
    "-o",
    "output_file",
    type=click.Path(),
    help="Output file (default: stdout)",
)
@click.option(
    "-m", "--mode",
    type=click.Choice(["gui_only", "cli_read_only", "cli_full"]),
    default="gui_only",
    help="Access mode (default: gui_only - safest)",
)
@click.option(
    "-e", "--env",
    type=click.Choice(["prod", "uat", "dev", "lab"]),
    default="prod",
    help="Target environment (default: prod)",
)
def runbook(
    domain: str | None,
    symptom: str | None,
    input_file: str | None,
    output_file: str | None,
    mode: str,
    env: str,
):
    """Generate safe troubleshooting runbook.

    \b
    QUICK MODE (2 args, all defaults):
      netops runbook firewall high_cpu

    \b
    WITH OPTIONS:
      netops runbook firewall high_cpu -m cli_read_only -e prod

    \b
    YAML MODE:
      netops runbook -i examples/runbook_high_cpu.yaml

    \b
    INTERACTIVE:
      netops runbook
    """
    if input_file:
        # YAML file mode
        yaml_data = load_yaml_input(input_file)
        result = generate_runbook_from_yaml(yaml_data)
    elif domain and symptom:
        # Quick mode - args provided
        result = generate_runbook(
            domain=domain,
            symptom_category=symptom,
            access_mode=mode,
            environment=env,
        )
    elif not domain and not symptom:
        # Interactive mode
        result = run_runbook_interactive()
    else:
        # Partial args
        click.echo("Error: Both DOMAIN and SYMPTOM required for quick mode.", err=True)
        click.echo("Usage: netops runbook firewall high_cpu", err=True)
        sys.exit(1)

    # Output result
    if output_file:
        Path(output_file).write_text(result)
        click.echo(f"Output written to: {output_file}")
    else:
        click.echo("\n" + "=" * 80)
        click.echo(result)


def run_runbook_interactive() -> str:
    """Run interactive runbook generator."""
    click.echo("\n" + "=" * 60)
    click.echo("SAFE TROUBLESHOOTING RUNBOOK GENERATOR")
    click.echo("=" * 60)
    click.echo("Required: 2 selections | All steps are SAFE by default\n")

    # Get available domains
    domains = get_available_domains()
    if not domains:
        click.echo("Error: No playbooks found", err=True)
        sys.exit(1)

    # REQUIRED: domain selection
    domain = questionary.select(
        "Domain:",
        choices=domains,
        style=custom_style,
    ).ask()

    if not domain:
        click.echo("Error: domain is required", err=True)
        sys.exit(1)

    # Get symptoms for selected domain
    symptoms = get_symptoms_for_domain(domain)
    if not symptoms:
        click.echo(f"Error: No symptoms defined for domain '{domain}'", err=True)
        sys.exit(1)

    # REQUIRED: symptom selection
    symptom = questionary.select(
        "Symptom category:",
        choices=symptoms,
        style=custom_style,
    ).ask()

    if not symptom:
        click.echo("Error: symptom_category is required", err=True)
        sys.exit(1)

    # Generate with defaults (gui_only, prod)
    return generate_runbook(
        domain=domain,
        symptom_category=symptom,
        access_mode="gui_only",
        environment="prod",
    )


# =============================================================================
# FCR AUTOFILL
# =============================================================================


@main.command()
@click.argument("purpose", required=False)
@click.option(
    "--input", "-i", "input_file",
    type=click.Path(exists=True),
    help="YAML input file",
)
@click.option(
    "--output", "-o", "output_file",
    type=click.Path(),
    help="Output file (default: stdout)",
)
@click.option(
    "-t", "--type",
    "change_type",
    type=click.Choice(["firewall_rule", "nat_change", "f5_ssl", "routing_change", "acl_update", "vpn_config"]),
    default="firewall_rule",
    help="Change type (default: firewall_rule)",
)
@click.option(
    "-r", "--risk",
    type=click.Choice(["low", "medium", "high"]),
    default="low",
    help="Risk level (default: low)",
)
@click.option(
    "-d", "--direction",
    type=click.Choice(["inbound", "outbound", "bidirectional"]),
    default="inbound",
    help="Direction (default: inbound)",
)
def fcr(
    purpose: str | None,
    input_file: str | None,
    output_file: str | None,
    change_type: str,
    risk: str,
    direction: str,
):
    """Generate FCR section content for GNOC.

    \b
    QUICK MODE (1 arg, all defaults):
      netops fcr "management access"

    \b
    WITH OPTIONS:
      netops fcr "management access" -t firewall_rule -r low

    \b
    YAML MODE:
      netops fcr -i examples/fcr_firewall.yaml
    """
    if input_file:
        yaml_data = load_yaml_input(input_file)
        result = generate_fcr_from_yaml(yaml_data)
    elif purpose:
        result = generate_fcr_content(
            purpose=purpose,
            change_type=change_type,
            direction=direction,
            risk_level=risk,
        )
    else:
        # Interactive - just ask purpose
        click.echo("\n" + "=" * 60)
        click.echo("FCR SECTION AUTOFILL")
        click.echo("=" * 60)
        click.echo("Required: 1 field | Everything else defaults\n")

        purpose = questionary.text("Purpose:", style=custom_style).ask()
        if not purpose:
            click.echo("Error: purpose is required", err=True)
            sys.exit(1)

        result = generate_fcr_content(purpose=purpose)

    if output_file:
        Path(output_file).write_text(result)
        click.echo(f"Output written to: {output_file}")
    else:
        click.echo("\n" + "=" * 80)
        click.echo(result)


if __name__ == "__main__":
    main()
