# EVP-7 G5 376-Record Statistical Analysis

Raw model responses remain ignored under outputs/. This artifact reads only review structure, decisions, costs, candidate labels, project, and patch-source metadata, then writes aggregate raw-output-free statistics.

## Method

- Bootstrap unit: `candidate_id`
- Bootstrap samples: 2000
- Bootstrap seed: 9507
- Paired baseline: `E0`
- Effect size: point estimate delta versus E0 for paired comparisons

## Per-Evidence-Level Intervals

| evidence | metric | point | Wilson 95% CI | bootstrap 95% CI |
|---|---|---:|---:|---:|
| E0 | false_accept_rate | 0.0000 | [0.0000, 0.0493] | [0.0000, 0.0000] |
| E0 | accepted_precision | 1.0000 | [0.2065, 1.0000] | [1.0000, 1.0000] |
| E0 | correct_recall | 0.0500 | [0.0089, 0.2361] | [0.0000, 0.1579] |
| E0 | escalation_rate | 0.5213 | [0.4215, 0.6194] | [0.4255, 0.6277] |
| E2 | false_accept_rate | 0.0000 | [0.0000, 0.0493] | [0.0000, 0.0000] |
| E2 | accepted_precision | NA | NA | NA |
| E2 | correct_recall | 0.0000 | [0.0000, 0.1611] | [0.0000, 0.0000] |
| E2 | escalation_rate | 0.6064 | [0.5053, 0.6991] | [0.5106, 0.7021] |
| E4 | false_accept_rate | 0.0000 | [0.0000, 0.0493] | [0.0000, 0.0000] |
| E4 | accepted_precision | 1.0000 | [0.2065, 1.0000] | [1.0000, 1.0000] |
| E4 | correct_recall | 0.0500 | [0.0089, 0.2361] | [0.0000, 0.1667] |
| E4 | escalation_rate | 0.2234 | [0.1510, 0.3175] | [0.1383, 0.3085] |
| E6 | false_accept_rate | 0.0000 | [0.0000, 0.0493] | [0.0000, 0.0000] |
| E6 | accepted_precision | 1.0000 | [0.6457, 1.0000] | [1.0000, 1.0000] |
| E6 | correct_recall | 0.3500 | [0.1812, 0.5671] | [0.1429, 0.5714] |
| E6 | escalation_rate | 0.1702 | [0.1076, 0.2587] | [0.0957, 0.2553] |

## Paired Delta Versus E0

| comparison | metric | point delta | bootstrap 95% CI | P(delta > 0) |
|---|---|---:|---:|---:|
| E2 - E0 | false_accept_rate | 0.0000 | [0.0000, 0.0000] | 0.0000 |
| E2 - E0 | correct_recall | -0.0500 | [-0.1667, 0.0000] | 0.0000 |
| E2 - E0 | escalation_rate | 0.0851 | [-0.0106, 0.1702] | 0.9510 |
| E2 - E0 | utility_score | -3.0000 | [-6.7500, 0.5000] | 0.0400 |
| E4 - E0 | false_accept_rate | 0.0000 | [0.0000, 0.0000] | 0.0000 |
| E4 - E0 | correct_recall | 0.0000 | [-0.1539, 0.1430] | 0.3535 |
| E4 - E0 | escalation_rate | -0.2979 | [-0.3936, -0.1915] | 0.0000 |
| E4 - E0 | utility_score | 7.0000 | [2.5000, 11.7500] | 0.9980 |
| E6 - E0 | false_accept_rate | 0.0000 | [0.0000, 0.0000] | 0.0000 |
| E6 - E0 | correct_recall | 0.3000 | [0.1000, 0.5263] | 0.9965 |
| E6 - E0 | escalation_rate | -0.3511 | [-0.4574, -0.2553] | 0.0000 |
| E6 - E0 | utility_score | 14.2500 | [7.7500, 21.5063] | 1.0000 |

## Per-Project Breakdown

