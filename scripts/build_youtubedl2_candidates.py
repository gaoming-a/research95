from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_patch_blank_context(diff_text: str) -> str:
    lines = diff_text.strip("\n").splitlines()
    return "\n".join(" " if line == "" else line for line in lines) + "\n"


OFFICIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/extractor/common.py
+++ b/youtube_dl/extractor/common.py
@@ -2007,16 +2007,14 @@ class InfoExtractor(object):
                                     f['url'] = initialization_url
                                 f['fragments'].append({location_key(initialization_url): initialization_url})
                             f['fragments'].extend(representation_ms_info['fragments'])
-                        try:
-                            existing_format = next(
-                                fo for fo in formats
-                                if fo['format_id'] == representation_id)
-                        except StopIteration:
-                            full_info = formats_dict.get(representation_id, {}).copy()
-                            full_info.update(f)
-                            formats.append(full_info)
-                        else:
-                            existing_format.update(f)
+                        # According to [1, 5.3.5.2, Table 7, page 35] @id of Representation
+                        # is not necessarily unique within a Period thus formats with
+                        # the same `format_id` are quite possible. There are numerous examples
+                        # of such manifests (see https://github.com/rg3/youtube-dl/issues/15111,
+                        # https://github.com/rg3/youtube-dl/issues/13919)
+                        full_info = formats_dict.get(representation_id, {}).copy()
+                        full_info.update(f)
+                        formats.append(full_info)
                     else:
                         self.report_warning('Unknown MIME type %s in DASH manifest' % mime_type)
         return formats
""")


EMPTY_DIFF = "diff --git a/youtube_dl/extractor/common.py b/youtube_dl/extractor/common.py\n"


PARTIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/extractor/common.py
+++ b/youtube_dl/extractor/common.py
@@ -2016,7 +2016,7 @@ class InfoExtractor(object):
                             full_info.update(f)
                             formats.append(full_info)
                         else:
-                            existing_format.update(f)
+                            pass
                     else:
                         self.report_warning('Unknown MIME type %s in DASH manifest' % mime_type)
         return formats
""")


IRRELEVANT_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/extractor/common.py
+++ b/youtube_dl/extractor/common.py
@@ -1830,5 +1830,6 @@ class InfoExtractor(object):
         mpd_duration = parse_duration(mpd_doc.get('mediaPresentationDuration'))
+        mpd_duration = mpd_duration
         formats = []
         for period in mpd_doc.findall(_add_ns('Period')):
             period_duration = parse_duration(period.get('duration')) or mpd_duration
             period_ms_info = extract_multisegment_info(period, {
""")


def base_record() -> dict[str, Any]:
    issue = (
        "DASH MPD parsing should preserve multiple Representation entries that "
        "share the same id instead of merging them into one format."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_2",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/extractor/common.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_2_parse_mpd_formats.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_2_parse_mpd_formats.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_2",
        "touched_files": ["youtube_dl/extractor/common.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_InfoExtractor.TestInfoExtractor.test_parse_mpd_formats"],
    }


def candidate(
    model_candidate_id: str,
    patch_id: str,
    candidate_type: str,
    expected_outcome: str,
    patch_materialization: str,
    patch_text: str,
    construction_notes: str,
) -> dict[str, Any]:
    record = base_record()
    record.update(
        {
            "candidate_type": candidate_type,
            "construction_notes": construction_notes,
            "expected_outcome": expected_outcome,
            "model_candidate_id": model_candidate_id,
            "oracle_workdir": f"data/patch_verification/workdirs/{patch_id}",
            "patch_id": patch_id,
            "patch_materialization": patch_materialization,
            "patch_text": patch_text,
        }
    )
    return record


def build_candidates() -> list[dict[str, Any]]:
    return [
        candidate(
            "candidate_0001",
            "bugsinpy_youtube-dl_2__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference diff from the BugsInPy youtube-dl bug 2 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_2__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_2__ignore_duplicate_representation",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: avoids overwriting duplicate ids but still drops the duplicate representation.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_2__irrelevant_noop_assignment",
            "irrelevant_patch",
            "irrelevant_or_noop",
            "manual_irrelevant_diff_against_buggy_checkout",
            IRRELEVANT_PATCH,
            "Irrelevant negative: changes no MPD parsing behavior.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_2 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
