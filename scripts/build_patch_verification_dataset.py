from __future__ import annotations

import argparse
import difflib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SOURCE_BUGS = [
    {
        "task_id": "bugsinpy_httpie_1",
        "project": "httpie",
        "touched_files": ["httpie/downloads.py"],
        "issue_summary": "download filename collision handling should create a unique filename",
        "visible_tests": ["tests/test_downloads.py::TestDownloadUtils::test_unique_filename"],
        "hidden_oracles": [
            "scripts/oracles/httpie_1_unique_filename.py",
            "scripts/oracles/httpie_1_errno_fallback.py",
        ],
        "oracle_command": "python scripts/oracles/httpie_1_unique_filename.py",
    },
    {
        "task_id": "bugsinpy_httpie_2",
        "project": "httpie",
        "touched_files": ["httpie/client.py"],
        "issue_summary": "max redirects should be assigned to the requests session before execution",
        "visible_tests": ["tests/test_redirects.py::TestRedirects::test_max_redirects"],
        "hidden_oracles": ["scripts/oracles/httpie_2_max_redirects.py"],
        "oracle_command": "python scripts/oracles/httpie_2_max_redirects.py",
    },
    {
        "task_id": "bugsinpy_httpie_3",
        "project": "httpie",
        "touched_files": ["httpie/sessions.py"],
        "issue_summary": "session header updates should ignore explicitly unset None values",
        "visible_tests": ["tests/test_sessions.py::TestSession::test_download_in_session"],
        "hidden_oracles": ["scripts/oracles/httpie_3_session_headers.py"],
        "oracle_command": "python scripts/oracles/httpie_3_session_headers.py",
    },
    {
        "task_id": "bugsinpy_httpie_4",
        "project": "httpie",
        "touched_files": ["httpie/models.py"],
        "issue_summary": "a lowercase user-supplied host header should not be duplicated",
        "visible_tests": ["tests/test_regressions.py::test_Host_header_overwrite"],
        "hidden_oracles": ["scripts/oracles/httpie_4_host_header.py"],
        "oracle_command": "python scripts/oracles/httpie_4_host_header.py",
    },
    {
        "task_id": "bugsinpy_httpie_5",
        "project": "httpie",
        "touched_files": ["httpie/cli.py"],
        "issue_summary": "escaped long separators should be parsed as part of the key",
        "visible_tests": ["tests/tests.py::TestItemParsing::test_escape_longsep"],
        "hidden_oracles": ["scripts/oracles/httpie_5_escape_long_separator.py"],
        "oracle_command": "python scripts/oracles/httpie_5_escape_long_separator.py",
    },
    {
        "task_id": "bugsinpy_luigi_3",
        "project": "luigi",
        "touched_files": ["luigi/parameter.py"],
        "issue_summary": "TupleParameter should round-trip JSON serialized scalar tuples as tuples",
        "visible_tests": ["test/parameter_test.py::TestSerializeTupleParameter::testSerialize"],
        "hidden_oracles": ["scripts/oracles/luigi_3_tuple_parameter.py"],
        "oracle_command": "python scripts/oracles/luigi_3_tuple_parameter.py",
    },
    {
        "task_id": "bugsinpy_luigi_4",
        "project": "luigi",
        "touched_files": ["luigi/contrib/redshift.py"],
        "issue_summary": "Redshift COPY generation should tolerate columns=None",
        "visible_tests": [
            "test/contrib/redshift_test.py::TestS3CopyToTable::test_s3_copy_with_nonetype_columns"
        ],
        "hidden_oracles": ["scripts/oracles/luigi_4_redshift_none_columns.py"],
        "oracle_command": "python scripts/oracles/luigi_4_redshift_none_columns.py",
    },
    {
        "task_id": "bugsinpy_cookiecutter_1",
        "project": "cookiecutter",
        "touched_files": ["cookiecutter/generate.py"],
        "issue_summary": "JSON context files containing non-ASCII characters should be decoded as UTF-8",
        "visible_tests": ["tests/test_generate_context.py::test_generate_context_decodes_non_ascii_chars"],
        "hidden_oracles": ["scripts/oracles/cookiecutter_1_utf8_context.py"],
        "oracle_command": "python scripts/oracles/cookiecutter_1_utf8_context.py",
    },
    {
        "task_id": "bugsinpy_cookiecutter_2",
        "project": "cookiecutter",
        "touched_files": ["cookiecutter/hooks.py"],
        "issue_summary": "all matching pre- or post-generation hook scripts should be executed, not only the first match",
        "visible_tests": ["tests/test_hooks.py::TestExternalHooks::test_run_hook"],
        "hidden_oracles": ["scripts/oracles/cookiecutter_2_multiple_hooks.py"],
        "oracle_command": "python scripts/oracles/cookiecutter_2_multiple_hooks.py",
    },
    {
        "task_id": "bugsinpy_cookiecutter_3",
        "project": "cookiecutter",
        "touched_files": ["cookiecutter/prompt.py"],
        "issue_summary": "choice prompts should not let Click duplicate the choices already rendered in Cookiecutter's custom prompt text",
        "visible_tests": ["tests/test_read_user_choice.py::test_click_invocation"],
        "hidden_oracles": ["scripts/oracles/cookiecutter_3_prompt_show_choices.py"],
        "oracle_command": "python scripts/oracles/cookiecutter_3_prompt_show_choices.py",
    },
    {
        "task_id": "bugsinpy_tqdm_9",
        "project": "tqdm",
        "touched_files": ["tqdm/_tqdm.py"],
        "issue_summary": "SI-scaled meter totals should round at display precision boundaries and manual tqdm instances should report total length",
        "visible_tests": [
            "tqdm/tests/tests_tqdm.py::test_si_format",
            "tqdm/tests/tests_tqdm.py::test_update",
        ],
        "hidden_oracles": ["scripts/oracles/tqdm_9_si_len.py"],
        "oracle_command": "python scripts/oracles/tqdm_9_si_len.py",
    },
    {
        "task_id": "bugsinpy_PySnooper_1",
        "project": "PySnooper",
        "touched_files": ["pysnooper/tracer.py", "pysnooper/pycompat.py"],
        "issue_summary": "Snooper log files and decoded source lines should preserve non-ASCII text as UTF-8",
        "visible_tests": ["tests/test_chinese.py::test_chinese"],
        "hidden_oracles": ["scripts/oracles/pysnooper_1_utf8_log.py"],
        "oracle_command": "python scripts/oracles/pysnooper_1_utf8_log.py",
    },
]

