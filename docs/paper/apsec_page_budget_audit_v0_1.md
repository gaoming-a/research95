# APSEC IEEEtran and page-budget audit

Status: `passed`

## Counts

| item | value |
| --- | ---: |
| word count excluding tables | 3071 |
| converted tables | 14 |
| converted figures | 3 |
| references | 11 |
| estimated pages | 8.14 |
| compiled PDF pages | 8 |

## Compile Summary

- compiled PDF present: `true`
- undefined references in latest log: `False`
- overfull hbox count in latest log: `4`
- underfull hbox count in latest log: `11`

## Checks

| check | passed |
| --- | --- |
| ieeetran_source_generated | true |
| bibtex_generated | true |
| citation_keys_converted_to_cite_commands | true |
| page_budget_estimate_within_apsec_technical_limit | true |
| compiled_pdf_within_apsec_technical_limit | true |
| compiled_pdf_has_no_undefined_references | true |
| stress_matrix_result_present_in_tex | true |
| anonymous_author_block_present | true |
| final_pdf_not_claimed | true |

## Compile Runs

| command | exit code |
| --- | ---: |
| `pdflatex -interaction=nonstopmode apsec_ieeetran_draft.tex` | 0 |
| `bibtex apsec_ieeetran_draft` | 0 |
| `pdflatex -interaction=nonstopmode apsec_ieeetran_draft.tex` | 0 |
| `pdflatex -interaction=nonstopmode apsec_ieeetran_draft.tex` | 0 |

## Remaining Formatting Risks

- Converted table captions are mechanical and should be manually shortened before submission.
- Compiled PDF still has table-width overfull/underfull warnings that need manual layout repair.
- Final double-blind compliance still requires visual inspection even though the source author block is anonymous.
- BibTeX entries compile but should be normalized to venue-quality fields.
- The current package is a draft source conversion, not a submitted or camera-ready PDF.
