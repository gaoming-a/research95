from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_patch_blank_context(diff_text: str) -> str:
    lines = diff_text.strip("\n").splitlines()
    return "\n".join(" " if line == "" else line for line in lines) + "\n"


OFFICIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/jsinterp.py
+++ b/youtube_dl/jsinterp.py
@@ -198,12 +198,12 @@ class JSInterpreter(object):
             return opfunc(x, y)

        m = re.match(
-            r'^(?P<func>%s)\\((?P<args>[a-zA-Z0-9_$,]+)\\)$' % _NAME_RE, expr)
+            r'^(?P<func>%s)\\((?P<args>[a-zA-Z0-9_$,]*)\\)$' % _NAME_RE, expr)
         if m:
             fname = m.group('func')
             argvals = tuple([
                 int(v) if v.isdigit() else local_vars[v]
-                for v in m.group('args').split(',')])
+                for v in m.group('args').split(',')]) if len(m.group('args')) > 0 else tuple()
             if fname not in self._functions:
                 self._functions[fname] = self.extract_function(fname)
             return self._functions[fname](argvals)
""")


EMPTY_DIFF = "diff --git a/youtube_dl/jsinterp.py b/youtube_dl/jsinterp.py\n"


PARTIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/jsinterp.py
+++ b/youtube_dl/jsinterp.py
@@ -198,7 +198,7 @@ class JSInterpreter(object):
             return opfunc(x, y)

        m = re.match(
-            r'^(?P<func>%s)\\((?P<args>[a-zA-Z0-9_$,]+)\\)$' % _NAME_RE, expr)
+            r'^(?P<func>%s)\\((?P<args>[a-zA-Z0-9_$,]*)\\)$' % _NAME_RE, expr)
         if m:
             fname = m.group('func')
             argvals = tuple([
""")


IRRELEVANT_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/jsinterp.py
+++ b/youtube_dl/jsinterp.py
@@ -195,4 +195,5 @@ class JSInterpreter(object):
             if abort:
                 raise ExtractorError(
                     'Premature right-side return of %s in %r' % (op, expr))
+            expr = expr
             return opfunc(x, y)
""")


def base_record() -> dict[str, Any]:
    issue = (
        "JSInterpreter should support calling JavaScript functions with no "
        "arguments from inside interpreted expressions."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_4",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/jsinterp.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_jsinterp.TestJSInterpreter.test_call.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_4_jsinterp_call.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_4_jsinterp_call.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_4",
        "touched_files": ["youtube_dl/jsinterp.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_jsinterp.TestJSInterpreter.test_call"],
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
            "bugsinpy_youtube-dl_4__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 4 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_4__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_4__regex_only_empty_args",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: matches empty argument calls but still tries to resolve an empty local variable.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_4__irrelevant_noop_assignment",
            "irrelevant_patch",
            "irrelevant_or_noop",
            "manual_irrelevant_diff_against_buggy_checkout",
            IRRELEVANT_PATCH,
            "Irrelevant negative: changes no JS function-call behavior.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_4 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
