Subject: Service Update - {{ incident_title }}

Dear Valued Customer,

We are writing to provide you with an update regarding the current service situation.

## Status Summary
| Field | Value |
|-------|-------|
| Status | {{ current_status | title }} |
| Impact | {{ impact_summary }} |
| Priority | {{ severity }} |
| Next Update | {{ next_update_time }} |

## What We Know
Our team is actively working to resolve this issue. {{ impact_summary | capitalize }}.

{% if has_checks %}
Our engineers have completed the following diagnostic steps:
{{ checks_done_formatted }}
{% endif %}

## What We Are Doing
{% for step in next_steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

## Next Update
We will provide our next update within {{ next_update_time }}, or sooner if there are significant developments.

If you have questions, please contact your account representative or our support team.

Best regards,
Network Operations Center

---
Update: {{ timestamp }} | Ref: {{ severity }}-{{ incident_title | replace(" ", "-") | lower }}
