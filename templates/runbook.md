# Troubleshooting Runbook: {{ domain | title }} - {{ symptom_category | replace("_", " ") | title }}

| Setting | Value |
|---------|-------|
| Domain | {{ domain | title }} |
| Symptom | {{ symptom_category | replace("_", " ") | title }} |
| Access Mode | {{ access_mode | replace("_", " ") | title }} |
| Environment | {{ environment | upper }} |

## What This Symptom Usually Indicates
{{ symptom_explanation }}

## Safe Diagnostic Steps
{% for step in diagnostic_steps %}
### Step {{ loop.index }}: {{ step.title }}
**Action:** {{ step.action }}
{% if step.expected_output %}
**Expected:** {{ step.expected_output }}
{% endif %}
{% if step.warning %}
**Warning:** {{ step.warning }}
{% endif %}

{% endfor %}

## Evidence Checklist
{% for item in evidence_checklist %}
- [ ] {{ item }}
{% endfor %}

## STOP - Escalate Immediately If:
{% for condition in stop_conditions %}
- {{ condition }}
{% endfor %}

## Escalation Path
{{ escalation_path }}

---
Generated: {{ timestamp }} | Access: {{ access_mode }} - No disruptive commands included
