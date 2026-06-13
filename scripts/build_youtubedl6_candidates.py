from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BLANK_CONTEXT = " \n"


OFFICIAL_PATCH = (
    "--- a/youtube_dl/utils.py\n"
    "+++ b/youtube_dl/utils.py\n"
    "@@ -1976,7 +1976,7 @@ def match_filter_func(filter_str):\n"
    + BLANK_CONTEXT
    + " def parse_dfxp_time_expr(time_expr):\n"
    "     if not time_expr:\n"
    "-        return 0.0\n"
    "+        return\n"
    + BLANK_CONTEXT
    + "     mobj = re.match(r'^(?P<time_offset>\\d+(?:\\.\\d+)?)s?$', time_expr)\n"
    "     if mobj:\n"
    "@@ -2020,10 +2020,15 @@ def dfxp2srt(dfxp_data):\n"
    "         raise ValueError('Invalid dfxp/TTML subtitle')\n"
    + BLANK_CONTEXT
    + "     for para, index in zip(paras, itertools.count(1)):\n"
    "-        begin_time = parse_dfxp_time_expr(para.attrib['begin'])\n"
    "+        begin_time = parse_dfxp_time_expr(para.attrib.get('begin'))\n"
    "         end_time = parse_dfxp_time_expr(para.attrib.get('end'))\n"
    "+        dur = parse_dfxp_time_expr(para.attrib.get('dur'))\n"
    "+        if begin_time is None:\n"
    "+            continue\n"
    "         if not end_time:\n"
    "-            end_time = begin_time + parse_dfxp_time_expr(para.attrib['dur'])\n"
    "+            if not dur:\n"
    "+                continue\n"
    "+            end_time = begin_time + dur\n"
    "         out.append('%d\\n%s --> %s\\n%s\\n\\n' % (\n"
    "             index,\n"
    "             srt_subtitles_timecode(begin_time),\n"
)


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


PARTIAL_PATCH = (
    "--- a/youtube_dl/utils.py\n"
    "+++ b/youtube_dl/utils.py\n"
    "@@ -1976,7 +1976,7 @@ def match_filter_func(filter_str):\n"
    + BLANK_CONTEXT
    + " def parse_dfxp_time_expr(time_expr):\n"
    "     if not time_expr:\n"
    "-        return 0.0\n"
    "+        return\n"
    + BLANK_CONTEXT
    + "     mobj = re.match(r'^(?P<time_offset>\\d+(?:\\.\\d+)?)s?$', time_expr)\n"
    "     if mobj:\n"
)


IRRELEVANT_PATCH = """--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -1960,6 +1960,7 @@ def match_filter_func(filter_str):
 def match_filter_func(filter_str):
     def _match_func(info_dict):
+        info_dict = info_dict
         if match_str(filter_str, info_dict):
             return None
         else:
             video_title = info_dict.get('title', info_dict.get('id', 'video'))
"""


def base_record() -> dict[str, Any]:
    issue = (
        "DFXP/TTML subtitle time parsing should keep missing or invalid time "
        "expressions invalid and ignore invalid subtitle paragraphs instead of "
        "coercing them to zero or raising KeyError."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_6",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_parse_dfxp_time_expr.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_6_dfxp_time.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_6_dfxp_time.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_6",
        "touched_files": ["youtube_dl/utils.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_parse_dfxp_time_expr"],
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
            "bugsinpy_youtube-dl_6__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 6 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_6__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_6__parse_empty_only",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            PARTIAL_PATCH,
            "Partial negative: fixes empty time parsing but still raises on invalid DFXP paragraphs.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_6__irrelevant_noop_assignment",
            "irrelevant_patch",
            "irrelevant_or_noop",
            "manual_irrelevant_diff_against_buggy_checkout",
            IRRELEVANT_PATCH,
            "Irrelevant negative: changes no DFXP time parsing behavior.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_6 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
