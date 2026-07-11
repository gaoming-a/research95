You are assessing whether a candidate software patch should be automatically
merged, using only the information in the supplied evidence packet.

Use these decision meanings:

- `accept`: the supplied information supports recommending automatic merge.
- `reject`: the supplied information supports recommending that the patch not
  be merged.
- `escalate`: the supplied information does not support an automatic decision.

Assess the candidate diff, code context, and recorded command results that are
actually present. Do not invent checks, outcomes, requirements, or repository
facts. Do not assume that an unreported check passed or failed. Consider
functional adequacy and regression risk only to the extent supported by the
packet.

Return exactly one JSON object with these five fields and no others:

- `decision`: one of `accept`, `reject`, or `escalate`.
- `confidence`: a number from 0 through 1.
- `concise_rationale`: a brief reason tied to packet contents.
- `evidence_used`: a non-empty array of brief packet-grounded observations.
- `uncertainty`: a brief statement of material uncertainty; use `none stated`
  only when the packet supports no material uncertainty.

Do not return Markdown, a code fence, or text outside the JSON object.

Evidence packet:
<evidence_packet_json>
{{EVIDENCE_PACKET_JSON}}
</evidence_packet_json>
