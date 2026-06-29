from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPT_DIR = REPO_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from cross_review.env import load_env_file  # noqa: E402
from cross_review.openrouter import DeepSeekClient, QwenClient, redact_sensitive_text  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_patch_verification_dataset as dataset_builder  # noqa: E402
from generate_agent_patch_candidates import (  # noqa: E402
    FORBIDDEN_PROMPT_TOKENS,
    raw_response_path,
    source_root_default,
    write_raw,
)


PROMPT_VERSION = "agent_full_file_v1"
DEFAULT_TASK_IDS = ["bugsinpy_youtube-dl_7"]


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


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
        Path(failed_path).chmod(stat.S_IWRITE)
        func(failed_path)

    shutil.rmtree(path, onerror=make_writable_and_retry)


def copy_buggy_checkout(source_root: Path, source_bug: dict[str, Any], workdir: Path) -> None:
    source = checkout_root(source_root, source_bug)
    if not source.exists():
        raise FileNotFoundError(f"missing buggy checkout: {source}")
    if workdir.exists():
        remove_tree(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source / ".git", workdir / ".git")
    for file_path in source_bug["touched_files"]:
        src = source / file_path
        dst = workdir / file_path
        if not src.exists():
            raise FileNotFoundError(f"missing touched file: {src}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def read_buggy_file(source_root: Path, source_bug: dict[str, Any], max_source_chars: int) -> tuple[str, str]:
    touched_files = list(source_bug["touched_files"])
    if len(touched_files) != 1:
        raise ValueError("full-file protocol supports exactly one touched file")
    file_path = str(touched_files[0])
    path = dataset_builder.checkout_file(source_root, source_bug, "buggy", file_path)
    if not path.exists():
        raise FileNotFoundError(f"missing buggy source file: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) > max_source_chars:
        raise ValueError(
            f"buggy source file has {len(text)} chars, exceeding max_source_chars={max_source_chars}"
        )
    return file_path, text


def check_prompt_boundary(prompt: str) -> None:
    hits = [token for token in FORBIDDEN_PROMPT_TOKENS if token in prompt]
    if hits:
        raise ValueError(f"full-file prompt contains forbidden evaluator tokens: {hits}")


def render_prompt(source_root: Path, source_bug: dict[str, Any], variant_index: int, max_source_chars: int) -> str:
    file_path, source_text = read_buggy_file(source_root, source_bug, max_source_chars)
    prompt = "\n".join(
        [
            "You are acting as an AI coding agent editing a copied Python checkout.",
            "",
            "Return exactly one JSON object and no surrounding Markdown.",
            "",
            "JSON schema:",
            "{",
            '  "file_path": "relative/path.py",',
            '  "content": "complete revised file content",',
            '  "rationale": "short explanation of the intended fix"',
            "}",
            "",
            "Rules:",
            "- Return the complete revised content of the single touched file.",
            "- Do not return a diff, patch, search/replace edit, or Markdown fence.",
            "- Preserve unrelated code exactly unless changing it is necessary for the visible issue.",
            "- Use only the visible issue summary, visible test hint, touched file name, and buggy source below.",
            "- Do not assume hidden tests, oracle results, reference patches, fixed code, or post-fix code.",
            "",
            f"Task id: {source_bug['task_id']}",
            f"Patch variant requested: {variant_index}",
            f"Project: {source_bug['project']}",
            f"Issue summary: {source_bug['issue_summary']}",
            f"Touched file: {file_path}",
            f"Visible test hint: {json.dumps(source_bug['visible_tests'], ensure_ascii=False)}",
            "",
            "Buggy source:",
            f"### File: {file_path}",
            "```python",
            source_text,
            "```",
        ]
    )
    check_prompt_boundary(prompt)
    return prompt


def next_raw_response_path(out_dir: Path, task_id: str, variant_index: int, model: str) -> Path:
    attempt = 1
    while raw_response_path(out_dir, task_id, variant_index, model, attempt).exists():
        attempt += 1
    return raw_response_path(out_dir, task_id, variant_index, model, attempt)


def parse_full_file_response(response: dict[str, Any], expected_file_path: str) -> tuple[str, str]:
    parsed = extract_json_object(response_text(response))
    file_path = str(parsed.get("file_path", "")).strip()
    content = parsed.get("content")
    if file_path != expected_file_path:
        raise ValueError(f"unexpected file_path: {file_path!r}")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("missing full-file content")
    return content, str(parsed.get("rationale", "")).strip()


def materialize_full_file(workdir: Path, file_path: str, content: str) -> None:
    rel = Path(file_path)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError(f"unsafe file path: {file_path}")
    path = workdir / rel
    if not path.exists():
        raise FileNotFoundError(f"target file does not exist: {file_path}")
    path.write_text(content, encoding="utf-8", newline="\n")


def run_git_diff(workdir: Path, touched_file: str) -> str:
    completed = subprocess.run(
        ["git", "diff", "--", touched_file],
        cwd=workdir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git diff failed: {completed.stderr[-1000:]}")
    if "@@" not in completed.stdout:
        raise ValueError("full-file response produced no unified-diff hunks")
    return completed.stdout


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
) -> dict[str, Any]:
    return {
        "patch_id": patch_id,
        "model_candidate_id": model_candidate_id,
        "task_id": source_bug["task_id"],
        "project": source_bug["project"],
        "source": f"{api_provider}_agent_full_file",
        "candidate_type": "model_generated_patch",
        "expected_outcome": "incorrect",
        "base_version": "buggy",
        "patch_text": patch_text,
        "touched_files": source_bug["touched_files"],
        "context_mode": "agent_full_file_git_diff",
        "visible_context": dataset_builder.build_visible_context(source_bug, source_bug["touched_files"]),
        "issue_summary": source_bug["issue_summary"],
        "visible_tests": source_bug["visible_tests"],
        "hidden_oracles": source_bug["hidden_oracles"],
        "oracle_command": source_bug["oracle_command"],
        "oracle_workdir": f"data/patch_verification/workdirs/{patch_id}",
        "evidence_sources": ["patch_diff", "visible_test_hint", "agent_full_file"],
        "label_confidence": "pending_validation",
        "construction_notes": (
            f"Agent-style full-file AI-generated patch from {model} in run {run_id}. "
            "The model returned complete file content; the script overwrote a copied buggy file "
            "and exported patch_text with git diff."
        ),
        "patch_materialization": "agent_full_file_git_diff",
        "generation_model": model,
        "generation_prompt_version": PROMPT_VERSION,
        "generation_run_id": run_id,
        "generation_rationale": rationale,
        "raw_generation_response_path": raw["path"],
        "raw_generation_response_sha256": raw["sha256"],
    }


def build_evidence_packet(candidate: dict[str, Any]) -> dict[str, Any]:
    packet = dataset_builder.build_evidence_packet(candidate)
    packet["evidence_packet_version"] = "agent_full_file_evidence_packet_v1"
    packet["available_evidence_sources"] = ["patch_diff", "visible_test_hint"]
    packet["label_leakage_guard"] = "Full-file generation metadata, evaluator labels, and oracle results are omitted"
    return packet


def build_client(api_provider: str) -> DeepSeekClient | QwenClient:
    if api_provider == "deepseek_official":
        return DeepSeekClient()
    if api_provider == "qwen_official":
        return QwenClient()
    raise SystemExit(f"unsupported api provider: {api_provider}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate single-file full-file AI candidate patches.")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--model", default="qwen3.7-max")
    parser.add_argument("--api-provider", choices=["deepseek_official", "qwen_official"], default="qwen_official")
    parser.add_argument("--env", default=".env")
    parser.add_argument("--source-workspace-root", default=str(source_root_default()))
    parser.add_argument("--task-id", action="append", default=None)
    parser.add_argument("--patches-per-task", type=int, default=4)
    parser.add_argument("--variant-start-index", type=int, default=1)
    parser.add_argument("--model-candidate-start-index", type=int, default=1)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-tokens", type=int, default=32768)
    parser.add_argument("--max-source-chars", type=int, default=90000)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--execute", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.dry_run == args.execute:
        raise SystemExit("Pass exactly one of --dry-run or --execute.")
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
    candidate_index = args.model_candidate_start_index + len(candidates)
    for source_bug in source_bugs:
        file_path = str(source_bug["touched_files"][0])
        for variant_index in range(args.variant_start_index, args.variant_start_index + args.patches_per_task):
            patch_id = f"{source_bug['task_id']}__full_file_patch_{variant_index:02d}"
            prompt = render_prompt(source_root, source_bug, variant_index, args.max_source_chars)
            prompt_manifest.append(
                {
                    "task_id": source_bug["task_id"],
                    "variant_index": variant_index,
                    "model": args.model,
                    "api_provider": args.api_provider,
                    "prompt_version": PROMPT_VERSION,
                    "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "prompt_chars": len(prompt),
                    "label_leakage_check": "passed",
                }
            )
            write_jsonl(out_dir / "prompt_manifest.jsonl", prompt_manifest)
            if args.dry_run or patch_id in existing_patch_ids:
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
                content, rationale = parse_full_file_response(response, file_path)
                copy_buggy_checkout(source_root, source_bug, workdir)
                materialize_full_file(workdir, file_path, content)
                patch_text = run_git_diff(workdir, file_path)
            except Exception as exc:  # noqa: BLE001
                write_json(
                    out_dir / "generation_error.json",
                    {
                        "task_id": source_bug["task_id"],
                        "variant_index": variant_index,
                        "raw_response": raw,
                        "error": redact_sensitive_text(str(exc)),
                        "note": "Full-file generation stopped before candidate construction.",
                    },
                )
                raise SystemExit(f"Full-file generation failed; see {(out_dir / 'generation_error.json').as_posix()}")
            candidate = build_candidate(
                source_bug=source_bug,
                patch_text=patch_text,
                patch_id=patch_id,
                model_candidate_id=f"agent_candidate_{candidate_index:04d}",
                model=args.model,
                api_provider=args.api_provider,
                run_id=args.run_id,
                raw=raw,
                rationale=rationale,
            )
            candidates.append(candidate)
            existing_patch_ids.add(patch_id)
            candidate_index += 1
            write_jsonl(out_dir / "candidates.pending.jsonl", candidates)
            write_jsonl(
                out_dir / "evidence_packets.pending.jsonl",
                [build_evidence_packet(candidate) for candidate in candidates],
            )
    summary = {
        "run_id": args.run_id,
        "model": args.model,
        "api_provider": args.api_provider,
        "prompt_version": PROMPT_VERSION,
        "dry_run": bool(args.dry_run),
        "candidate_count": len(candidates),
        "prompt_count": len(prompt_manifest),
        "task_ids": sorted({record["task_id"] for record in prompt_manifest}),
        "generation_date_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Full-file agent patches are labels pending validation until relabel step is run.",
    }
    write_json(out_dir / "generation_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
