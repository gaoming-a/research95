from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


OFFICIAL_PATCH = """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1701,8 +1701,8 @@ def js_to_json(code):
         if v in ('true', 'false', 'null'):
             return v
         if v.startswith('"'):
-            return v
-        if v.startswith("'"):
+            v = re.sub(r"\\\\'", "'", v[1:-1])
+        elif v.startswith("'"):
             v = v[1:-1]
             v = re.sub(r"\\\\\\\\|\\\\'|\\"", lambda m: {
                 '\\\\\\\\': '\\\\\\\\',
"""


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


PARTIAL_PATCH = """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1701,8 +1701,8 @@ def js_to_json(code):
         if v in ('true', 'false', 'null'):
             return v
         if v.startswith('"'):
-            return v
-        if v.startswith("'"):
+            v = v[1:-1]
+        elif v.startswith("'"):
             v = v[1:-1]
             v = re.sub(r"\\\\\\\\|\\\\'|\\"", lambda m: {
                 '\\\\\\\\': '\\\\\\\\',
"""


IRRELEVANT_PATCH = """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1721,6 +1721,7 @@ def js_to_json(code):
 
 
 def qualities(quality_ids):
+    quality_ids = quality_ids
     \"\"\" Get a numeric quality value out of a list of possible values \"\"\"
     def q(qid):
         try:
"""


def base_record() -> dict[str, Any]:
    issue = (
        "js_to_json should convert JavaScript-style quoted strings containing escaped "
        "apostrophes into valid JSON without preserving invalid apostrophe escapes."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_7",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_js_to_json_realworld.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_7_js_to_json.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_7_js_to_json.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_7",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_js_to_json_realworld"],
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
            "bugsinpy_youtube-dl_7__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference diff from the BugsInPy youtube-dl bug 7 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_7__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_7__strip_without_unescape",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: strips outer double quotes but preserves invalid escaped apostrophes.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_7__irrelevant_noop_assignment",
            "irrelevant_patch",
            "irrelevant_or_noop",
            "manual_irrelevant_diff_against_buggy_checkout",
            IRRELEVANT_PATCH,
            "Irrelevant negative: changes no js_to_json behavior.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_7 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
