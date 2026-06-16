from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REFERENCE_PATCH = """--- a/thefuck/rules/pip_unknown_command.py
+++ b/thefuck/rules/pip_unknown_command.py
@@ -12,8 +12,8 @@ def match(command):
 
 
 def get_new_command(command):
-    broken_cmd = re.findall(r'ERROR: unknown command \\"([a-z]+)\\"',
+    broken_cmd = re.findall(r'ERROR: unknown command "([^"]+)"',
                             command.output)[0]
-    new_cmd = re.findall(r'maybe you meant \\"([a-z]+)\\"', command.output)[0]
+    new_cmd = re.findall(r'maybe you meant "([^"]+)"', command.output)[0]
 
     return replace_argument(command.script, broken_cmd, new_cmd)
"""


EMPTY_DIFF = "diff --git a/thefuck/rules/pip_unknown_command.py b/thefuck/rules/pip_unknown_command.py\n"


PARTIAL_PATCH = """--- a/thefuck/rules/pip_unknown_command.py
+++ b/thefuck/rules/pip_unknown_command.py
@@ -14,6 +14,6 @@ def get_new_command(command):
 def get_new_command(command):
     broken_cmd = re.findall(r'ERROR: unknown command \\"([a-z]+)\\"',
                             command.output)[0]
-    new_cmd = re.findall(r'maybe you meant \\"([a-z]+)\\"', command.output)[0]
+    new_cmd = re.findall(r'maybe you meant "([^"]+)"', command.output)[0]
 
     return replace_argument(command.script, broken_cmd, new_cmd)
"""


REGRESSION_PATCH = """--- a/thefuck/rules/pip_unknown_command.py
+++ b/thefuck/rules/pip_unknown_command.py
@@ -8,12 +8,11 @@ def match(command):
 def match(command):
     return ('pip' in command.script and
-            'unknown command' in command.output and
-            'maybe you meant' in command.output)
+            'unknown command' in command.output)
 
 
 def get_new_command(command):
-    broken_cmd = re.findall(r'ERROR: unknown command \\"([a-z]+)\\"',
+    broken_cmd = re.findall(r'ERROR: unknown command "([^"]+)"',
                             command.output)[0]
-    new_cmd = re.findall(r'maybe you meant \\"([a-z]+)\\"', command.output)[0]
+    new_cmd = re.findall(r'maybe you meant "([^"]+)"', command.output)[0]
 
     return replace_argument(command.script, broken_cmd, new_cmd)
"""


def base_record() -> dict[str, Any]:
    issue = (
        "pip unknown-command suggestions should preserve command names that "
        "contain non-letter characters such as plus signs."
    )
    visible_context = "\n".join(
        [
            "Project: thefuck",
            "Task: bugsinpy_thefuck_1",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: thefuck/rules/pip_unknown_command.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: tests/rules/test_pip_unknown_command.py::test_get_new_command",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/thefuck_1_pip_unknown_command.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/thefuck_1_pip_unknown_command.py",
        "project": "thefuck",
        "source": "bugsinpy",
        "task_id": "bugsinpy_thefuck_1",
        "touched_files": ["thefuck/rules/pip_unknown_command.py"],
        "visible_context": visible_context,
        "visible_tests": ["tests/rules/test_pip_unknown_command.py::test_get_new_command"],
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
            "bugsinpy_thefuck_1__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_source_diff",
            REFERENCE_PATCH,
            "Reference source diff from the BugsInPy thefuck bug 1 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_thefuck_1__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_thefuck_1__suggested_regex_only",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: expands only the suggested-command regex while the broken command regex remains letter-only.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_thefuck_1__broad_match_regression",
            "regression_patch",
            "regression",
            "manual_regression_diff_against_buggy_checkout",
            REGRESSION_PATCH,
            "Regression negative: fixes get_new_command but broadens match to outputs without recommendations.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build thefuck_1 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
