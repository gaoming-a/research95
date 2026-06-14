from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


FFMPEG_FIX = """diff --git a/youtube_dl/postprocessor/ffmpeg.py b/youtube_dl/postprocessor/ffmpeg.py
index 51256a3fb..f71d413b5 100644
--- a/youtube_dl/postprocessor/ffmpeg.py
+++ b/youtube_dl/postprocessor/ffmpeg.py
@@ -585,7 +585,7 @@ class FFmpegSubtitlesConvertorPP(FFmpegPostProcessor):
                 dfxp_file = old_file
                 srt_file = subtitles_filename(filename, lang, 'srt')
@@BLANK@@
-                with io.open(dfxp_file, 'rt', encoding='utf-8') as f:
+                with open(dfxp_file, 'rb') as f:
                     srt_data = dfxp2srt(f.read())
@@BLANK@@
                 with io.open(srt_file, 'wt', encoding='utf-8') as f:
""".replace("@@BLANK@@", " ")


UTILS_FIX = """diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py
index 9e4492d40..b724e0b70 100644
--- a/youtube_dl/utils.py
+++ b/youtube_dl/utils.py
@@ -2572,14 +2572,18 @@ def srt_subtitles_timecode(seconds):
@@BLANK@@
@@BLANK@@
 def dfxp2srt(dfxp_data):
+    '''
+    @param dfxp_data A bytes-like object containing DFXP data
+    @returns A unicode object containing converted SRT data
+    '''
     LEGACY_NAMESPACES = (
-        ('http://www.w3.org/ns/ttml', [
-            'http://www.w3.org/2004/11/ttaf1',
-            'http://www.w3.org/2006/04/ttaf1',
-            'http://www.w3.org/2006/10/ttaf1',
+        (b'http://www.w3.org/ns/ttml', [
+            b'http://www.w3.org/2004/11/ttaf1',
+            b'http://www.w3.org/2006/04/ttaf1',
+            b'http://www.w3.org/2006/10/ttaf1',
         ]),
-        ('http://www.w3.org/ns/ttml#styling', [
-            'http://www.w3.org/ns/ttml#style',
+        (b'http://www.w3.org/ns/ttml#styling', [
+            b'http://www.w3.org/ns/ttml#style',
         ]),
     )
@@BLANK@@
@@ -2674,7 +2678,7 @@ def dfxp2srt(dfxp_data):
         for ns in v:
             dfxp_data = dfxp_data.replace(ns, k)
@@BLANK@@
-    dfxp = compat_etree_fromstring(dfxp_data.encode('utf-8'))
+    dfxp = compat_etree_fromstring(dfxp_data)
     out = []
     paras = dfxp.findall(_x('.//ttml:p')) or dfxp.findall('.//p')
@@BLANK@@
""".replace("@@BLANK@@", " ")


OFFICIAL_PATCH = UTILS_FIX + FFMPEG_FIX


EMPTY_DIFF = "diff --git a/youtube_dl/utils.py b/youtube_dl/utils.py\n"


def base_record() -> dict[str, Any]:
    issue = (
        "DFXP/TTML subtitle conversion should operate on subtitle bytes so XML "
        "encodings such as UTF-16 are preserved through dfxp2srt and the ffmpeg "
        "subtitle converter."
    )
    visible_context = "\n".join(
        [
            "Project: youtube-dl",
            "Task: bugsinpy_youtube-dl_16",
            "Candidate: patch proposal without ground-truth label.",
            "Touched files: youtube_dl/utils.py; youtube_dl/postprocessor/ffmpeg.py",
            f"Behavior summary: {issue}",
            "Visible regression hint: test.test_utils.TestUtil.test_dfxp2srt.",
        ]
    )
    return {
        "base_version": "buggy",
        "context_mode": "patch_diff",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "hidden_oracles": ["scripts/oracles/youtubedl_16_dfxp2srt_bytes.py"],
        "issue_summary": issue,
        "label_confidence": "high",
        "oracle_command": "python scripts/oracles/youtubedl_16_dfxp2srt_bytes.py",
        "project": "youtube-dl",
        "source": "bugsinpy",
        "task_id": "bugsinpy_youtube-dl_16",
        "touched_files": ["youtube_dl/utils.py", "youtube_dl/postprocessor/ffmpeg.py"],
        "visible_context": visible_context,
        "visible_tests": ["test.test_utils.TestUtil.test_dfxp2srt"],
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
            "bugsinpy_youtube-dl_16__reference_fix",
            "correct_reference",
            "correct",
            "buggy_fixed_unified_diff",
            OFFICIAL_PATCH,
            "Reference source diff from the BugsInPy youtube-dl bug 16 patch.",
        ),
        candidate(
            "candidate_0002",
            "bugsinpy_youtube-dl_16__empty_diff_control",
            "buggy_noop",
            "incorrect",
            "empty_diff_against_buggy_checkout",
            EMPTY_DIFF,
            "Negative control represented by an empty source diff against the buggy checkout.",
        ),
        candidate(
            "candidate_0003",
            "bugsinpy_youtube-dl_16__utils_only_bytes_fix",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            UTILS_FIX,
            "Partial negative: dfxp2srt accepts bytes but the subtitle converter still reads DFXP as UTF-8 text.",
        ),
        candidate(
            "candidate_0004",
            "bugsinpy_youtube-dl_16__ffmpeg_only_binary_read",
            "partial_fix",
            "partial",
            "manual_partial_diff_against_buggy_checkout",
            FFMPEG_FIX,
            "Partial negative: the converter reads bytes but dfxp2srt still rejects bytes-like DFXP data.",
        ),
    ]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build youtube-dl_16 admission candidate records.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    records = build_candidates()
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidate_count": len(records), "out": args.out}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
