# Patch Verification Metrics

## Confusion Matrix

For binary summaries, treat `correct` patches as positive and all other usable
outcomes as negative.

| Ground Truth | Decision | Count Name |
| --- | --- | --- |
| correct | accept | true accept |
| correct | reject | false reject |
| correct | escalate | escalated correct |
| incorrect/partial/overfitted/irrelevant | accept | false accept |
| incorrect/partial/overfitted/irrelevant | reject | true reject |
| incorrect/partial/overfitted/irrelevant | escalate | escalated incorrect |

`environment_invalid` candidates are excluded from main metrics and reported
separately.

## Primary Metrics

Accepted precision:

```text
true_accept / (true_accept + false_accept)
```

Correct-patch recall:

```text
true_accept / (true_accept + false_reject + escalated_correct)
```

False accept rate:

```text
false_accept / (false_accept + true_reject + escalated_incorrect)
```

False reject rate:

```text
false_reject / (true_accept + false_reject + escalated_correct)
```

Escalation rate:

```text
all_escalated / all_valid_candidates
```

Effective accepted precision, excluding escalations:

```text
true_accept / all_accepted
```

Human workload proxy:

```text
escalated_candidates / all_valid_candidates
```

## Secondary Metrics

- invalid-output rate;
- cost per accepted correct patch;
- cost per false accept avoided;
- per-project false accept rate;
- per-candidate-type false accept rate;
- claim support rate;
- unsupported accepted-claim rate.

## Stop-Gate Metrics

The first pilot should not be scaled unless evidence-first verification shows:

- lower false accept rate than LLM-only review; and
- accepted precision improves without accepting almost no patches; and
- escalation rate is interpretable rather than near-total rejection.

Near-total rejection means:

```text
acceptance_rate < 0.15
```

unless the pilot intentionally contains mostly invalid or incorrect patches.

The executable implementation is:

```powershell
python scripts\evaluate_api_pilot_gate.py `
  --metrics <full_run_dir>\metrics.json `
  --reviews <full_run_dir>\reviews.jsonl `
  --out-json <full_run_dir>\gate_report.json `
  --out-md <full_run_dir>\gate_report.md
```

Positive paper claims require a real, non-mock run whose gate verdict is
`continue`, followed by manual inspection of failure examples.
