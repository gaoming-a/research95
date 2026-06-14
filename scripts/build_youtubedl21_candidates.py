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
@@ -1748,10 +1748,15 @@ def base_url(url):


 def urljoin(base, path):
+    if isinstance(path, bytes):
+        path = path.decode('utf-8')
     if not isinstance(path, compat_str) or not path:
         return None
     if re.match(r'^(?:https?:)?//', path):
         return path
-    if not isinstance(base, compat_str) or not re.match(r'^(?:https?:)?//', base):
+    if isinstance(base, bytes):
+        base = base.decode('utf-8')
+    if not isinstance(base, compat_str) or not re.match(
+            r'^(?:https?:)?//', base):
         return None
     return compat_urlparse.urljoin(base, path)
"""
)


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


PATH_ONLY_PATCH = normalize_patch_blank_context(
    """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1748,6 +1748,8 @@ def base_url(url):


 def urljoin(base, path):
+    if isinstance(path, bytes):
+        path = path.decode('utf-8')
     if not isinstance(path, compat_str) or not path:
         return None
     if re.match(r'^(?:https?:)?//', path):
"""
)


BASE_ONLY_PATCH = normalize_patch_blank_context(
    """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1753,6 +1753,9 @@ def urljoin(base, path):
         return None
     if re.match(r'^(?:https?:)?//', path):
         return path
-    if not isinstance(base, compat_str) or not re.match(r'^(?:https?:)?//', base):
+    if isinstance(base, bytes):
+        base = base.decode('utf-8')
+    if not isinstance(base, compat_str) or not re.match(
+            r'^(?:https?:)?//', base):
         return None
     return compat_urlparse.urljoin(base, path)
"""
)


def base_record() -> dict[str, Any]:
    issue = "urljoin should accept UTF-8 bytes for both base URL and path inputs."
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_21",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_urljoin.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_21_urljoin_bytes.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_21_urljoin_bytes.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_21",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_urljoin"],
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
            "bugsinpy_youtube-dl_21__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 21 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_21__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_21__path_only_bytes",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PATH_ONLY_PATCH,
            "Partial negative: decodes bytes paths but still rejects bytes base URLs.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_21__base_only_bytes",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            BASE_ONLY_PATCH,
            "Partial negative: decodes bytes base URLs but still rejects bytes paths.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_21 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
