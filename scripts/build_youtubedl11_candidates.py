from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_patch_blank_context(diff_text: str) -> str:
    lines = diff_text.strip("\n").splitlines()
    return "\n".join(" " if line == "" else line for line in lines) + "\n"


OFFICIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -3519,7 +3519,7 @@ def str_or_none(v, default=None):

 def str_to_int(int_str):
     \"\"\" A more relaxed version of int_or_none \"\"\"
-    if int_str is None:
-        return None
+    if not isinstance(int_str, compat_str):
+        return int_str
     int_str = re.sub(r'[,\\.\\+]', '', int_str)
     return int(int_str)
""")


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


PARTIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -3519,7 +3519,7 @@ def str_or_none(v, default=None):

 def str_to_int(int_str):
     \"\"\" A more relaxed version of int_or_none \"\"\"
-    if int_str is None:
-        return None
+    if isinstance(int_str, int):
+        return int_str
     int_str = re.sub(r'[,\\.\\+]', '', int_str)
     return int(int_str)
""")


IRRELEVANT_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -3528,5 +3528,6 @@ def str_to_int(int_str):

 def float_or_none(v, scale=1, invscale=1, default=None):
+    v = v
     if v is None:
         return default
     try:
""")


def base_record() -> dict[str, Any]:
    issue = (
        "str_to_int should remain a relaxed parser by preserving non-string "
        "inputs such as None and integers instead of applying re.sub to them."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_11",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_str_to_int.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_11_str_to_int.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_11_str_to_int.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_11",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_str_to_int"],
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
            "bugsinpy_youtube-dl_11__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 11 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_11__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_11__int_only_non_string_guard",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: preserves integers but sends None into re.sub.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_11__irrelevant_noop_assignment",
            "irrelevant_patch",
            "irrelevant_or_noop",
            "manual_irrelevant_diff_against_buggy_checkout",
            IRRELEVANT_PATCH,
            "Irrelevant negative: changes no str_to_int behavior.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_11 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
