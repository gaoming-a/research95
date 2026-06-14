from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_patch_blank_context(diff_text: str) -> str:
    lines = diff_text.strip("\n").splitlines()
    return "\n".join(" " if line == "" else line for line in lines) + "\n"


OFFICIAL_PATCH = normalize_patch_blank_context(
    """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2733,6 +2733,8 @@ def cli_option(params, command_option, param):

 def cli_bool_option(params, command_option, param, true_value='true', false_value='false', separator=None):
     param = params.get(param)
+    if param is None:
+        return []
     assert isinstance(param, bool)
     if separator:
         return [command_option + separator + (true_value if param else false_value)]
"""
)


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


NONE_AS_FALSE_PATCH = normalize_patch_blank_context(
    """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2733,6 +2733,8 @@ def cli_option(params, command_option, param):

 def cli_bool_option(params, command_option, param, true_value='true', false_value='false', separator=None):
     param = params.get(param)
+    if param is None:
+        param = False
     assert isinstance(param, bool)
     if separator:
         return [command_option + separator + (true_value if param else false_value)]
"""
)


FALSY_SKIP_PATCH = normalize_patch_blank_context(
    """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2733,6 +2733,8 @@ def cli_option(params, command_option, param):

 def cli_bool_option(params, command_option, param, true_value='true', false_value='false', separator=None):
     param = params.get(param)
+    if not param:
+        return []
     assert isinstance(param, bool)
     if separator:
         return [command_option + separator + (true_value if param else false_value)]
"""
)


def base_record() -> dict[str, Any]:
    issue = (
        "cli_bool_option should skip missing optional boolean parameters without "
        "treating an explicit False value as missing."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_17",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_cli_bool_option.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_17_cli_bool_option.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_17_cli_bool_option.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_17",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_cli_bool_option"],
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
            "bugsinpy_youtube-dl_17__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 17 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_17__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_17__none_as_false",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            NONE_AS_FALSE_PATCH,
            "Partial negative: avoids the assertion but emits an explicit false option for missing params.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_17__falsy_skip",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            FALSY_SKIP_PATCH,
            "Partial negative: skips missing params but also skips explicit False values.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_17 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
