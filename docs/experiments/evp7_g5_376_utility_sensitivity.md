# EVP-7 G5 376-Record Utility Sensitivity

This analysis reads ignored review records structurally and joins tracked candidate labels only for aggregate utility calculations. It writes no raw model responses or prompt text.

## Method

- Utility formula: `true_accept - lambda*false_accept - mu*escalated - nu*false_reject`
- False accept penalties: `[1.0, 5.0, 10.0]`
- Escalation penalties: `[0.1, 0.25, 0.5]`
- False reject penalties: `[0.5, 1.0, 2.0]`
- Scenario count: 27

## Stability Summary

- Dominant best level: `E6`
- Dominant best-level share: 1.0000
- Dominant ranking: `E6 > E4 > E0 > E2`
- Dominant ranking share: 1.0000
- Interpretation: The current grid changes escalation and false-reject penalties but does not change false-accept penalties in this run because observed false accept counts are zero at every evidence level.

## Best Level Counts

| evidence level | scenarios as best |
|---|---:|
| E0 | 0 |
| E2 | 0 |
| E4 | 0 |
| E6 | 27 |

## Scenario Results

| lambda | mu | nu | best | ranking | E0 | E2 | E4 | E6 |
|---:|---:|---:|---|---|---:|---:|---:|---:|
| 1.0000 | 0.1000 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -4.4000 | -6.2000 | -1.6000 | 4.9000 |
| 1.0000 | 0.1000 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -4.9000 | -6.7000 | -2.1000 | 4.4000 |
| 1.0000 | 0.1000 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -5.9000 | -7.7000 | -3.1000 | 3.4000 |
| 1.0000 | 0.2500 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -11.7500 | -14.7500 | -4.7500 | 2.5000 |
| 1.0000 | 0.2500 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -12.2500 | -15.2500 | -5.2500 | 2.0000 |
| 1.0000 | 0.2500 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -13.2500 | -16.2500 | -6.2500 | 1.0000 |
| 1.0000 | 0.5000 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -24.0000 | -29.0000 | -10.0000 | -1.5000 |
| 1.0000 | 0.5000 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -24.5000 | -29.5000 | -10.5000 | -2.0000 |
| 1.0000 | 0.5000 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -25.5000 | -30.5000 | -11.5000 | -3.0000 |
| 5.0000 | 0.1000 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -4.4000 | -6.2000 | -1.6000 | 4.9000 |
| 5.0000 | 0.1000 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -4.9000 | -6.7000 | -2.1000 | 4.4000 |
| 5.0000 | 0.1000 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -5.9000 | -7.7000 | -3.1000 | 3.4000 |
| 5.0000 | 0.2500 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -11.7500 | -14.7500 | -4.7500 | 2.5000 |
| 5.0000 | 0.2500 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -12.2500 | -15.2500 | -5.2500 | 2.0000 |
| 5.0000 | 0.2500 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -13.2500 | -16.2500 | -6.2500 | 1.0000 |
| 5.0000 | 0.5000 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -24.0000 | -29.0000 | -10.0000 | -1.5000 |
| 5.0000 | 0.5000 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -24.5000 | -29.5000 | -10.5000 | -2.0000 |
| 5.0000 | 0.5000 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -25.5000 | -30.5000 | -11.5000 | -3.0000 |
| 10.0000 | 0.1000 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -4.4000 | -6.2000 | -1.6000 | 4.9000 |
| 10.0000 | 0.1000 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -4.9000 | -6.7000 | -2.1000 | 4.4000 |
| 10.0000 | 0.1000 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -5.9000 | -7.7000 | -3.1000 | 3.4000 |
| 10.0000 | 0.2500 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -11.7500 | -14.7500 | -4.7500 | 2.5000 |
| 10.0000 | 0.2500 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -12.2500 | -15.2500 | -5.2500 | 2.0000 |
| 10.0000 | 0.2500 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -13.2500 | -16.2500 | -6.2500 | 1.0000 |
| 10.0000 | 0.5000 | 0.5000 | E6 | E6 > E4 > E0 > E2 | -24.0000 | -29.0000 | -10.0000 | -1.5000 |
| 10.0000 | 0.5000 | 1.0000 | E6 | E6 > E4 > E0 > E2 | -24.5000 | -29.5000 | -10.5000 | -2.0000 |
| 10.0000 | 0.5000 | 2.0000 | E6 | E6 > E4 > E0 > E2 | -25.5000 | -30.5000 | -11.5000 | -3.0000 |

## Boundary Check

- Raw-output-free check passed: true
