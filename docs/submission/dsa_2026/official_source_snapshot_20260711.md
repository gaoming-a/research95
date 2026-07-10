# DSA 2026 Official-Source Snapshot

Snapshot date: 2026-07-11 (Asia/Shanghai)

Purpose: freeze the venue facts used by P0/D0. This is a normalized evidence
snapshot, not a substitute for the live pages. All claims below are bounded to
the cited official sources and retrieval date.

## Source Manifest

| Source | URL | Retrieved SHA-256 |
|---|---|---|
| DSA home | https://dsa26.techconf.org/ | `AB187423D26D6E65C72BEF91CED943434BF2063927F22531C22C0F82ADC2AC01` |
| Submission | https://dsa26.techconf.org/submission | `F02B19193A1E1E4C8A56183A88C68CF861188985C6E52ADAE7F0A179D0FBBACD` |
| Regular/Short | https://dsa26.techconf.org/track/regular | `ED4E05770A6E9711A21C181EE084558D6A1F4CF173705937CE194E6A3FC64489` |
| Proceedings | https://dsa26.techconf.org/track/proceeding | `6A93D437CD2EEE077AF63197F9F8449DE3438C929ACCEE41D982A0D6935CE282` |
| Registration | https://dsa26.techconf.org/registration | `0DE23D57BF087EEA531A7AB5F038C77325A0A8F0C60E54B278929178F5550A32` |
| Previous conferences | https://dsa26.techconf.org/previous_conferences | `6790F518C5D3A4B322593A8F31F988D095E2D647EEF4B2832E1A59BEA77EE0C5` |
| CFP PDF | https://dsa26.techconf.org/download/CFP-DSA-2026.pdf | `453CB8CCAA6728213861B6732D9E8E155B9C577D77ED9918FAF7D3342FB59E74` |
| LaTeX template ZIP | https://dsa26.techconf.org/download/DSA-Paper-Template.zip | `4AA03B1133DEDA277A507D9AD7897FE032027DAAD452CE86D7840EC37EA1D74F` |
| Direct template PDF | https://dsa26.techconf.org/download/DSA-Paper-Template.pdf | `8736D187413B23CB81A28200B913A70BE36462AD3A69E6DF523C2C7C079FAD5D` |
| IEEE AI policy | https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/ | `F7E652159F3D566EFEA86BE721A673D3BDB875B479139E988A759B9CB7E340A5` |

The SHA-256 values are hashes of the bytes returned on the snapshot date. Live
content can change without notice.

## Verified Venue Facts

- Scope directly includes dependable software, verification/validation/testing,
  debugging/program repair, empirical studies, tools/automation, and the
  dependability of generative AI.
- Regular and Short Papers are due 2026-09-01. The public pages do not state a
  deadline time zone.
- Notification is 2026-10-18. Camera-ready and author registration are due
  2026-10-25. The conference is in Xiamen on 2026-11-14--15.
- A Regular Paper is at most 12 pages and a Short Paper at most 10 pages. The
  track page explicitly says these limits include content and references.
- Initial submissions are in English and PDF, include author names and
  affiliations, an abstract, and at most 6 keywords. Each paper can have at
  most 5 authors. The submission page does not describe double-blind review.
- At least three Program Committee members review each submission.
- The proceedings are stated to be published by IEEE CPS. The venue wording is
  that accepted papers will be submitted for possible inclusion in IEEE Xplore
  and Ei Compendex; this is not an indexing guarantee.
- One full registration is required per paper by 2026-10-25. Early/author fees
  are USD 700 for IEEE/REAJ/ORSC members and USD 750 for others.
- A co-author must present in person. A non-author guest presenter does not
  satisfy the publication/indexing condition.
- The official contact resolves to `zxc190007@utdallas.edu` from the DSA
  Secretariat link on the site.

## Previous-Proceedings Evidence for Library Verification

The DSA series page links the following IEEE Xplore proceedings. This proves
IEEE Xplore publication records, not Ei Compendex indexing.

| Year | IEEE Xplore conference ID | IEEE catalog | ISBN |
|---|---:|---|---|
| 2025 | `11320275` | `CFP25M61-ART` | `978-1-6654-7769-7` |
| 2024 | `10817827` | `CFP24M61-ART` | `979-8-3315-3239-0` |
| 2023 | `10314134` | `CFP23M61-ART` | `979-8-3503-0477-0` |

Engineering Village/Compendex must still be queried through the author's
institution. For each year, save the Compendex accession record, exact query,
database selection, retrieval date, and export/screenshot.

## AI-Policy Boundary

No DSA 2026 venue-specific GenAI author policy was found on the official site
as of the snapshot date. IEEE's general author policy requires disclosure in
the acknowledgments when AI-generated content, including text, figures, images,
or code, appears in an IEEE article; the system, affected sections, and level
of use must be identified. Grammar/editing-only use is generally outside the
mandatory rule, though disclosure is recommended.

This project has substantive AI participation beyond grammar correction, so it
must not rely on the editing-only exception. DSA Secretariat confirmation is a
hard gate before scientific execution or submission.

## Template Snapshot

- Official ZIP SHA-256: `4AA03B1133DEDA277A507D9AD7897FE032027DAAD452CE86D7840EC37EA1D74F`.
- `IEEEconf.cls` SHA-256: `AED94D44C0EB4A7B84A5B065CD55531F995D14D90AA0089A7EA0DB8BB313CDAE`.
- The class identifies itself as `IEEEconf` version 1.8 dated 2012-12-27.
- The official sample uses `\documentclass[conference]{IEEEconf}`.
- The default output is US Letter, 10 point, two-column.
- The ZIP's sample PDF and the direct PDF template have different byte/text
  content. The LaTeX build therefore uses the ZIP as the authoritative LaTeX
  source, not the separately linked PDF.

The reproducible build result is recorded in
`docs/submission/dsa_2026/dsa_template_skeleton_build_audit.md`.