TASK_PARTIAL_ALLOWLIST = {
    "bugsinpy_tqdm_9": {
        "first_hunk_only",
        "missing_change_1",
        "missing_change_4",
        "split_replace_1_3",
    },
    "bugsinpy_PySnooper_1": {
        "first_hunk_only",
        "missing_change_2",
        "missing_change_3",
    },
}


REQUIRED_CANDIDATE_FIELDS = {
    "patch_id",
    "model_candidate_id",
    "task_id",
    "project",
    "source",
    "candidate_type",
    "expected_outcome",
    "base_version",
    "patch_text",
    "touched_files",
    "context_mode",
    "visible_context",
    "issue_summary",
    "visible_tests",
    "hidden_oracles",
    "oracle_command",
    "oracle_workdir",
    "evidence_sources",
    "label_confidence",
    "construction_notes",
    "patch_materialization",
}


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def contains_label_token(text: str, token: str) -> bool:
    escaped = re.escape(token)
    pattern = rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])"
    return re.search(pattern, text) is not None


def build_visible_context(source_bug: dict[str, Any], touched_files: list[str]) -> str:
    files = ", ".join(touched_files)
    tests = ", ".join(source_bug["visible_tests"])
    return (
        f"Project: {source_bug['project']}\n"
        f"Task: {source_bug['task_id']}\n"
        f"Candidate: patch proposal without ground-truth label.\n"
        f"Touched files: {files}\n"
        f"Behavior summary: {source_bug['issue_summary']}.\n"
        f"Visible regression hint: {tests}."
    )


def source_root_default() -> Path:
    return Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"


def checkout_file(source_root: Path, source_bug: dict[str, Any], version: str, file_path: str) -> Path:
    bug_dir = source_bug["task_id"].replace("bugsinpy_", "")
    return source_root / bug_dir / version / source_bug["project"] / file_path


