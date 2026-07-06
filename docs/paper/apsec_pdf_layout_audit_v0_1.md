# APSEC PDF layout audit

- status: `passed`
- pdf: `docs/paper/apsec_ieeetran_draft.pdf`
- pdf pages: `8`
- render dir: `tmp/pdfs/apsec_ieeetran_layout_audit`

## Checks

| check | passed | detail |
| --- | ---: | --- |
| `compiled_pdf_exists` | true | `"docs/paper/apsec_ieeetran_draft.pdf"` |
| `pdfinfo_pages_within_apsec_limit` | true | `8` |
| `rendered_page_count_matches_pdfinfo` | true | `{"pdfinfo_pages": 8, "rendered_pages": 8}` |
| `rendered_pages_nonblank` | true | `{"tmp/pdfs/apsec_ieeetran_layout_audit/page-1.png": 0.16671, "tmp/pdfs/apsec_ieeetran_layout_audit/page-2.png": 0.163116, "tmp/pdfs/apsec_ieeetran_layout_audit/page-3.png": 0.087517, "tmp/pdfs/apsec_ieeetran_layout_audit/page-4.png": 0.078743, "tmp/pdfs/apsec_ieeetran_layout_audit/page-5.png": 0.097845, "tmp/pdfs/apsec_ieeetran_layout_audit/page-6.png": 0.15789, "tmp/pdfs/apsec_ieeetran_layout_audit/page-7.png": 0.097989, "tmp/pdfs/apsec_ieeetran_layout_audit/page-8.png": 0.031437}` |
| `source_author_block_anonymous` | true | `"author block"` |
| `old_apsec_wording_absent` | true | `[]` |

## Remaining Risks

- This audit verifies renderability and obvious blank-page/layout failures; final camera-ready visual polish still needs human inspection.
- The compiled PDF remains a draft package, not a final submission artifact.
