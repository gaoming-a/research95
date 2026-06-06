# Imagegen Prompts

## `imagegen_framework.png`

```text
Use case: scientific-educational
Asset type: high-end research paper figure, graphical abstract / overview figure for a CCF-A software engineering paper
Primary request: Create a polished publication-quality graphical abstract for a paper about tool-augmented verification of AI-generated software patches.
Scene/backdrop: clean white academic paper background, no mock browser frame, no decorative gradients.
Subject: a pipeline showing an AI-generated patch being reviewed by three increasingly evidence-aware reviewers: LLM-only review, prompt-only evidence-first review, and tool-augmented verification. The final gate outputs Accept, Reject, or Escalate.
Style/medium: crisp vector-like editorial infographic, Nature/ACM/IEEE paper figure style, flat shapes, precise arrows, clean geometry, professional academic design.
Composition/framing: wide horizontal figure, left-to-right workflow. Left: small code patch card with diff-like lines. Middle: three stacked reviewer modules with increasing evidence strength. Right: merge gate with three outcomes. Include a subtle evidence layer icon with test/check symbols feeding into the tool-augmented verifier.
Lighting/mood: neutral, bright, rigorous, restrained.
Color palette: white background; deep blue for LLM-only; amber for prompt-only evidence-first; green for tool-augmented verification; red accent only for unsafe partial patch / reject risk; dark gray text.
Text (verbatim): "AI Patch", "LLM-only", "Evidence-first", "Tool-augmented", "Accept", "Reject", "Escalate", "Executable evidence".
Constraints: text must be readable and spelled exactly; no extra labels; no fake equations; no logos; no watermark; no people; no 3D cartoon style. Use thin arrows and balanced spacing. Make it look suitable for a top-tier software engineering conference paper.
Avoid: dense tiny text, garbled text, icons that look playful, photographic style, clutter, neon colors, glossy gradients, random code text, brand logos.
```

## `imagegen_evidence_boundary.png`

```text
Use case: scientific-educational
Asset type: high-end research paper figure, evidence-ablation conceptual figure
Primary request: Create a polished publication-quality infographic explaining evidence visibility levels for AI patch verification.
Scene/backdrop: clean white academic paper background.
Subject: a three-column comparison of review conditions. Column 1: LLM-only, sees only task and patch. Column 2: Evidence-first, sees task, patch, visible tests, evidence metadata. Column 3: Tool-augmented, sees task, patch, visible tests, evidence metadata, patch apply status, behavior summary. Evaluator labels remain hidden in all columns.
Style/medium: crisp vector-like scientific infographic, ACM/IEEE top conference style, flat design, clean grid, precise icons, restrained colors.
Composition/framing: wide landscape, three vertical columns with a layered evidence stack. Use check icons for visible evidence and lock icons for hidden information. Tool-augmented column should visually have the strongest evidence stack but still show a locked hidden-label layer.
Lighting/mood: neutral, rigorous, minimal.
Color palette: deep blue for LLM-only, amber for Evidence-first, green for Tool-augmented, light gray for hidden/locked items, dark gray text.
Text (verbatim): "LLM-only", "Evidence-first", "Tool-augmented", "Task + Patch", "Visible Tests", "Evidence Metadata", "Patch Apply", "Behavior Summary", "Evaluator Labels Hidden".
Constraints: all text must be readable and spelled exactly; no extra labels; no tiny text; no watermark; no logos; no people; no 3D; no decorative background. Make it look like a CCF-A software engineering paper figure.
Avoid: garbled words, excessive icons, playful style, gradients, random numbers, fake charts.
```

## `imagegen_tradeoff.png`

```text
Create a clean publication-quality academic infographic for an AI software patch verification paper. White background, flat vector-like style, IEEE/ACM paper figure aesthetic.

Wide landscape layout with three method cards from left to right:
1. "LLM-only" with high "Recall" bar and medium "Safety" bar, plus small red warning icon labeled "False accept risk".
2. "Evidence-first" with high "Safety" bar and medium "Recall" bar, plus amber warning icon labeled "Recall loss".
3. "Tool-augmented" with high "Safety" bar and high "Recall" bar, plus green check icon labeled "Balanced gate".

Use only these exact text labels: "LLM-only", "Evidence-first", "Tool-augmented", "Safety", "Recall", "False accept risk", "Recall loss", "Balanced gate".

Color palette: deep blue, amber, green, red accent, dark gray text. No percentages, no extra labels, no logos, no watermark, no people, no decorative background, no tiny text. Make it look like a top-tier software engineering conference figure.
```

## `imagegen_claim_boundary.png`

```text
Create a polished graphical abstract panel for a top-tier software engineering research paper.

Theme: claim boundary for AI-generated patch verification.

Composition: left-to-right progression with three clean blocks connected by arrows:
1. "LLM-only" block: blue, shows a patch icon and a small red warning triangle.
2. "Evidence-first" block: amber, shows a document/evidence icon and a cautious gate.
3. "Tool-augmented" block: green, shows a terminal/test icon plus checkmark.

Below the three blocks, add a clean claim strip with three short labels:
"Unsafe alone" under LLM-only, "Mixed result" under Evidence-first, "Conditional support" under Tool-augmented.

Style: flat vector-like, white background, academic infographic, CCF-A/IEEE/ACM paper visual style, precise arrows, no decorative gradients, no 3D, no people.

Use only these exact text labels: "LLM-only", "Evidence-first", "Tool-augmented", "Unsafe alone", "Mixed result", "Conditional support".

Constraints: text must be readable and spelled exactly; no extra labels; no numbers; no logos; no watermark; no fake equations; balanced whitespace; professional publication figure.
```
