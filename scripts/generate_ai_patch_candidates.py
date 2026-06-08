from __future__ import annotations

import argparse
import hashlib
import json
import re
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
from cross_review.openrouter import DeepSeekClient, redact_sensitive_text  # noqa: E402
from cross_review.parsing import extract_json_object, response_text  # noqa: E402

import build_patch_verification_dataset as dataset_builder  # noqa: E402


PROMPT_VERSION = "ai_patch_generator_v1"
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


def write_json(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_root_default() -> Path:
    return Path("..") / "research" / "data" / "real_bugs" / "bugsinpy_workspace"


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
            "You are acting as an AI coding agent asked to fix a real Python bug.",
            "",
            "Return exactly one JSON object and no surrounding Markdown.",
            "",
            "JSON schema:",
            "{",
            '  "patch_diff": "unified diff patch against the buggy checkout",',
            '  "rationale": "short explanation of the intended fix",',
            '  "modified_files": ["relative/path.py"]',
            "}",
            "",
            "Rules:",
            "- Generate a plausible source patch as a unified diff.",
            "- The diff must apply to the buggy checkout with git apply.",
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
        raise ValueError(f"generator prompt contains forbidden evaluator tokens: {hits}")


def normalize_patch_diff(raw_patch: str) -> str:
    patch = raw_patch.strip()
    if patch.startswith("```"):
        patch = re.sub(r"^```(?:diff|patch)?\s*", "", patch)
        patch = re.sub(r"\s*```$", "", patch)
    patch = patch.replace("\r\n", "\n").replace("\r", "\n")
    if not patch.endswith("\n"):
        patch += "\n"
    return patch


def parse_generation(response: dict[str, Any]) -> tuple[str, str, list[str]]:
    text = response_text(response)
    parsed = extract_json_object(text)
    patch_diff = normalize_patch_diff(str(parsed.get("patch_diff", "")))
    rationale = str(parsed.get("rationale", "")).strip()
    modified_files_raw = parsed.get("modified_files", [])
    modified_files = [str(item) for item in modified_files_raw] if isinstance(modified_files_raw, list) else []
    if "@@" not in patch_diff:
        raise ValueError("generated patch_diff does not contain a unified-diff hunk")
    if not modified_files:
        modified_files = infer_modified_files(patch_diff)
    return patch_diff, rationale, modified_files


def infer_modified_files(patch_diff: str) -> list[str]:
    files: list[str] = []
    for line in patch_diff.splitlines():
        if line.startswith("+++ b/"):
            files.append(line[len("+++ b/") :])
    return files


def raw_response_path(out_dir: Path, task_id: str, variant_index: int, model: str, attempt: int = 1) -> Path:
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    suffix = "" if attempt == 1 else f"__attempt_{attempt:02d}"
    return out_dir / "raw" / safe_model / f"{task_id}__ai_patch_{variant_index:02d}{suffix}.json"


def raw_attempt_paths(out_dir: Path, task_id: str, variant_index: int, model: str) -> list[Path]:
    paths: list[Path] = []
    first = raw_response_path(out_dir, task_id, variant_index, model, attempt=1)
    if first.exists():
        paths.append(first)
    safe_model = re.sub(r"[^A-Za-z0-9_.-]+", "_", model)
    raw_dir = out_dir / "raw" / safe_model
    pattern = f"{task_id}__ai_patch_{variant_index:02d}__attempt_*.json"
    paths.extend(sorted(raw_dir.glob(pattern)))
    return paths


def write_raw(path: Path, response: dict[str, Any]) -> dict[str, str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(response, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.write_text(content, encoding="utf-8")
    return {"path": path.as_posix(), "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}


def raw_info(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    return {"path": path.as_posix(), "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_candidate(
    source_bug: dict[str, Any],
    patch_text: str,
    modified_files: list[str],
    patch_id: str,
    model_candidate_id: str,
    model: str,
    run_id: str,
    raw: dict[str, str],
    rationale: str,
) -> dict[str, Any]:
    touched_files = modified_files or source_bug["touched_files"]
    return {
        "patch_id": patch_id,
        "model_candidate_id": model_candidate_id,
        "task_id": source_bug["task_id"],
        "project": source_bug["project"],
        "source": "deepseek_official",
        "candidate_type": "model_generated_patch",
        "expected_outcome": "incorrect",
        "base_version": "buggy",
        "patch_text": patch_text,
        "touched_files": touched_files,
        "context_mode": "ai_generated_patch_diff",
        "visible_context": dataset_builder.build_visible_context(source_bug, touched_files),
        "issue_summary": source_bug["issue_summary"],
        "visible_tests": source_bug["visible_tests"],
        "hidden_oracles": source_bug["hidden_oracles"],
        "oracle_command": source_bug["oracle_command"],
        "oracle_workdir": f"data/patch_verification/workdirs/{patch_id}",
        "evidence_sources": ["patch_diff", "visible_test_hint"],
        "label_confidence": "pending_validation",
        "construction_notes": (
            f"AI-generated patch from {model} in run {run_id}. "
            "Expected outcome is initialized as incorrect until validation relabels it."
        ),
        "patch_materialization": "deepseek_ai_generated_unified_diff",
        "generation_model": model,
        "generation_prompt_version": PROMPT_VERSION,
        "generation_run_id": run_id,
        "generation_rationale": rationale,
        "raw_generation_response_path": raw["path"],
        "raw_generation_response_sha256": raw["sha256"],
    }


def build_evidence_packet(candidate: dict[str, Any]) -> dict[str, Any]:
    packet = dataset_builder.build_evidence_packet(candidate)
    packet["evidence_packet_version"] = "ai_patch_evidence_packet_v1"
    packet["available_evidence_sources"] = ["patch_diff", "visible_test_hint"]
    packet["label_leakage_guard"] = (
        "AI patch generation metadata, evaluator labels, hidden oracle paths, and oracle results are omitted"
    )
    return packet


def relabel_candidates_from_validation(
    candidates: list[dict[str, Any]],
    validations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    validation_by_id = {record["model_candidate_id"]: record for record in validations}
    relabeled: list[dict[str, Any]] = []
    for candidate in candidates:
        next_candidate = dict(candidate)
        validation = validation_by_id.get(candidate["model_candidate_id"])
        if not validation:
            relabeled.append(next_candidate)
            continue
        if not validation.get("patch_applied"):
            next_candidate["expected_outcome"] = "environment_invalid"
            next_candidate["label_confidence"] = "high"
            next_candidate["construction_notes"] += " Validation relabel: patch did not apply."
        elif validation.get("oracle_passed"):
            next_candidate["expected_outcome"] = "correct"
            next_candidate["label_confidence"] = "high"
            next_candidate["construction_notes"] += " Validation relabel: retained oracle passed."
        else:
            next_candidate["expected_outcome"] = "incorrect"
            next_candidate["label_confidence"] = "high"
            next_candidate["construction_notes"] += " Validation relabel: retained oracle failed."
        relabeled.append(next_candidate)
    return relabeled


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


def existing_candidate_ids(candidates: list[dict[str, Any]]) -> set[str]:
    return {str(candidate["patch_id"]) for candidate in candidates}


def upsert_prompt_manifest(
    prompt_manifest: list[dict[str, Any]],
    prompt_record: dict[str, Any],
) -> None:
    for index, record in enumerate(prompt_manifest):
        if (
            record.get("task_id") == prompt_record["task_id"]
            and int(record.get("variant_index", 0)) == int(prompt_record["variant_index"])
        ):
            prompt_manifest[index] = {
                **record,
                **prompt_record,
                "resumed_prompt_record": True,
            }
            return
    prompt_manifest.append(prompt_record)


def persist_pending(out_dir: Path, candidates: list[dict[str, Any]], prompt_manifest: list[dict[str, Any]]) -> None:
    write_jsonl(out_dir / "prompt_manifest.jsonl", prompt_manifest)
    if candidates:
        write_jsonl(out_dir / "candidates.pending.jsonl", candidates)
        write_jsonl(out_dir / "evidence_packets.pending.jsonl", [build_evidence_packet(c) for c in candidates])


def next_raw_attempt(out_dir: Path, task_id: str, variant_index: int, model: str) -> int:
    existing = raw_attempt_paths(out_dir, task_id, variant_index, model)
    return len(existing) + 1


def build_summary(
    run_id: str,
    model: str,
    candidates: list[dict[str, Any]],
    prompt_manifest: list[dict[str, Any]],
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "dry_run": dry_run,
        "candidate_count": len(candidates),
        "prompt_count": len(prompt_manifest),
        "task_ids": sorted(
            {candidate["task_id"] for candidate in candidates}
            or {record["task_id"] for record in prompt_manifest}
        ),
        "generation_date_utc": datetime.now(timezone.utc).isoformat(),
        "note": "Generated patches are labels pending validation until relabel step is run.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate AI candidate patches for validated BugsInPy tasks.")
    parser.add_argument("--out-dir", default="outputs/httpie_ai_patch_stage_ab_001")
    parser.add_argument("--run-id", default="httpie_ai_patch_stage_ab_001")
    parser.add_argument("--model", default="deepseek-v4-pro")
    parser.add_argument("--api-provider", choices=["deepseek_official"], default="deepseek_official")
    parser.add_argument("--env", default=".env")
    parser.add_argument("--source-workspace-root", default=str(source_root_default()))
    parser.add_argument("--task-id", action="append", default=None)
    parser.add_argument("--patches-per-task", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--max-source-chars", type=int, default=18000)
    parser.add_argument("--dry-run", action="store_true", help="Render prompts and metadata only.")
    parser.add_argument("--execute", action="store_true", help="Actually call the model API.")
    return parser.parse_args()


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

    prompt_manifest: list[dict[str, Any]] = read_jsonl(out_dir / "prompt_manifest.jsonl")
    candidates: list[dict[str, Any]] = read_jsonl(out_dir / "candidates.pending.jsonl")
    candidate_ids = existing_candidate_ids(candidates)
    client = None
    if args.execute:
        load_env_file(args.env)
        client = DeepSeekClient()

    candidate_index = len(candidates) + 1
    for source_bug in source_bugs:
        for variant_index in range(1, args.patches_per_task + 1):
            patch_id = f"{source_bug['task_id']}__ai_patch_{variant_index:02d}"
            if patch_id in candidate_ids:
                continue
            prompt = render_prompt(source_root, source_bug, variant_index, args.max_source_chars)
            prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            upsert_prompt_manifest(
                prompt_manifest,
                {
                    "task_id": source_bug["task_id"],
                    "variant_index": variant_index,
                    "model": args.model,
                    "prompt_version": PROMPT_VERSION,
                    "prompt_sha256": prompt_sha256,
                    "prompt_chars": len(prompt),
                    "label_leakage_check": "passed",
                },
            )
            persist_pending(out_dir, candidates, prompt_manifest)
            if args.dry_run:
                continue

            patch_text = ""
            rationale = ""
            modified_files: list[str] = []
            raw: dict[str, str] | None = None
            parse_errors: list[dict[str, str]] = []
            for existing_raw in raw_attempt_paths(out_dir, source_bug["task_id"], variant_index, args.model):
                response = read_json(existing_raw)
                try:
                    patch_text, rationale, modified_files = parse_generation(response)
                    raw = raw_info(existing_raw)
                    break
                except Exception as exc:  # noqa: BLE001
                    parse_errors.append({"path": existing_raw.as_posix(), "error": redact_sensitive_text(str(exc))})
            if raw is None:
                assert client is not None
                response = client.chat_completion(
                    model=args.model,
                    prompt=prompt,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                attempt = next_raw_attempt(out_dir, source_bug["task_id"], variant_index, args.model)
                raw = write_raw(
                    raw_response_path(out_dir, source_bug["task_id"], variant_index, args.model, attempt=attempt),
                    response,
                )
                try:
                    patch_text, rationale, modified_files = parse_generation(response)
                except Exception as exc:  # noqa: BLE001
                    parse_errors.append({"path": raw["path"], "error": redact_sensitive_text(str(exc))})
                    write_json(
                        out_dir / "generation_error.json",
                        {
                            "task_id": source_bug["task_id"],
                            "variant_index": variant_index,
                            "raw_response": raw,
                            "prior_parse_errors": parse_errors,
                            "error": redact_sensitive_text(str(exc)),
                            "note": "Generation stopped before candidate construction.",
                        },
                    )
                    persist_pending(out_dir, candidates, prompt_manifest)
                    raise SystemExit(
                        f"Generation parse failed; see {(out_dir / 'generation_error.json').as_posix()}"
                    )
            model_candidate_id = f"ai_candidate_{candidate_index:04d}"
            candidates.append(
                build_candidate(
                    source_bug=source_bug,
                    patch_text=patch_text,
                    modified_files=modified_files,
                    patch_id=patch_id,
                    model_candidate_id=model_candidate_id,
                    model=args.model,
                    run_id=args.run_id,
                    raw=raw,
                    rationale=rationale,
                )
            )
            candidate_ids.add(patch_id)
            candidate_index += 1
            persist_pending(out_dir, candidates, prompt_manifest)

    persist_pending(out_dir, candidates, prompt_manifest)
    summary = build_summary(args.run_id, args.model, candidates, prompt_manifest, dry_run=args.dry_run)
    write_json(out_dir / "generation_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