def unified_diff(source_root: Path, source_bug: dict[str, Any], file_path: str) -> str:
    buggy_lines, fixed_lines = read_buggy_fixed_lines(source_root, source_bug, file_path)
    return unified_diff_from_lines(file_path, buggy_lines, fixed_lines, source_bug["task_id"])


def read_buggy_fixed_lines(
    source_root: Path, source_bug: dict[str, Any], file_path: str
) -> tuple[list[str], list[str]]:
    buggy_path = checkout_file(source_root, source_bug, "buggy", file_path)
    fixed_path = checkout_file(source_root, source_bug, "fixed", file_path)
    if not buggy_path.exists():
        raise FileNotFoundError(f"missing buggy source file for {source_bug['task_id']}: {buggy_path}")
    if not fixed_path.exists():
        raise FileNotFoundError(f"missing fixed source file for {source_bug['task_id']}: {fixed_path}")

    buggy_lines = buggy_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    fixed_lines = fixed_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    return buggy_lines, fixed_lines


def unified_diff_from_lines(
    file_path: str, buggy_lines: list[str], candidate_lines: list[str], task_id: str
) -> str:
    diff_lines = difflib.unified_diff(
        buggy_lines,
        candidate_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        n=3,
    )
    diff_text = "".join(diff_lines)
    if not diff_text.strip():
        raise ValueError(f"empty diff for {task_id}:{file_path}")
    return diff_text


def empty_diff(file_path: str) -> str:
    return f"diff --git a/{file_path} b/{file_path}\n"


def comment_only_diff(source_root: Path, source_bug: dict[str, Any], file_path: str) -> str:
    buggy_lines, _ = read_buggy_fixed_lines(source_root, source_bug, file_path)
    candidate_lines = list(buggy_lines)
    insert_at = 0
    while insert_at < len(candidate_lines) and (
        candidate_lines[insert_at].startswith("#!") or "coding" in candidate_lines[insert_at]
    ):
        insert_at += 1
    candidate_lines.insert(insert_at, "# Candidate review note: source formatting touched.\n")
    return unified_diff_from_lines(file_path, buggy_lines, candidate_lines, source_bug["task_id"])


def first_hunk_only(diff_text: str) -> str | None:
    lines = diff_text.splitlines(keepends=True)
    hunk_indexes = [index for index, line in enumerate(lines) if line.startswith("@@")]
    if len(hunk_indexes) < 2:
        return None
    header = lines[: hunk_indexes[0]]
    first_hunk = lines[hunk_indexes[0] : hunk_indexes[1]]
    return "".join(header + first_hunk)


def changed_opcodes(buggy_lines: list[str], fixed_lines: list[str]) -> list[tuple[str, int, int, int, int]]:
    matcher = difflib.SequenceMatcher(a=buggy_lines, b=fixed_lines)
    return [opcode for opcode in matcher.get_opcodes() if opcode[0] != "equal"]


def apply_all_except_one_change(
    buggy_lines: list[str],
    fixed_lines: list[str],
    omitted_change_index: int,
) -> list[str]:
    output: list[str] = []
    for change_index, (tag, old_start, old_end, new_start, new_end) in enumerate(
        changed_opcodes(buggy_lines, fixed_lines)
    ):
        previous_new_end = changed_opcodes(buggy_lines, fixed_lines)[change_index - 1][4] if change_index else 0
        output.extend(fixed_lines[previous_new_end:new_start])
        if change_index == omitted_change_index:
            output.extend(buggy_lines[old_start:old_end])
        else:
            output.extend(fixed_lines[new_start:new_end])
    opcodes = changed_opcodes(buggy_lines, fixed_lines)
    output.extend(fixed_lines[opcodes[-1][4] :])
    return output


