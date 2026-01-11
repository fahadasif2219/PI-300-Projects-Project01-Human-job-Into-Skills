# Project Context – NetOps Skills Toolkit

## Project Goal
Build CLI-based skills for network engineers that:
- Are safe by default (no disruptive commands)
- Require minimal typing
- Use smart defaults
- Produce real operational outputs

## Implemented Skills

### Skill 1 – Incident Update
Command:
- netops incident "title" "impact"
- netops incident -i examples/incident_p2.yaml

Features:
- Minimal prompts
- Smart defaults (severity, status, audience)
- Manager and Client outputs
- Evidence checklist auto-generated

### Skill 2 – Runbook Generator
Command:
- netops runbook firewall high_cpu
- netops runbook fs certificate_error

Features:
- Safe steps only
- STOP conditions
- Escalation path
- Evidence checklist

### Skill 3 – FCR Autofill
Command:
- netops fcr "management access"
- netops fcr "management access" -t nat_change -r medium

Features:
- Autofills technical description, tests, rollback, impact
- Ready-to-go checklist
- Evidence checklist

## Design Rules
- No redesign unless broken
- Minimal prompts
- Heavy defaults
- Safe by default
- Token-efficient instructions
- Follow patterns from existing skills

## Folder Structure
- netops_skills/
- skills/: incident_update.py, runbook_generator.py, fcr_autofill.py
- playbooks/
- examples/
- tests/
- README.md

## Current Status
- 3 skills complete
- ~70 tests passing
- README has quick CLI examples
- Repo already published