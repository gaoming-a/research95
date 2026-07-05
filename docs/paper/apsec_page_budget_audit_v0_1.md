# APSEC IEEEtran and page-budget audit

Status: `passed`

## Counts

| item | value |
| --- | ---: |
| word count excluding tables | 2706 |
| converted tables | 11 |
| converted figures | 3 |
| references | 11 |
| estimated pages | 7.05 |
| compiled PDF pages | 6 |

## Compile Summary

- compiled PDF present: `true`
- undefined references in latest log: `False`
- overfull hbox count in latest log: `6`
- underfull hbox count in latest log: `24`

## Checks

| check | passed |
| --- | --- |
| ieeetran_source_generated | true |
| bibtex_generated | true |
| citation_keys_converted_to_cite_commands | true |
| page_budget_estimate_within_apsec_technical_limit | true |
| final_pdf_not_claimed | true |

## Remaining Formatting Risks

- Converted table captions are mechanical and should be manually shortened before submission.
- Compiled PDF still has table-width overfull/underfull warnings that need manual layout repair.
- Final double-blind compliance still requires visual inspection.
- BibTeX entries compile but should be normalized to venue-quality fields.
- The current package is a draft source conversion, not a submitted or camera-ready PDF.
