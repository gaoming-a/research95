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
@@ -2,6 +2,7 @@
 # -*- coding: utf-8 -*-

 import calendar
+import codecs
 import contextlib
 import ctypes
 import datetime
@@ -1263,9 +1264,11 @@ class PagedList(object):


 def uppercase_escape(s):
+    unicode_escape = codecs.getdecoder('unicode_escape')
     return re.sub(
         r'\\U[0-9a-fA-F]{8}',
-        lambda m: m.group(0).decode('unicode-escape'), s)
+        lambda m: unicode_escape(m.group(0))[0],
+        s)

 try:
     struct.pack(u'!I', 0)
"""
)


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


IMPORT_ONLY_PATCH = normalize_patch_blank_context(
    r"""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2,6 +2,7 @@
 # -*- coding: utf-8 -*-

 import calendar
+import codecs
 import contextlib
 import ctypes
 import datetime
"""
)


RAW_ESCAPE_PATCH = normalize_patch_blank_context(
    r"""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1263,9 +1263,9 @@ class PagedList(object):


 def uppercase_escape(s):
     return re.sub(
         r'\\U[0-9a-fA-F]{8}',
-        lambda m: m.group(0).decode('unicode-escape'), s)
+        lambda m: m.group(0), s)

 try:
     struct.pack(u'!I', 0)
"""
)


def base_record() -> dict[str, Any]:
    issue = "uppercase_escape should decode uppercase Unicode escape sequences on Python 3."
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_37",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_uppercase_escpae.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_37_uppercase_escape.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_37_uppercase_escape.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_37",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_uppercase_escpae"],
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
            "bugsinpy_youtube-dl_37__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 37 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_37__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_37__import_only_codecs",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            IMPORT_ONLY_PATCH,
            "Partial negative: imports codecs but leaves the Python 3 str.decode call unchanged.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_37__raw_escape_passthrough",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            RAW_ESCAPE_PATCH,
            "Partial negative: avoids the exception but returns the raw escape sequence.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_37 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
