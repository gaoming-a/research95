from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from cross_review.env import load_env_file  # noqa: E402
from cross_review.jsonl import write_jsonl  # noqa: E402
from cross_review.openrouter import DeepSeekClient, QwenClient, redact_sensitive_text  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_patch_verification_dataset as dataset_builder  # noqa: E402


PROMPT_VERSION = "agent_edit_plan_v1"
DEFAULT_TASK_IDS = [
    "bugsinpy_httpie_1",
    "bugsinpy_httpie_2",
    "bugsinpy_httpie_3",
    "bugsinpy_httpie_4",
    "bugsinpy_httpie_5",
]
FORBIDDEN_PROMPT_TOKENS = [
    "expected_outcome",
    "candidate_type",
    "hidden_oracles",
    "oracle_command",
    "oracle_workdir",
    "construction_notes",
    "fixed checkout",
    "reference diff",
    "oracle_passed",
]


def source_root_default() -> Path:
    return Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def checkout_root(source_root: Path, source_bug: dict[str, Any]) -> Path:
    bug_dir = source_bug["task_id"].replace("bugsinpy_", "")
    return source_root / bug_dir / "buggy" / source_bug["project"]


def remove_tree(path: Path) -> None:
    def make_writable_and_retry(func: Any, failed_path: str, _exc_info: Any) -> None:
        os.chmod(failed_path, stat.S_IWRITE)
        func(failed_path)

    shutil.rmtree(path, onerror=make_writable_and_retry)


