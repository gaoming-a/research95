from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_patch_blank_context(diff_text: str) -> str:
    lines = diff_text.strip("\n").splitlines()
    return "\n".join(" " if line == "" else line for line in lines) + "\n"


OFFICIAL_PATCH = normalize_patch_blank_context(
    r"""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2107,7 +2107,7 @@ def js_to_json(code):
         v = m.group(0)
         if v in ('true', 'false', 'null'):
             return v
-        elif v.startswith('/*') or v == ',':
+        elif v.startswith('/*') or v.startswith('//') or v == ',':
             return ""

         if v[0] in ("'", '"'):
@@ -2134,7 +2134,7 @@ def js_to_json(code):
     return re.sub(r'''(?sx)
         "(?:[^"\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^"\\]*"|
         '(?:[^'\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^'\\]*'|
-        /\*.*?\*/|,(?=\s*[\]}])|
+        /\*.*?\*/|//[^\n]*|,(?=\s*[\]}])|
         [a-zA-Z_][.a-zA-Z_0-9]*|
         \b(?:0[xX][0-9a-fA-F]+|0+[0-7]+)(?:\s*:)?|
         [0-9]+(?=\s*:)
"""
)


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


REGEX_ONLY_PATCH = normalize_patch_blank_context(
    r"""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2134,7 +2134,7 @@ def js_to_json(code):
     return re.sub(r'''(?sx)
         "(?:[^"\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^"\\]*"|
         '(?:[^'\\]*(?:\\\\|\\['"nurtbfx/\n]))*[^'\\]*'|
-        /\*.*?\*/|,(?=\s*[\]}])|
+        /\*.*?\*/|//[^\n]*|,(?=\s*[\]}])|
         [a-zA-Z_][.a-zA-Z_0-9]*|
         \b(?:0[xX][0-9a-fA-F]+|0+[0-7]+)(?:\s*:)?|
         [0-9]+(?=\s*:)
"""
)


REPLACER_ONLY_PATCH = normalize_patch_blank_context(
    r"""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2107,7 +2107,7 @@ def js_to_json(code):
         v = m.group(0)
         if v in ('true', 'false', 'null'):
             return v
-        elif v.startswith('/*') or v == ',':
+        elif v.startswith('/*') or v.startswith('//') or v == ',':
             return ""

         if v[0] in ("'", '"'):
"""
)


def base_record() -> dict[str, Any]:
    issue = "js_to_json should ignore JavaScript single-line // comments."
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_23",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_js_to_json_edgecases.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_23_js_to_json_line_comments.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_23_js_to_json_line_comments.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_23",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_js_to_json_edgecases"],
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
            "bugsinpy_youtube-dl_23__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 23 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_23__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_23__regex_only_line_comment",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            REGEX_ONLY_PATCH,
            "Partial negative: tokenizes // comments but still converts them to JSON strings.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_23__replacer_only_line_comment",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            REPLACER_ONLY_PATCH,
            "Partial negative: replacer can drop // tokens, but the tokenizer never matches them.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_23 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
