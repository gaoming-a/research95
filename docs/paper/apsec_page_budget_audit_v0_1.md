# APSEC IEEEtran and page-budget audit

Status: `passed`

## Counts

| item | value |
| --- | ---: |
| word count excluding tables | 3071 |
| converted tables | 6 |
| converted figures | 3 |
| references | 11 |
| estimated pages | 6.38 |
| compiled PDF pages | 6 |

## Compile Summary

- compiled PDF present: `true`
- undefined references in latest log: `False`
- overfull hbox count in latest log: `0`
- underfull hbox count in latest log: `11`

## Checks

| check | passed |
| --- | --- |
| ieeetran_source_generated | true |
| bibtex_generated | true |
| citation_keys_converted_to_cite_commands | true |
| camera_facing_caption_cleanup | true |
| camera_facing_internal_note_removed | true |
| camera_facing_table_count_curated | true |
| camera_facing_long_float_removed | true |
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

- Compiled PDF may still have underfull hbox warnings from narrow-column paragraph breaks that need visual layout review.
- Final double-blind compliance still requires visual inspection even though the source author block is anonymous.
- BibTeX entries compile but should be normalized to venue-quality fields.
- References remain sparse for APSEC and need a separate verified expansion pass.
- The current package is a draft source conversion, not a submitted or camera-ready PDF.
