from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


TEST_PATH_MARKERS = ("/test", "/tests/", "\\test", "\\tests\\")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build review-ready task/generation/execution JSONL files from validated real-bug metadata."
    )
    parser.add_argument("--metadata", required=True, help="Validated real-bug metadata JSONL.")
    parser.add_argument("--root", default=".", help="Repository root used to resolve relative workdirs.")
    parser.add_argument("--out-tasks", required=True)
    parser.add_argument("--out-generations", required=True)
    parser.add_argument("--out-executions", required=True)
    parser.add_argument("--max-file-chars", type=int, default=12000)
    parser.add_argument(
        "--source-context",
        choices=["files", "patch_hunks"],
        default="files",
        help="Use whole modified files or patch-hunk excerpts as submitted code context.",
    )
    parser.add_argument("--hunk-context-lines", type=int, default=30)
    parser.add_argument(
        "--context-mode",
        choices=[
            "full_test",
            "summary_only",
            "source_only",
            "calibrated_full_test",
            "evidence_summary_only",
            "agent_context_summary",
        ],
        default="full_test",
        help="Reviewer-visible task context for prompt-context ablations.",
    )
    parser.add_argument("--include-fixed-controls", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    metadata = read_jsonl(Path(args.metadata))
    tasks: list[dict[str, Any]] = []
    generations: list[dict[str, Any]] = []
    executions: list[dict[str, Any]] = []

    for record in metadata:
        bug_id = required_str(record, "bug_id")
        bug_patch = resolve_path(root, record.get("bug_patch"))
        source_files = source_files_from_patch(bug_patch)
        if not source_files:
            raise SystemExit(f"No non-test source files found in patch for {bug_id}")
        patch_hunks = patch_hunks_from_patch(bug_patch)

        test_file = str(record.get("test_file") or "")
        visible_test = read_project_file(root, record.get("buggy_workdir"), test_file, args.max_file_chars)
        task = {
            "task_id": bug_id,
            "bug_id": bug_id,
            "source": record.get("source"),
            "project": record.get("project"),
            "language": record.get("language", "python"),
            "bug_source": "real_engineering_bug",
            "prompt_context_mode": args.context_mode,
            "task_prompt_version": task_prompt_version(args.context_mode),
            "prompt": build_review_task_prompt(
                record=record,
                source_files=source_files,
                visible_test=visible_test,
                context_mode=args.context_mode,
                source_context_mode=args.source_context,
                hunk_context_lines=args.hunk_context_lines,
            ),
            "visible_test_file": test_file,
            "visible_regression_test_command": first_command(record),
            "hidden_tests": [],
        }
        if args.context_mode == "agent_context_summary":
            task["agent_context"] = build_agent_context(
                record=record,
                source_files=source_files,
                source_context=args.source_context,
                hunk_context_lines=args.hunk_context_lines,
            )
        tasks.append(task)

        buggy_code = build_code_context(
            root=root,
            workdir=record.get("buggy_workdir"),
            source_files=source_files,
            max_file_chars=args.max_file_chars,
            source_context=args.source_context,
            patch_hunks=patch_hunks,
            side="buggy",
            hunk_context_lines=args.hunk_context_lines,
        )
        fixed_code = build_code_context(
            root=root,
            workdir=record.get("fixed_workdir"),
            source_files=source_files,
            max_file_chars=args.max_file_chars,
            source_context=args.source_context,
            patch_hunks=patch_hunks,
            side="fixed",
            hunk_context_lines=args.hunk_context_lines,
        )

        buggy_generation_id = f"{bug_id}__buggy"
        generations.append(
            {
                "generation_id": buggy_generation_id,
                "task_id": bug_id,
                "generator_model": "real_bug_buggy",
                "model_id": "real_world_buggy_version",
                "bug_source": "real_engineering_bug",
                "variant": "buggy",
                "code": buggy_code,
                "source_files": source_files,
                "source_context": args.source_context,
                "prompt_version": task_prompt_version(args.context_mode),
            }
        )
        executions.append(
            {
                "generation_id": buggy_generation_id,
                "task_id": bug_id,
                "generator_model": "real_bug_buggy",
                "model_id": "real_world_buggy_version",
                "bug_source": "real_engineering_bug",
                "variant": "buggy",
                "passed": False,
                "oracle": "validated_regression_test",
            }
        )

        if args.include_fixed_controls:
            fixed_generation_id = f"{bug_id}__fixed_control"
            generations.append(
                {
                    "generation_id": fixed_generation_id,
                    "task_id": bug_id,
                    "generator_model": "real_bug_fixed_control",
                    "model_id": "real_world_fixed_version",
                    "bug_source": "real_engineering_bug",
                    "variant": "fixed_control",
                    "code": fixed_code,
                    "source_files": source_files,
                    "source_context": args.source_context,
                    "prompt_version": task_prompt_version(args.context_mode),
                }
            )
            executions.append(
                {
                    "generation_id": fixed_generation_id,
                    "task_id": bug_id,
                    "generator_model": "real_bug_fixed_control",
                    "model_id": "real_world_fixed_version",
                    "bug_source": "real_engineering_bug",
                    "variant": "fixed_control",
                    "passed": True,
                    "oracle": "validated_regression_test",
                }
            )

    assert_unique(tasks, "task_id")
    assert_unique(generations, "generation_id")
    assert_unique(executions, "generation_id")
    write_jsonl(Path(args.out_tasks), tasks)
    write_jsonl(Path(args.out_generations), generations)
    write_jsonl(Path(args.out_executions), executions)
    print(
        json.dumps(
            {
                "tasks": len(tasks),
                "generations": len(generations),
                "executions": len(executions),
                "buggy_generations": sum(1 for row in generations if row.get("variant") == "buggy"),
                "fixed_controls": sum(1 for row in generations if row.get("variant") == "fixed_control"),
            },
            indent=2,
        )
    )


def build_review_task_prompt(
    record: dict[str, Any],
    source_files: list[str],
    visible_test: str,
    context_mode: str,
    source_context_mode: str,
    hunk_context_lines: int,
) -> str:
    source_file_list = "\n".join(f"- {path}" for path in source_files)
    test_file = str(record.get("test_file") or "unknown")
    command = first_command(record)
    base = (
        "You are reviewing a real Python project change context.\n"
        "Determine whether the submitted project code contains a defect.\n"
        "Do not assume whether the submitted code is buggy or fixed. The execution outcome and labels are hidden.\n\n"
        f"Project: {record.get('project')}\n"
        f"Source: {record.get('source')} real engineering bug sample\n"
    )
    source_context = (
        "Submitted source files to inspect:\n"
        f"{source_file_list}\n"
    )
    if context_mode == "full_test":
        return (
            base
            + "Review context mode: full visible regression test.\n"
            + "Assess the source code relative to the regression test below, but do not infer labels from the test name.\n"
            + f"Regression test command: {command}\n"
            + f"Regression test file: {test_file}\n"
            + source_context
            + "\nVisible regression test code:\n"
            + f"{visible_test}"
        )
    if context_mode == "calibrated_full_test":
        return (
            base
            + "Review context mode: calibrated full visible regression test.\n"
            + "Assess the source code relative to the regression test below, but apply a conservative defect threshold.\n"
            + "Report bug_found=true only when the submitted code contains a concrete defect that is directly supported by the source and would plausibly violate the stated behavior.\n"
            + "Report bug_found=false for speculative risks, style issues, design preferences, incomplete evidence, or concerns that are not tied to a concrete failing behavior.\n"
            + "In the explanation, clearly distinguish concrete defect evidence from speculation.\n"
            + f"Regression test command: {command}\n"
            + f"Regression test file: {test_file}\n"
            + source_context
            + "\nVisible regression test code:\n"
            + f"{visible_test}"
        )
    if context_mode == "summary_only":
        return (
            base
            + "Review context mode: regression summary only.\n"
            + "The full regression-test code is hidden. Use the test name and command only as a behavioral hint.\n"
            + f"Regression test command: {command}\n"
            + f"Regression test file: {test_file}\n"
            + f"Regression behavior hint: the submitted code should satisfy the behavior exercised by {test_target(command)}.\n"
            + source_context
        )
    if context_mode == "evidence_summary_only":
        return (
            base
            + "Review context mode: evidence-constrained regression summary only.\n"
            + "The full regression-test code is hidden. Use the test name and command only as a behavioral hint, not as proof that a bug exists.\n"
            + "Report bug_found=true only when the submitted code excerpt contains concrete executable evidence of a correctness defect.\n"
            + "Report bug_found=false when the concern is speculative, depends on missing context, describes a plausible but unproven edge case, or is only suggested by the regression-test name.\n"
            + "If the excerpt is insufficient to prove the defect, set bug_found=false and state that the evidence is insufficient in the explanation.\n"
            + "Do not report excerpt boundaries, missing surrounding code, or style/design preferences as bugs.\n"
            + f"Regression test command: {command}\n"
            + f"Regression test file: {test_file}\n"
            + f"Regression behavior hint: the submitted code should satisfy the behavior exercised by {test_target(command)}.\n"
            + source_context
        )
    if context_mode == "agent_context_summary":
        agent_context = format_agent_context(
            build_agent_context(
                record=record,
                source_files=source_files,
                source_context=source_context_mode,
                hunk_context_lines=hunk_context_lines,
            )
        )
        return (
            base
            + "Review context mode: agent-style contextual review.\n"
            + "You are joining a coding-agent workflow as an independent reviewer after an implementation attempt.\n"
            + "The submitted artifact may be defect-containing or a passing reference/control version. The execution outcome and labels are hidden.\n"
            + "Use the agent context below to understand the workflow, but do not treat the regression-test name or the existence of a prior task as proof that a bug exists.\n"
            + "Report bug_found=true only when the supplied source excerpt and workflow context contain concrete executable evidence of a correctness defect.\n"
            + "Report bug_found=false when the concern is speculative, depends on missing context, describes a plausible but unproven edge case, or only restates the target behavior.\n"
            + "If the supplied context is insufficient to prove a defect, set bug_found=false and say the evidence is insufficient.\n\n"
            + "Agent workflow context:\n"
            + f"{agent_context}\n\n"
            + source_context
        )
    if context_mode == "source_only":
        return (
            base
            + "Review context mode: source context only.\n"
            + "Regression tests and execution outcomes are hidden. Review only the submitted source context.\n"
            + source_context
        )
    raise ValueError(f"Unknown context mode: {context_mode}")


def task_prompt_version(context_mode: str) -> str:
    if context_mode == "calibrated_full_test":
        return "real_bug_review_task_calibrated_v1"
    if context_mode == "evidence_summary_only":
        return "real_bug_review_task_evidence_summary_v1"
    if context_mode == "agent_context_summary":
        return "real_bug_review_task_agent_context_v1"
    if context_mode in {"full_test", "summary_only", "source_only"}:
        return "real_bug_review_task_context_modes_v1"
    raise ValueError(f"Unknown context mode: {context_mode}")


def build_agent_context(
    record: dict[str, Any],
    source_files: list[str],
    source_context: str,
    hunk_context_lines: int,
) -> dict[str, Any]:
    command = first_command(record)
    return {
        "role": "independent reviewer joining after a coding-agent implementation attempt",
        "project": record.get("project"),
        "target_behavior": test_target(command),
        "regression_command": command,
        "regression_file": str(record.get("test_file") or "unknown"),
        "submitted_context_scope": source_context,
        "patch_hunk_context_lines": hunk_context_lines if source_context == "patch_hunks" else None,
        "source_files": source_files,
        "hidden_information": [
            "whether the submitted artifact is the defect-containing version or the reference/control version",
            "the local regression-test execution outcome",
            "the historical patch label",
        ],
        "decision_rule": [
            "Use workflow context to understand the target behavior.",
            "Do not infer a bug from the existence of a regression command.",
            "Return no bug when the excerpt does not prove the defect.",
        ],
    }


def format_agent_context(agent_context: dict[str, Any]) -> str:
    lines = [
        f"- Reviewer role: {agent_context['role']}",
        f"- Project: {agent_context['project']}",
        f"- Target behavior: {agent_context['target_behavior']}",
        f"- Regression command: {agent_context['regression_command']}",
        f"- Regression file: {agent_context['regression_file']}",
        f"- Submitted context scope: {agent_context['submitted_context_scope']}",
    ]
    if agent_context.get("patch_hunk_context_lines") is not None:
        lines.append(f"- Patch-hunk surrounding lines: {agent_context['patch_hunk_context_lines']}")
    lines.append("- Source files:")
    lines.extend(f"  - {path}" for path in agent_context["source_files"])
    lines.append("- Hidden from reviewer:")
    lines.extend(f"  - {item}" for item in agent_context["hidden_information"])
    lines.append("- Decision rule:")
    lines.extend(f"  - {item}" for item in agent_context["decision_rule"])
    return "\n".join(lines)


def test_target(command: str) -> str:
    if "::" in command:
        return command.rsplit(" ", 1)[-1]
    return command or "the named regression test"


def build_code_context(
    root: Path,
    workdir: Any,
    source_files: list[str],
    max_file_chars: int,
    source_context: str,
    patch_hunks: dict[str, list[dict[str, int]]],
    side: str,
    hunk_context_lines: int,
) -> str:
    blocks = []
    for source_file in source_files:
        if source_context == "files":
            blocks.append(read_project_file(root, workdir, source_file, max_file_chars))
        elif source_context == "patch_hunks":
            blocks.append(
                read_patch_hunk_context(
                    root=root,
                    workdir=workdir,
                    relative_path=source_file,
                    hunks=patch_hunks.get(source_file, []),
                    side=side,
                    context_lines=hunk_context_lines,
                )
            )
        else:
            raise ValueError(f"Unknown source context: {source_context}")
    return "\n\n".join(blocks)


def read_project_file(root: Path, workdir: Any, relative_path: str, max_file_chars: int) -> str:
    if not relative_path:
        return "# File: <missing>\n"
    base = resolve_path(root, workdir)
    path = base.joinpath(*relative_path.replace("\\", "/").split("/"))
    if not path.exists():
        raise SystemExit(f"Missing project file: {relative_path} under {workdir}")
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_file_chars:
        text = text[:max_file_chars] + "\n# ... truncated ...\n"
    return f"# File: {relative_path}\n{text}"


def read_patch_hunk_context(
    root: Path,
    workdir: Any,
    relative_path: str,
    hunks: list[dict[str, int]],
    side: str,
    context_lines: int,
) -> str:
    if not hunks:
        raise SystemExit(f"Missing patch hunks for source file: {relative_path}")
    base = resolve_path(root, workdir)
    path = base.joinpath(*relative_path.replace("\\", "/").split("/"))
    if not path.exists():
        raise SystemExit(f"Missing project file: {relative_path} under {workdir}")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    ranges: list[tuple[int, int]] = []
    for hunk in hunks:
        start_key = "old_start" if side == "buggy" else "new_start"
        count_key = "old_count" if side == "buggy" else "new_count"
        start = max(1, hunk[start_key] - context_lines)
        end = min(len(lines), hunk[start_key] + max(hunk[count_key], 1) + context_lines - 1)
        ranges.append((start, end))
    merged = merge_ranges(ranges)
    blocks = [f"# File: {relative_path}"]
    for start, end in merged:
        blocks.append(f"# Excerpt: lines {start}-{end} around patch hunk")
        for line_number in range(start, end + 1):
            blocks.append(f"{line_number}: {lines[line_number - 1]}")
    return "\n".join(blocks) + "\n"


def source_files_from_patch(patch_path: Path) -> list[str]:
    if not patch_path.exists():
        raise SystemExit(f"Missing bug patch: {patch_path}")
    files: list[str] = []
    for line in patch_path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"diff --git a/(.+?) b/(.+)$", line)
        if not match:
            continue
        candidate = match.group(2)
        if is_test_path(candidate):
            continue
        if candidate not in files:
            files.append(candidate)
    return files


