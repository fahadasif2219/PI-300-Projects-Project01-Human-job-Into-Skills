# INCIDENT STATUS UPDATE

## Management Snapshot
- **Incident Title:** {{ incident_title }}
- **Severity:** {{ severity }}
- **Business Impact:** {{ impact_summary }}
- **Current Risk Level:** {{ risk_level | default("Medium") }}
- **Incident Owner:** Network Operations
- **Mitigation in Progress:** Yes
- **Next Update:** {{ next_update_time }}

---

## Executive Summary
Network Operations is actively managing an incident impacting {{ impacted_scope | default("affected users/services") }}.
Initial analysis confirms the issue is **under investigation**, with no immediate indication of security breach or configuration error.
Services remain impacted while diagnostics continue.

---

## Current Situation
- Incident identified and acknowledged by Network Operations.
- Initial health checks completed across relevant network components.
- No blocking firewall or policy changes detected at this stage.
- Focus has shifted to upstream connectivity and dependent services.

---

## Actions Completed
{% for check in checks_done %}
- {{ check }}
{% endfor %}
{% if not checks_done %}
- Initial connectivity and monitoring checks completed
- Incident scoped and ownership established
{% endif %}

---

## Evidence Available / To Be Collected
{% for item in evidence %}
- {{ item }}
{% endfor %}
{% if not evidence %}
- Monitoring alerts and timestamps
- Firewall and VPN session statistics
- Interface and tunnel health indicators
- Authentication or upstream service logs
{% endif %}

---

## Next Steps (In Progress)
{% for step in next_steps %}
- {{ step }}
{% endfor %}
{% if not next_steps %}
1. Continue root cause analysis across dependent services
2. Validate upstream provider and authentication paths
3. Prepare escalation if resolution thresholds are exceeded
{% endif %}

---

## Management Ask
- **No action required** from management at this time.
- Network Operations will provide the next update at **{{ next_update_time }}** or sooner if conditions change.

---

## Status Commitment
We will continue to provide structured updates until:
- Service is fully restored **or**
- Incident is formally escalated with a confirmed remediation plan

---

*Generated automatically to ensure consistent, auditable incident communication.*