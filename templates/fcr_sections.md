# FCR Content: {{ change_type | replace("_", " ") | title }}

| Field | Value |
|-------|-------|
| Purpose | {{ purpose }} |
| Change Type | {{ change_type | replace("_", " ") | title }} |
| Rule Count | {{ rule_count | title }} |
| Direction | {{ direction | title }} |
| Risk Level | {{ risk_level | upper }} |
| Environment | {{ environment | upper }} |

## Section 4: Technical Description
{{ technical_description }}

## Tests Conducted
{% for test in tests_conducted %}
{{ loop.index }}. {{ test }}
{% endfor %}

## Rollback Options
{% for option in rollback_options %}
{{ loop.index }}. {{ option }}
{% endfor %}

**Rollback Time Estimate:** {{ rollback_time }}

## Impact Statement
{{ impact_statement }}

**Affected Systems:**
{% for system in affected_systems %}
- {{ system }}
{% endfor %}

## Ready-to-Go Checklist Justification
{% for item in checklist_justification %}
- [x] {{ item }}
{% endfor %}

## Evidence Checklist
{% for item in evidence_checklist %}
- [ ] {{ item }}
{% endfor %}

---
Generated: {{ timestamp }} | For use in official FCR Word document