def build_partial_missing_change_diffs(
    source_root: Path,
    source_bug: dict[str, Any],
    file_path: str,
) -> list[dict[str, str]]:
    buggy_lines, fixed_lines = read_buggy_fixed_lines(source_root, source_bug, file_path)
    opcodes = changed_opcodes(buggy_lines, fixed_lines)
    if len(opcodes) < 2:
        return []

    records: list[dict[str, str]] = []
    for omitted_index in range(len(opcodes)):
        candidate_lines = apply_all_except_one_change(buggy_lines, fixed_lines, omitted_index)
        patch_text = unified_diff_from_lines(file_path, buggy_lines, candidate_lines, source_bug["task_id"])
        records.append(
            {
                "suffix": f"missing_change_{omitted_index + 1}",
                "patch_text": patch_text,
                "materialization": "reference_diff_with_one_change_omitted",
                "notes": (
                    "Difficult negative generated by applying the retained reference diff except "
                    f"change block {omitted_index + 1}."
                ),
            }
        )
    return records


def build_split_replace_partial_diffs(
    source_root: Path,
    source_bug: dict[str, Any],
    file_path: str,
) -> list[dict[str, str]]:
    buggy_lines, fixed_lines = read_buggy_fixed_lines(source_root, source_bug, file_path)
    opcodes = changed_opcodes(buggy_lines, fixed_lines)
    records: list[dict[str, str]] = []
    for opcode_index, (tag, old_start, old_end, new_start, new_end) in enumerate(opcodes):
        old_chunk = buggy_lines[old_start:old_end]
        new_chunk = fixed_lines[new_start:new_end]
        if tag != "replace" or len(old_chunk) != len(new_chunk) or len(new_chunk) < 2:
            continue
        for line_index in range(len(new_chunk)):
            candidate_lines = list(fixed_lines)
            candidate_lines[new_start + line_index] = old_chunk[line_index]
            patch_text = unified_diff_from_lines(file_path, buggy_lines, candidate_lines, source_bug["task_id"])
            records.append(
                {
                    "suffix": f"split_replace_{opcode_index + 1}_{line_index + 1}",
                    "patch_text": patch_text,
                    "materialization": "reference_replace_with_one_line_reverted",
                    "notes": (
                        "Difficult negative generated from a retained replace block with one line "
                        f"reverted to the buggy version: block {opcode_index + 1}, line {line_index + 1}."
                    ),
                }
            )
    return records


def build_task_specific_negative_diffs(
    source_root: Path,
    source_bug: dict[str, Any],
    file_path: str,
) -> list[dict[str, str]]:
    if source_bug["task_id"] == "bugsinpy_cookiecutter_1":
        buggy_lines, _ = read_buggy_fixed_lines(source_root, source_bug, file_path)
        target = "        with open(context_file) as file_handle:\n"
        replacement = "        with open(context_file, encoding='ascii') as file_handle:\n"
        if target not in buggy_lines:
            raise ValueError(f"expected Cookiecutter context-open line not found in {file_path}")

        candidate_lines = [replacement if line == target else line for line in buggy_lines]
        return [
            {
                "suffix": "wrong_ascii_encoding",
                "patch_text": unified_diff_from_lines(
                    file_path,
                    buggy_lines,
                    candidate_lines,
                    source_bug["task_id"],
                ),
                "materialization": "task_specific_wrong_encoding_diff",
                "notes": (
                    "Difficult negative for the single-line Cookiecutter UTF-8 bug: the candidate "
                    "adds an explicit encoding argument but chooses ASCII rather than UTF-8."
                ),
            }
        ]
    if source_bug["task_id"] == "bugsinpy_cookiecutter_3":
        buggy_lines, _ = read_buggy_fixed_lines(source_root, source_bug, file_path)
        target = "        prompt, type=click.Choice(choices), default=default\n"
        replacement = "        prompt, type=click.Choice(choices), default=default, show_choices=True\n"
        if target not in buggy_lines:
            raise ValueError(f"expected Cookiecutter click.prompt line not found in {file_path}")

        candidate_lines = [replacement if line == target else line for line in buggy_lines]
        return [
            {
                "suffix": "wrong_show_choices_true",
                "patch_text": unified_diff_from_lines(
                    file_path,
                    buggy_lines,
                    candidate_lines,
                    source_bug["task_id"],
                ),
                "materialization": "task_specific_wrong_prompt_visibility_diff",
                "notes": (
                    "Difficult negative for the single-line Cookiecutter prompt bug: the candidate "
                    "touches the relevant Click prompt argument but explicitly keeps choice rendering enabled."
                ),
            }
        ]
    return []