def copy_buggy_checkout(source_root: Path, source_bug: dict[str, Any], workdir: Path) -> None:
    source = checkout_root(source_root, source_bug)
    if not source.exists():
        raise FileNotFoundError(f"missing buggy checkout: {source}")
    if workdir.exists():
        remove_tree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    git_dir = source / ".git"
    if not git_dir.exists():
        raise FileNotFoundError(f"missing .git directory in buggy checkout: {source}")
    shutil.copytree(git_dir, workdir / ".git")
    for file_path in source_bug["touched_files"]:
        rel = Path(file_path)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe touched file path: {file_path}")
        src = source / rel
        dst = workdir / rel
        if not src.exists():
            raise FileNotFoundError(f"missing touched file in buggy checkout: {file_path}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def read_buggy_file(source_root: Path, source_bug: dict[str, Any], file_path: str, max_chars: int) -> str:
    path = dataset_builder.checkout_file(source_root, source_bug, "buggy", file_path)
    if not path.exists():
        raise FileNotFoundError(f"missing buggy source file for {source_bug['task_id']}: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n# ... truncated by generator input budget ...\n"


def render_prompt(source_root: Path, source_bug: dict[str, Any], variant_index: int, max_source_chars: int) -> str:
    file_blocks = []
    for file_path in source_bug["touched_files"]:
        file_blocks.append(
            "\n".join(
                [
                    f"### File: {file_path}",
                    "```python",
                    read_buggy_file(source_root, source_bug, file_path, max_source_chars),
                    "```",
                ]
            )
        )
    prompt = "\n".join(
        [
            "You are acting as an AI coding agent editing a copied Python checkout.",
            "",
            "Return exactly one JSON object and no surrounding Markdown.",
            "",
            "JSON schema:",
            "{",
            '  "edits": [',
            '    {"file_path": "relative/path.py", "find": "exact old source snippet", "replace": "new source snippet"}',
            "  ],",
            '  "rationale": "short explanation of the intended fix"',
            "}",
            "",
            "Rules:",
            "- Produce exact search/replace edits against the buggy source shown below.",
            "- The find value must be copied character-for-character from one contiguous span in the buggy source.",
            "- Preserve indentation, spaces, quotes, and backslashes exactly in each find value.",
            "- Do not summarize, reformat, or normalize the find value.",
            "- Keep each find snippet specific enough to occur in the file exactly once when possible.",
            "- Do not output a unified diff.",
            "- Use only the visible issue summary, visible test hint, touched file names, and buggy source below.",
            "- Do not assume hidden tests, oracle results, reference patches, fixed code, or post-fix code.",
            "- Do not include prose outside the JSON object.",
            "",
            f"Task id: {source_bug['task_id']}",
            f"Patch variant requested: {variant_index}",
            f"Project: {source_bug['project']}",
            f"Issue summary: {source_bug['issue_summary']}",
            f"Touched files: {json.dumps(source_bug['touched_files'], ensure_ascii=False)}",
            f"Visible test hint: {json.dumps(source_bug['visible_tests'], ensure_ascii=False)}",
            "",
            "Buggy source:",
            "",
            "\n\n".join(file_blocks),
        ]
    )
    check_prompt_boundary(prompt)
    return prompt


def check_prompt_boundary(prompt: str) -> None:
    hits = [token for token in FORBIDDEN_PROMPT_TOKENS if token in prompt]
    if hits:
        raise ValueError(f"agent prompt contains forbidden evaluator tokens: {hits}")


def raw_response_path(out_dir: Path, task_id: str, variant_index: int, model: str, attempt: int = 1) -> Path:
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    suffix = "" if attempt == 1 else f"__attempt_{attempt:02d}"
    return out_dir / "raw" / safe_model / f"{task_id}__agent_patch_{variant_index:02d}{suffix}.json"


def next_raw_response_path(out_dir: Path, task_id: str, variant_index: int, model: str) -> Path:
    attempt = 1
    while raw_response_path(out_dir, task_id, variant_index, model, attempt).exists():
        attempt += 1
    return raw_response_path(out_dir, task_id, variant_index, model, attempt)


def write_raw(path: Path, response: dict[str, Any]) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(content, encoding="utf-8")
    return {"path": path.as_posix(), "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}


def parse_edit_plan(response: dict[str, Any]) -> tuple[list[dict[str, str]], str]:
    parsed = extract_json_object(response_text(response))
    edits_raw = parsed.get("edits", [])
    if not isinstance(edits_raw, list) or not edits_raw:
        raise ValueError("edit plan has no edits")
    edits: list[dict[str, str]] = []
    for index, edit in enumerate(edits_raw, start=1):
        if not isinstance(edit, dict):
            raise ValueError(f"edit {index} is not an object")
        file_path = str(edit.get("file_path", "")).strip()
        find = str(edit.get("find", ""))
        replace = str(edit.get("replace", ""))
        if not file_path or not find:
            raise ValueError(f"edit {index} missing file_path or find")
        edits.append({"file_path": file_path, "find": find, "replace": replace})
    return edits, str(parsed.get("rationale", "")).strip()


def apply_edit_plan(workdir: Path, edits: list[dict[str, str]]) -> list[dict[str, Any]]:
    applied: list[dict[str, Any]] = []
    for edit in edits:
        rel = Path(edit["file_path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError(f"unsafe edit path: {edit['file_path']}")
        path = workdir / rel
        if not path.exists():
            raise FileNotFoundError(f"edit target does not exist: {edit['file_path']}")
        original = path.read_text(encoding="utf-8", errors="replace")
        occurrences = original.count(edit["find"])
        if occurrences < 1:
            raise ValueError(f"find snippet not found in {edit['file_path']}")
        updated = original.replace(edit["find"], edit["replace"], 1)
        path.write_text(updated, encoding="utf-8", newline="\n")
        applied.append({"file_path": edit["file_path"], "find_occurrences": occurrences})
    return applied


def run_git_diff(workdir: Path, touched_files: list[str]) -> str:
    command = ["git", "diff", "--", *touched_files]
    completed = subprocess.run(
        command,
        cwd=str(workdir),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git diff failed: {completed.stderr[-1000:]}")
    diff_text = completed.stdout
    if "@@" not in diff_text:
        raise ValueError("edit plan produced no unified-diff hunks")
    return diff_text


def build_candidate(
    source_bug: dict[str, Any],
    patch_text: str,
    patch_id: str,
    model_candidate_id: str,
    model: str,
    api_provider: str,
    run_id: str,
    raw: dict[str, str],
    rationale: str,
    applied_edits: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "patch_id": patch_id,
        "model_candidate_id": model_candidate_id,
        "task_id": source_bug["task_id"],
        "project": source_bug["project"],
        "source": f"{api_provider}_agent_edit",
        "candidate_type": "model_generated_patch",
        "expected_outcome": "incorrect",
        "base_version": "buggy",
        "patch_text": patch_text,
        "touched_files": source_bug["touched_files"],
        "context_mode": "agent_edit_plan_git_diff",
        "visible_context": dataset_builder.build_visible_context(source_bug, source_bug["touched_files"]),
        "issue_summary": source_bug["issue_summary"],
        "visible_tests": source_bug["visible_tests"],
        "hidden_oracles": source_bug["hidden_oracles"],
        "oracle_command": source_bug["oracle_command"],
        "oracle_workdir": f"data/patch_verification/workdirs/{patch_id}",
        "evidence_sources": ["patch_diff", "visible_test_hint", "agent_edit_plan"],
        "label_confidence": "pending_validation",
        "construction_notes": (
            f"Agent-style AI-generated patch from {model} in run {run_id}. "
            "The model produced edit snippets; the script applied them to a copied buggy checkout "
            "and exported patch_text with git diff."
        ),
        "patch_materialization": "agent_edit_plan_git_diff",
        "generation_model": model,
        "generation_prompt_version": PROMPT_VERSION,
        "generation_run_id": run_id,
        "generation_rationale": rationale,
        "agent_applied_edits": applied_edits,
        "raw_generation_response_path": raw["path"],
        "raw_generation_response_sha256": raw["sha256"],
    }


def build_evidence_packet(candidate: dict[str, Any]) -> dict[str, Any]:
    packet = dataset_builder.build_evidence_packet(candidate)
    packet["evidence_packet_version"] = "agent_patch_evidence_packet_v1"
    packet["available_evidence_sources"] = ["patch_diff", "visible_test_hint"]
    packet["label_leakage_guard"] = (
        "Agent edit metadata, evaluator labels, hidden oracle paths, and oracle results are omitted"
    )
    return packet


def persist(out_dir: Path, candidates: list[dict[str, Any]], prompt_manifest: list[dict[str, Any]]) -> None:
    write_jsonl(out_dir / "prompt_manifest.jsonl", prompt_manifest)
    if candidates:
        write_jsonl(out_dir / "candidates.pending.jsonl", candidates)
        write_jsonl(out_dir / "evidence_packets.pending.jsonl", [build_evidence_packet(candidate) for candidate in candidates])


def upsert_prompt_manifest(prompt_manifest: list[dict[str, Any]], prompt_record: dict[str, Any]) -> None:
    for index, record in enumerate(prompt_manifest):
        if (
            record.get("task_id") == prompt_record["task_id"]
            and int(record.get("variant_index", 0)) == int(prompt_record["variant_index"])
        ):
            prompt_manifest[index] = {**record, **prompt_record, "resumed_prompt_record": True}
            return
    prompt_manifest.append(prompt_record)


def build_summary(args: argparse.Namespace, candidates: list[dict[str, Any]], prompt_manifest: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "run_id": args.run_id,
        "model": args.model,
        "api_provider": args.api_provider,
        "prompt_version": PROMPT_VERSION,
        "dry_run": bool(args.dry_run),
        "candidate_count": len(candidates),
        "prompt_count": len(prompt_manifest),
        "task_ids": sorted(
            {candidate["task_id"] for candidate in candidates}
            or {record["task_id"] for record in prompt_manifest}
        ),
        "generation_date_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Agent-style patches are labels pending validation until relabel step is run.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate agent-style AI candidate patches in copied checkouts.")
    parser.add_argument("--out-dir", default="outputs/httpie_agent_patch_stage_ab_001")
    parser.add_argument("--run-id", default="httpie_agent_patch_stage_ab_001")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument("--api-provider", choices=["deepseek_official", "qwen_official"], default="deepseek_official")
    parser.add_argument("--env", default=".env")
    parser.add_argument("--source-workspace-root", default=str(source_root_default()))
    parser.add_argument("--task-id", action="append", default=None)
    parser.add_argument("--patches-per-task", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--max-source-chars", type=int, default=12000)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def build_client(api_provider: str) -> DeepSeekClient | QwenClient:
    if api_provider == "deepseek_official":
        return DeepSeekClient()
    if api_provider == "qwen_official":
        return QwenClient()
    raise SystemExit(f"unsupported api provider: {api_provider}")


def main() -> None:
    args = parse_args()
    if args.execute and args.dry_run:
        raise SystemExit("Use either --dry-run or --execute, not both.")
    if not args.execute and not args.dry_run:
        raise SystemExit("Refusing to run: pass --dry-run or --execute explicitly.")
    source_root = Path(args.source_workspace_root)
    task_ids = args.task_id or DEFAULT_TASK_IDS
    source_bugs = dataset_builder.select_source_bugs(task_ids)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_manifest = read_jsonl(out_dir / "prompt_manifest.jsonl")
    candidates = read_jsonl(out_dir / "candidates.pending.jsonl")
    existing_patch_ids = {candidate["patch_id"] for candidate in candidates}
    client = None
    if args.execute:
        load_env_file(args.env)
        client = build_client(args.api_provider)
    candidate_index = len(candidates) + 1
    for source_bug in source_bugs:
        for variant_index in range(1, args.patches_per_task + 1):
            patch_id = f"{source_bug['task_id']}__agent_patch_{variant_index:02d}"
            if patch_id in existing_patch_ids:
                continue
            prompt = render_prompt(source_root, source_bug, variant_index, args.max_source_chars)
            upsert_prompt_manifest(
                prompt_manifest,
                {
                    "task_id": source_bug["task_id"],
                    "variant_index": variant_index,
                    "model": args.model,
                    "api_provider": args.api_provider,
                    "prompt_version": PROMPT_VERSION,
                    "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "prompt_chars": len(prompt),
                    "label_leakage_check": "passed",
                },
            )
            persist(out_dir, candidates, prompt_manifest)
            if args.dry_run:
                continue
            assert client is not None
            response = client.chat_completion(
                model=args.model,
                prompt=prompt,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            raw = write_raw(next_raw_response_path(out_dir, source_bug["task_id"], variant_index, args.model), response)
            workdir = out_dir / "agent_workdirs" / patch_id
            try:
                edits, rationale = parse_edit_plan(response)
                copy_buggy_checkout(source_root, source_bug, workdir)
                applied_edits = apply_edit_plan(workdir, edits)
                patch_text = run_git_diff(workdir, source_bug["touched_files"])
            except Exception as exc:  # noqa: BLE001
                write_json(
                    out_dir / "generation_error.json",
                    {
                        "task_id": source_bug["task_id"],
                        "variant_index": variant_index,
                        "raw_response": raw,
                        "error": redact_sensitive_text(str(exc)),
                        "note": "Agent edit generation stopped before candidate construction.",
                    },
                )
                persist(out_dir, candidates, prompt_manifest)
                raise SystemExit(f"Agent generation failed; see {(out_dir / 'generation_error.json').as_posix()}")
            model_candidate_id = f"agent_candidate_{candidate_index:04d}"
            candidates.append(
                build_candidate(
                    source_bug=source_bug,
                    patch_text=patch_text,
                    patch_id=patch_id,
                    model_candidate_id=model_candidate_id,
                    model=args.model,
                    api_provider=args.api_provider,
                    run_id=args.run_id,
                    raw=raw,
                    rationale=rationale,
                    applied_edits=applied_edits,
                )
            )
            existing_patch_ids.add(patch_id)
            candidate_index += 1
            persist(out_dir, candidates, prompt_manifest)
    persist(out_dir, candidates, prompt_manifest)
    summary = build_summary(args, candidates, prompt_manifest)
    write_json(out_dir / "generation_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
