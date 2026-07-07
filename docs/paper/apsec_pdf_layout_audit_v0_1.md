# APSEC PDF layout audit

- status: `passed`
- pdf: `docs/paper/apsec_ieeetran_draft.pdf`
- pdf pages: `7`
- render dir: `tmp/pdfs/apsec_ieeetran_layout_audit`

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `compiled_pdf_exists` | true | `"docs/paper/apsec_ieeetran_draft.pdf"` |
| `pdfinfo_pages_within_apsec_limit` | true | `7` |
| `rendered_page_count_matches_pdfinfo` | true | `{"pdfinfo_pages": 7, "rendered_pages": 7}` |
| `rendered_pages_nonblank` | true | `{"tmp/pdfs/apsec_ieeetran_layout_audit/page-1.png": 0.165198, "tmp/pdfs/apsec_ieeetran_layout_audit/page-2.png": 0.171013, "tmp/pdfs/apsec_ieeetran_layout_audit/page-3.png": 0.125749, "tmp/pdfs/apsec_ieeetran_layout_audit/page-4.png": 0.095434, "tmp/pdfs/apsec_ieeetran_layout_audit/page-5.png": 0.149734, "tmp/pdfs/apsec_ieeetran_layout_audit/page-6.png": 0.135097, "tmp/pdfs/apsec_ieeetran_layout_audit/page-7.png": 0.047275}` |
| `source_author_block_anonymous` | true | `"author block"` |
| `old_apsec_wording_absent` | true | `[]` |

## Remaining Risks

- This audit verifies renderability and obvious blank-page/layout failures; final camera-ready visual polish still needs human inspection.
- The compiled PDF remains a draft package, not a final submission artifact.
