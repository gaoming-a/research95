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
@@ -1101,7 +1101,7 @@ def unified_timestamp(date_str, day_first=True):

     date_str = date_str.replace(',', ' ')

-    pm_delta = datetime.timedelta(hours=12 if re.search(r'(?i)PM', date_str) else 0)
+    pm_delta = 12 if re.search(r'(?i)PM', date_str) else 0
     timezone, date_str = extract_timezone(date_str)

     # Remove AM/PM + timezone
@@ -1109,13 +1109,13 @@ def unified_timestamp(date_str, day_first=True):

     for expression in date_formats(day_first):
         try:
-            dt = datetime.datetime.strptime(date_str, expression) - timezone + pm_delta
+            dt = datetime.datetime.strptime(date_str, expression) - timezone + datetime.timedelta(hours=pm_delta)
             return calendar.timegm(dt.timetuple())
         except ValueError:
             pass
     timetuple = email.utils.parsedate_tz(date_str)
     if timetuple:
-        return calendar.timegm(timetuple.timetuple())
+        return calendar.timegm(timetuple) + pm_delta * 3600


 def determine_ext(url, default_ext='unknown_video'):
""")


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


PARTIAL_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1101,7 +1101,7 @@ def unified_timestamp(date_str, day_first=True):

     date_str = date_str.replace(',', ' ')

-    pm_delta = datetime.timedelta(hours=12 if re.search(r'(?i)PM', date_str) else 0)
+    pm_delta = 12 if re.search(r'(?i)PM', date_str) else 0
     timezone, date_str = extract_timezone(date_str)

     # Remove AM/PM + timezone
@@ -1109,7 +1109,7 @@ def unified_timestamp(date_str, day_first=True):

     for expression in date_formats(day_first):
         try:
-            dt = datetime.datetime.strptime(date_str, expression) - timezone + pm_delta
+            dt = datetime.datetime.strptime(date_str, expression) - timezone + datetime.timedelta(hours=pm_delta)
             return calendar.timegm(dt.timetuple())
         except ValueError:
             pass
""")


IRRELEVANT_PATCH = normalize_patch_blank_context("""--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1121,6 +1121,7 @@ def unified_timestamp(date_str, day_first=True):

 def determine_ext(url, default_ext='unknown_video'):
+    url = url
     if url is None:
         return default_ext
     guess = url.partition('?')[0].rpartition('.')[2]
     if re.match(r'^[A-Za-z0-9]+$', guess):
""")


def base_record() -> dict[str, Any]:
    issue = (
        "unified_timestamp should correctly add PM offsets for both strptime "
        "parsed timestamps and email parsedate_tz fallback timestamps."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_5",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_unified_timestamps.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_5_unified_timestamps.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_5_unified_timestamps.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_5",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_unified_timestamps"],
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
            "bugsinpy_youtube-dl_5__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 5 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_5__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_5__strptime_pm_only",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: fixes strptime PM handling but leaves parsedate_tz PM fallback incorrect.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_5__irrelevant_noop_assignment",
            "irrelevant_patch",
            "irrelevant_or_noop",
            "manual_irrelevant_diff_against_buggy_checkout",
            IRRELEVANT_PATCH,
            "Irrelevant negative: changes no unified_timestamp behavior.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_5 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
