# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Network Operations Skills (netops-skills) - A toolkit to minimize repetitive typing for NOC tasks by converting human job workflows into reusable skills.

## Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
PYTHONPATH=. pytest -q

# Run CLI
netops --help
```

## Architecture

```
netops_skills/
├── cli.py              # Click-based CLI entry point
├── common/
│   ├── schema.py       # Dataclass schemas (IncidentInput, etc.)
│   ├── render.py       # Jinja2 template rendering
│   └── utils.py        # YAML loading, defaults
├── config/
│   ├── defaults.yaml   # Default values for all skills
│   └── profiles.yaml   # User profiles/presets
└── skills/
    ├── fcr_autofill.py       # First Call Resolution autofill
    ├── incident_update.py    # Incident status updates (manager/client)
    └── runbook_generator.py  # Runbook generation from playbooks
```

## Key Patterns

- **Skills** accept validated input schemas and return rendered markdown
- **Templates** in `templates/` use Jinja2 with conditional sections
- **Playbooks** in `playbooks/` define diagnostic workflows per technology (firewall, API, F5, etc.)
- **Examples** in `examples/` provide YAML input samples for each skill
