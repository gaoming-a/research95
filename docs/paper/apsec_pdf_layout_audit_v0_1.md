# APSEC PDF layout audit

- status: `passed`
- pdf: `docs/paper/apsec_ieeetran_draft.pdf`
- pdf pages: `6`
- render dir: `tmp/pdfs/apsec_ieeetran_layout_audit`

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `compiled_pdf_exists` | true | `"docs/paper/apsec_ieeetran_draft.pdf"` |
| `pdfinfo_pages_within_apsec_limit` | true | `6` |
| `rendered_page_count_matches_pdfinfo` | true | `{"pdfinfo_pages": 6, "rendered_pages": 6}` |
| `rendered_pages_nonblank` | true | `{"tmp/pdfs/apsec_ieeetran_layout_audit/page-1.png": 0.16671, "tmp/pdfs/apsec_ieeetran_layout_audit/page-2.png": 0.16199, "tmp/pdfs/apsec_ieeetran_layout_audit/page-3.png": 0.102634, "tmp/pdfs/apsec_ieeetran_layout_audit/page-4.png": 0.131812, "tmp/pdfs/apsec_ieeetran_layout_audit/page-5.png": 0.167538, "tmp/pdfs/apsec_ieeetran_layout_audit/page-6.png": 0.062536}` |
| `source_author_block_anonymous` | true | `"author block"` |
| `old_apsec_wording_absent` | true | `[]` |

## Remaining Risks

- This audit verifies renderability and obvious blank-page/layout failures; final camera-ready visual polish still needs human inspection.
- The compiled PDF remains a draft package, not a final submission artifact.