def patch_hunks_from_patch(patch_path: Path) -> dict[str, list[dict[str, int]]]:
    hunks: dict[str, list[dict[str, int]]] = {}
    current_file = ""
    for line in patch_path.read_text(encoding="utf-8", errors="replace").splitlines():
        file_match = re.match(r"diff --git a/(.+?) b/(.+)$", line)
        if file_match:
            current_file = file_match.group(2)
            continue
        if not current_file or is_test_path(current_file):
            continue
        hunk_match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if hunk_match:
            old_start = int(hunk_match.group(1))
            old_count = int(hunk_match.group(2) or "1")
            new_start = int(hunk_match.group(3))
            new_count = int(hunk_match.group(4) or "1")
            hunks.setdefault(current_file, []).append(
                {
                    "old_start": old_start,
                    "old_count": old_count,
                    "new_start": new_start,
                    "new_count": new_count,
                }
            )
    return hunks


def merge_ranges(ranges: list[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(ranges):
        if not merged or start > merged[-1][1] + 1:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def is_test_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    name = normalized.rsplit("/", 1)[-1]
    return any(marker in normalized for marker in TEST_PATH_MARKERS) or name.startswith("test_")


def first_command(record: dict[str, Any]) -> str:
    commands = record.get("run_test_commands") or []
    if isinstance(commands, list) and commands:
        return str(commands[0])
    return str(record.get("buggy_test_command") or "")


def required_str(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value:
        raise SystemExit(f"Missing required string field: {key}")
    return value


def resolve_path(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value:
        raise SystemExit("Missing path value")
    path = Path(value)
    if path.is_absolute():
        return path
    return root / path


def assert_unique(records: list[dict[str, Any]], key: str) -> None:
    seen: set[str] = set()
    for record in records:
        value = str(record[key])
        if value in seen:
            raise SystemExit(f"Duplicate {key}: {value}")
        seen.add(value)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            records.append(value)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


if __name__ == "__main__":
    main()