def select_source_bugs(task_ids: list[str] | None) -> list[dict[str, Any]]:
    if not task_ids:
        return list(SOURCE_BUGS)
    known = {source_bug["task_id"]: source_bug for source_bug in SOURCE_BUGS}
    missing = sorted(set(task_ids) - known.keys())
    if missing:
        raise ValueError(f"unknown task_id values: {missing}")
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    for task_id in task_ids:
        if task_id in seen:
            continue
        selected.append(known[task_id])
        seen.add(task_id)
    return selected


def build_reference_diffs(source_root: Path, source_bugs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    reference_diffs: dict[str, dict[str, Any]] = {}
    for source_bug in source_bugs:
        diff_text = "".join(unified_diff(source_root, source_bug, file_path) for file_path in source_bug["touched_files"])
        reference_diffs[source_bug["task_id"]] = {
            "patch_text": diff_text,
            "touched_files": list(source_bug["touched_files"]),
            "hunk_count": diff_text.count("\n@@"),
        }
    return reference_diffs


def build_candidate(
    source_bug: dict[str, Any],
    suffix: str,
    candidate_type: str,
    expected_outcome: str,
    patch_text: str,
    touched_files: list[str],
    construction_notes: str,
    patch_materialization: str,
) -> dict[str, Any]:
    patch_id = f"{source_bug['task_id']}__{suffix}"
    return {
        "patch_id": patch_id,
        "model_candidate_id": "",
        "task_id": source_bug["task_id"],
        "project": source_bug["project"],
        "source": "bugsinpy",
        "candidate_type": candidate_type,
        "expected_outcome": expected_outcome,
        "base_version": "buggy",
        "patch_text": patch_text,
        "touched_files": touched_files,
        "context_mode": "patch_diff",
        "visible_context": build_visible_context(source_bug, touched_files),
        "issue_summary": source_bug["issue_summary"],
        "visible_tests": source_bug["visible_tests"],
        "hidden_oracles": source_bug["hidden_oracles"],
        "oracle_command": source_bug["oracle_command"],
        "oracle_workdir": f"data/patch_verification/workdirs/{patch_id}",
        "evidence_sources": ["regression_oracle", "patch_diff"],
        "label_confidence": "high",
        "construction_notes": construction_notes,
        "patch_materialization": patch_materialization,
    }


def build_candidates(source_root: Path, source_bugs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reference_diffs = build_reference_diffs(source_root, source_bugs)
    candidates: list[dict[str, Any]] = []
    for source_bug in source_bugs:
        reference = reference_diffs[source_bug["task_id"]]
        candidates.append(
            build_candidate(
                source_bug=source_bug,
                suffix="reference_fix",
                candidate_type="correct_reference",
                expected_outcome="correct",
                patch_text=reference["patch_text"],
                touched_files=reference["touched_files"],
                construction_notes="Reference diff generated by comparing the retained buggy and fixed checkouts.",
                patch_materialization="buggy_fixed_unified_diff",
            )
        )
        candidates.append(
            build_candidate(
                source_bug=source_bug,
                suffix="empty_diff_control",
                candidate_type="buggy_noop",
                expected_outcome="incorrect",
                patch_text=empty_diff(source_bug["touched_files"][0]),
                touched_files=source_bug["touched_files"],
                construction_notes="Negative control represented by an empty source diff against the buggy checkout.",
                patch_materialization="empty_diff_against_buggy_checkout",
            )
        )
        comment_diff = comment_only_diff(source_root, source_bug, source_bug["touched_files"][0])
        candidates.append(
            build_candidate(
                source_bug=source_bug,
                suffix="comment_only_patch",
                candidate_type="irrelevant_patch",
                expected_outcome="irrelevant_or_noop",
                patch_text=comment_diff,
                touched_files=source_bug["touched_files"],
                construction_notes="Negative control using an applicable comment-only source diff.",
                patch_materialization="local_comment_only_unified_diff",
            )
        )

        partial_text = first_hunk_only(reference["patch_text"])
        partial_texts: set[str] = set()
        allowlist = TASK_PARTIAL_ALLOWLIST.get(source_bug["task_id"])
        if partial_text and (allowlist is None or "first_hunk_only" in allowlist):
            partial_texts.add(partial_text)
            candidates.append(
                build_candidate(
                    source_bug=source_bug,
                    suffix="first_hunk_only",
                    candidate_type="partial_fix",
                    expected_outcome="partial",
                    patch_text=partial_text,
                    touched_files=reference["touched_files"],
                    construction_notes=(
                        "Difficult negative built from the first hunk of a multi-hunk reference diff; "
                        "the remaining reference behavior is intentionally absent."
                    ),
                    patch_materialization="first_hunk_of_reference_unified_diff",
                )
            )
        for partial_record in (
            build_partial_missing_change_diffs(source_root, source_bug, reference["touched_files"][0])
            + build_split_replace_partial_diffs(source_root, source_bug, reference["touched_files"][0])
            + build_task_specific_negative_diffs(source_root, source_bug, reference["touched_files"][0])
        ):
            if allowlist is not None and partial_record["suffix"] not in allowlist:
                continue
            if partial_record["patch_text"] in partial_texts:
                continue
            partial_texts.add(partial_record["patch_text"])
            candidates.append(
                build_candidate(
                    source_bug=source_bug,
                    suffix=partial_record["suffix"],
                    candidate_type="partial_fix",
                    expected_outcome="partial",
                    patch_text=partial_record["patch_text"],
                    touched_files=reference["touched_files"],
                    construction_notes=partial_record["notes"],
                    patch_materialization=partial_record["materialization"],
                )
            )
    return candidates


def validate_candidate(candidate: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_CANDIDATE_FIELDS - candidate.keys())
    if missing:
        raise ValueError(f"{candidate.get('patch_id', '<unknown>')} missing fields: {missing}")
    visible = json.dumps(
        {
            "visible_context": candidate["visible_context"],
            "patch_text": candidate["patch_text"],
            "issue_summary": candidate["issue_summary"],
        },
        ensure_ascii=False,
    )
    forbidden = [
        candidate["candidate_type"],
        "correct_reference",
        "buggy_noop",
        "irrelevant_patch",
        "partial_fix",
        "reference_fix",
        "empty_diff_control",
        "comment_only_patch",
        "first_hunk_only",
        "noop",
        "No-op",
        "irrelevant",
        "Irrelevant",
        "hidden oracle passes",
        "hidden oracle fails",
    ]
    for token in forbidden:
        if token and contains_label_token(visible, token):
            raise ValueError(f"{candidate['patch_id']} leaks label token in visible context: {token}")


def build_evidence_packet(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": candidate["model_candidate_id"],
        "task_id": candidate["task_id"],
        "project": candidate["project"],
        "task_summary": candidate["issue_summary"],
        "visible_context": candidate["visible_context"],
        "patch_text": candidate["patch_text"],
        "touched_files": candidate["touched_files"],
        "visible_tests": candidate["visible_tests"],
        "available_evidence_sources": candidate["evidence_sources"],
        "has_hidden_oracle": bool(candidate["hidden_oracles"]),
        "evidence_packet_version": "patch_evidence_packet_v1",
        "label_leakage_guard": "ground-truth labels and oracle results are intentionally omitted",
    }


def build_baseline_outputs(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    baselines = [
        ("accept_all", "no_api_accept_all"),
        ("reject_all", "no_api_reject_all"),
        ("oracle_upper_bound", "no_api_oracle_upper_bound"),
    ]
    for candidate in candidates:
        for verifier_id, condition in baselines:
            if verifier_id == "accept_all":
                decision = "accept"
                claim = "Baseline accepts every candidate without evidence."
            elif verifier_id == "reject_all":
                decision = "reject"
                claim = "Baseline rejects every candidate without evidence."
            else:
                decision = "accept" if candidate["expected_outcome"] == "correct" else "reject"
                claim = "Oracle upper bound uses hidden labels and is not model capability."
            records.append(
                {
                    "patch_id": candidate["patch_id"],
                    "verifier_id": verifier_id,
                    "condition": condition,
                    "decision": decision,
                    "confidence": 1.0,
                    "claims": [
                        {
                            "claim_id": f"{candidate['patch_id']}__{verifier_id}__claim_001",
                            "claim": claim,
                            "evidence": ["deterministic_no_api_baseline"],
                            "evidence_status": "baseline_rule",
                        }
                    ],
                    "raw_response_path": None,
                    "cost_usd": 0.0,
                    "invalid_reason": None,
                }
            )
    return records


def build_summary(
    candidates: list[dict[str, Any]],
    verifier_outputs: list[dict[str, Any]],
    run_id: str,
) -> dict[str, Any]:
    difficult_negative_types = {"partial_fix", "overfitted_fix", "test_passing_wrong"}
    difficult_negative_count = sum(
        1 for candidate in candidates if candidate["candidate_type"] in difficult_negative_types
    )
    difficult_negative_ratio = difficult_negative_count / len(candidates) if candidates else 0.0
    return {
        "run_id": run_id,
        "candidate_count": len(candidates),
        "verifier_output_count": len(verifier_outputs),
        "project_counts": dict(sorted(Counter(candidate["project"] for candidate in candidates).items())),
        "candidate_type_counts": dict(
            sorted(Counter(candidate["candidate_type"] for candidate in candidates).items())
        ),
        "expected_outcome_counts": dict(
            sorted(Counter(candidate["expected_outcome"] for candidate in candidates).items())
        ),
        "patch_materialization_counts": dict(
            sorted(Counter(candidate["patch_materialization"] for candidate in candidates).items())
        ),
        "difficult_negative_count": difficult_negative_count,
        "difficult_negative_ratio": round(difficult_negative_ratio, 4),
        "api_readiness": {
            "real_patch_diffs_available": True,
            "min_candidate_count_met": len(candidates) >= 20,
            "difficult_negative_ratio_met": difficult_negative_ratio >= 0.30,
            "ready": len(candidates) >= 20 and difficult_negative_ratio >= 0.30,
        },
        "verifier_counts": dict(sorted(Counter(record["verifier_id"] for record in verifier_outputs).items())),
        "api_calls": 0,
        "notes": (
            "No-API pilot generated from retained real-bug oracle metadata and "
            "buggy/fixed checkout diffs. API readiness still depends on the "
            "difficult-negative ratio."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the first no-API patch-verification pilot dataset."
    )
    parser.add_argument(
        "--out-dir",
        default="outputs/patch_verification_pilot_001",
        help="Output directory for candidates, evidence packets, baselines, and summary.",
    )
    parser.add_argument(
        "--source-workspace-root",
        default=str(source_root_default()),
        help="Root containing BugsInPy buggy/fixed checkouts used to materialize patch diffs.",
    )
    parser.add_argument(
        "--no-baselines",
        action="store_true",
        help="Do not emit deterministic no-API verifier_outputs.jsonl baselines.",
    )
    parser.add_argument(
        "--run-id",
        default="patch_verification_pilot_001",
        help="Run identifier recorded in dataset_summary.json.",
    )
    parser.add_argument(
        "--task-id",
        action="append",
        help="Task id to include. Repeat to build a filtered Stage A/B dataset. Defaults to all built-in tasks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source_root = Path(args.source_workspace_root)
    if not source_root.exists():
        raise FileNotFoundError(f"source workspace root does not exist: {source_root}")

    source_bugs = select_source_bugs(args.task_id)
    candidates = build_candidates(source_root, source_bugs)
    for index, candidate in enumerate(candidates, start=1):
        candidate["model_candidate_id"] = f"candidate_{index:04d}"
    for candidate in candidates:
        validate_candidate(candidate)

    evidence_packets = [build_evidence_packet(candidate) for candidate in candidates]
    verifier_outputs = [] if args.no_baselines else build_baseline_outputs(candidates)
    summary = build_summary(candidates, verifier_outputs, args.run_id)

    write_jsonl(out_dir / "candidates.jsonl", candidates)
    write_jsonl(out_dir / "evidence_packets.jsonl", evidence_packets)
    if verifier_outputs:
        write_jsonl(out_dir / "verifier_outputs.jsonl", verifier_outputs)
    write_json(out_dir / "dataset_summary.json", summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
