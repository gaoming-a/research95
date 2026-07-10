# DSA 2026 LaTeX Skeleton Build Audit

Audit date: 2026-07-11 (Asia/Shanghai)

Status: PASS_TEMPLATE_TECHNICAL_GATE / AUTHOR_METADATA_PENDING

## Inputs

- Official ZIP:
  `https://dsa26.techconf.org/download/DSA-Paper-Template.zip`
- ZIP SHA-256:
  `4AA03B1133DEDA277A507D9AD7897FE032027DAAD452CE86D7840EC37EA1D74F`
- `IEEEconf.cls` SHA-256:
  `AED94D44C0EB4A7B84A5B065CD55531F995D14D90AA0089A7EA0DB8BB313CDAE`
- Tracked skeleton source:
  `docs/submission/dsa_2026/dsa_template_skeleton.tex`
- Skeleton source SHA-256:
  `87E388FD67E5575F9DF9BA64FA0C1004B4E4737751CFCF6554639059E556B410`

The skeleton contains explicit placeholder author metadata and is marked as a
non-submission document. It contains no scientific result.

## Build Diagnosis and Repair

The first command used MiKTeX `latexmk`. It failed before TeX compilation
because the local MiKTeX installation could not find the Perl script engine
required by `latexmk`.

This was an environment/toolchain problem, not a template or source error. No
package or new runtime was installed. The shortest equivalent clean build used
two direct passes:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error dsa_template_skeleton.tex
pdflatex -interaction=nonstopmode -halt-on-error -file-line-error dsa_template_skeleton.tex
```

The second-pass log has zero LaTeX warnings, undefined references, overfull
boxes, underfull boxes, or errors.

## PDF Verification

- Output: `output/pdf/dsa_2026_template_skeleton.pdf`
- PDF SHA-256:
  `6C787A6EB4CB17C021424348553FE31D2816A2704CE7835D5D8AC98D8EE04C02`
- Pages: 1
- Page size: 612 x 792 points, US Letter
- PDF version: 1.5
- Fonts: 8 font subsets; all embedded
- Images: none
- Page numbers: none visible
- Section numbering: Arabic numerals
- Keywords: 4
- Render audit: 250 dpi page rendering inspected; no clipping, overlap,
  missing glyphs, black boxes, or unreadable text

## Rebuild Procedure

1. Download the official ZIP and verify its SHA-256 against this record.
2. Extract it into a clean temporary directory.
3. Copy `dsa_template_skeleton.tex` beside the unmodified `IEEEconf.cls`.
4. Run the two `pdflatex` commands above.
5. Run `pdfinfo`, `pdffonts`, `pdfimages -list`, and a 220--300 dpi
   `pdftoppm` render.
6. Verify the output SHA only when the same TeX engine/version and creation
   metadata are expected; otherwise compare structure, logs, fonts, and render.

## Boundary

This PASS proves only that the official LaTeX class can be built and visually
audited in the current environment. It does not pass D0.1--D0.5, approve author
metadata, authorize P1, authorize a model API, or make the existing manuscript
submission-ready.