| group | evidence | records | false accept | correct recall | escalation | utility |
|---|---|---:|---:|---:|---:|---:|
| PySnooper | E0 | 10 | 0.0000 | 0.0000 | 0.5000 | -1.2500 |
| PySnooper | E2 | 10 | 0.0000 | 0.0000 | 0.6000 | -1.5000 |
| PySnooper | E4 | 10 | 0.0000 | 0.5000 | 0.1000 | 0.7500 |
| PySnooper | E6 | 10 | 0.0000 | 0.5000 | 0.2000 | 0.5000 |
| cookiecutter | E0 | 19 | 0.0000 | 0.0000 | 0.4211 | -2.0000 |
| cookiecutter | E2 | 19 | 0.0000 | 0.0000 | 0.5789 | -2.7500 |
| cookiecutter | E4 | 19 | 0.0000 | 0.0000 | 0.1053 | -1.5000 |
| cookiecutter | E6 | 19 | 0.0000 | 0.3333 | 0.1053 | -0.5000 |
| httpie | E0 | 6 | 0.0000 | 0.0000 | 0.6667 | -1.0000 |
| httpie | E2 | 6 | 0.0000 | 0.0000 | 0.6667 | -1.0000 |
| httpie | E4 | 6 | 0.0000 | 0.0000 | 0.1667 | -0.2500 |
| httpie | E6 | 6 | 0.0000 | 0.0000 | 0.1667 | -0.2500 |
| tqdm | E0 | 7 | 0.0000 | 0.0000 | 0.4286 | -0.7500 |
| tqdm | E2 | 7 | 0.0000 | 0.0000 | 0.7143 | -1.2500 |
| tqdm | E4 | 7 | 0.0000 | 0.0000 | 0.1429 | -0.2500 |
| tqdm | E6 | 7 | 0.0000 | 0.0000 | 0.1429 | -0.2500 |
| youtube-dl | E0 | 52 | 0.0000 | 0.0769 | 0.5577 | -7.2500 |
| youtube-dl | E2 | 52 | 0.0000 | 0.0000 | 0.5962 | -8.7500 |
| youtube-dl | E4 | 52 | 0.0000 | 0.0000 | 0.3077 | -4.0000 |
| youtube-dl | E6 | 52 | 0.0000 | 0.3846 | 0.1923 | 2.5000 |

## Per-Patch-Source Breakdown

| group | evidence | records | false accept | correct recall | escalation | utility |
|---|---|---:|---:|---:|---:|---:|
| buggy_noop | E0 | 20 | 0.0000 | NA | 0.6000 | -3.0000 |
| buggy_noop | E2 | 20 | 0.0000 | NA | 0.7500 | -3.7500 |
| buggy_noop | E4 | 20 | 0.0000 | NA | 0.0000 | 0.0000 |
| buggy_noop | E6 | 20 | 0.0000 | NA | 0.0500 | -0.2500 |
| correct_reference | E0 | 20 | NA | 0.0500 | 0.9000 | -4.5000 |
| correct_reference | E2 | 20 | NA | 0.0000 | 0.9500 | -5.7500 |
| correct_reference | E4 | 20 | NA | 0.0500 | 0.9000 | -4.5000 |
| correct_reference | E6 | 20 | NA | 0.3500 | 0.6000 | 3.0000 |
| irrelevant_patch | E0 | 14 | 0.0000 | NA | 0.0000 | 0.0000 |
| irrelevant_patch | E2 | 14 | 0.0000 | NA | 0.0000 | 0.0000 |
| irrelevant_patch | E4 | 14 | 0.0000 | NA | 0.0000 | 0.0000 |
| irrelevant_patch | E6 | 14 | 0.0000 | NA | 0.0000 | 0.0000 |
| partial_fix | E0 | 40 | 0.0000 | NA | 0.4750 | -4.7500 |
| partial_fix | E2 | 40 | 0.0000 | NA | 0.5750 | -5.7500 |
| partial_fix | E4 | 40 | 0.0000 | NA | 0.0750 | -0.7500 |
| partial_fix | E6 | 40 | 0.0000 | NA | 0.0750 | -0.7500 |

## Boundary Check

- Raw-output-free check passed: true
- Raw response and prompt text fields are omitted from this tracked artifact.
