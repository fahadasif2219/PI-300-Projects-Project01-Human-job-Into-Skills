# NetOps Skills

Network Operations Skills toolkit that converts repetitive NOC tasks into minimal-typing, reusable skills.

## Problem This Skill Solves

- Senior network engineers repeatedly write troubleshooting runbooks during incidents from memory
- High cognitive load under time pressure leads to missed steps and inconsistent documentation
- Junior engineers lack access to tribal knowledge encoded in experienced heads
- Manual runbook creation takes 20-30 minutes per incident, delaying resolution

## Primary Skill: Automated Runbook Generator

The Runbook Generator converts expert troubleshooting knowledge into structured, safe runbooks with minimal input.

**Inputs:**
- Device type (firewall, f5, switch, router)
- Problem category (high_cpu, certificate_error, etc.)
- Optional: execution mode (cli_read_only, gui, etc.)

**Outputs:**
- Step-by-step safe commands (no disruptive operations)
- STOP conditions to prevent escalation
- Evidence collection checklist
- Escalation path with contact info

**Time saved:** 20-30 minutes per incident

## Demo

[Watch 90-second demo](https://www.loom.com/share/0df406e44a8c420db5211cf8c7f0e77e) — Real incident simulation showing runbook generation from 2 selections.

## Skills Summary

| Skill | Replaces | Typing Required | Time Saved |
|-------|----------|-----------------|------------|
| Incident Update Composer | Manual email/ticket drafting | 2 lines + selections | 10-15 min/update |
| Runbook Generator | Writing troubleshooting steps from scratch | 2 selections | 20-30 min/runbook |
| FCR Autofill | Filling FCR sections manually | 1 line + selections | 15-20 min/FCR |

## Quick CLI Examples

```bash
# Skill 1: Incident Update (2 args)
netops incident "VPN down" "Users cannot connect"
netops incident "VPN down" "Users cannot connect" -s P1 -a client

# Skill 2: Runbook Generator (2 args)
netops runbook firewall high_cpu
netops runbook f5 certificate_error -m cli_read_only

# Skill 3: FCR Autofill (1 arg)
netops fcr "management access"
netops fcr "management access" -t nat_change -r medium
```

## Installation

```bash
cd Project-01-Human-Job-Into-Skills
pip install -e ".[dev]"
```

## Usage

### Interactive Mode (Recommended for Daily Work)

```bash
# Run incident update composer interactively
netops incident

# Run runbook generator interactively
netops runbook

# Run FCR autofill interactively
netops fcr
```

### YAML File Mode (For Reuse/Testing)

```bash
# Generate incident update from YAML
netops incident --input examples/incident_p2.yaml

# Generate runbook from YAML
netops runbook --input examples/runbook_high_cpu.yaml

# Generate FCR content from YAML
netops fcr --input examples/fcr_firewall.yaml
```

## Example Input/Output

### Incident Update Composer

**Input (2 typed lines + selections):**
```yaml
incident_title: VPN authentication intermittent
impact_summary: Users experiencing login failures
# Everything else is selectable or defaulted
```

**Output:**
```
Subject: [P2] VPN authentication intermittent - Manager Update

EXECUTIVE SUMMARY
-----------------
Impact: Users experiencing login failures
Status: Investigating
Severity: P2

DETAILED UPDATE
---------------
...
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
netops_skills/
├── cli.py              # Interactive CLI with minimal typing
├── config/
│   ├── defaults.yaml   # Default values for all skills
│   └── profiles.yaml   # Reusable engineer/team profiles
├── common/
│   ├── schema.py       # Input validation schemas
│   ├── render.py       # Template rendering
│   └── utils.py        # Shared utilities
└── skills/
    ├── incident_update.py
    ├── runbook_generator.py
    └── fcr_autofill.py
```

## Design Principles

1. **Minimal Typing**: Maximum 2-3 required typed fields per skill
2. **Smart Defaults**: Everything has sensible defaults
3. **Selection Over Typing**: Use menus/enums wherever possible
4. **Profile Reuse**: Save common settings in profiles
5. **Deterministic Output**: Same input always produces same output
