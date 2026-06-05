from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

from cross_review.env import is_placeholder_secret, load_env_file
from cross_review.execution import run_python_solution
from cross_review.jsonl import append_jsonl, read_json, read_jsonl, write_jsonl
from cross_review.metrics import detection_metrics, repair_metrics
from cross_review.openrouter import OpenRouterClient, list_openrouter_models
from cross_review.parsing import extract_code, extract_json_object, normalize_review, response_text
from cross_review.prompts import generation_prompt, repair_prompt, review_prompt


def main() -> None:
    parser = argparse.ArgumentParser(prog="cross-review")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-config")
    validate.add_argument("--experiment", required=True)
    validate.add_argument("--models", required=True)
    validate.set_defaults(func=cmd_validate_config)

    run_tests = subparsers.add_parser("run-tests")
    run_tests.add_argument("--tasks", required=True)
    run_tests.add_argument("--generations", required=True)
    run_tests.add_argument("--out", required=True)
    run_tests.add_argument("--timeout-seconds", type=int, default=5)
    run_tests.set_defaults(func=cmd_run_tests)

    run_repair_tests = subparsers.add_parser("run-repair-tests")
    run_repair_tests.add_argument("--tasks", required=True)
    run_repair_tests.add_argument("--repairs", required=True)
    run_repair_tests.add_argument("--out", required=True)
    run_repair_tests.add_argument("--timeout-seconds", type=int, default=5)
    run_repair_tests.set_defaults(func=cmd_run_repair_tests)

    metrics = subparsers.add_parser("compute-metrics")
    metrics.add_argument("--executions", required=True)
    metrics.add_argument("--reviews", required=True)
    metrics.add_argument("--out", required=True)
    metrics.set_defaults(func=cmd_compute_metrics)

    repair_metrics_parser = subparsers.add_parser("compute-repair-metrics")
    repair_metrics_parser.add_argument("--executions", required=True)
    repair_metrics_parser.add_argument("--repair-executions", required=True)
    repair_metrics_parser.add_argument("--out", required=True)
    repair_metrics_parser.set_defaults(func=cmd_compute_repair_metrics)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--tasks", required=True)
    generate.add_argument("--models-config", required=True)
    generate.add_argument("--model-keys", required=True, help="Comma-separated model keys")
    generate.add_argument("--out", required=True)
    generate.add_argument("--limit", type=int, default=None)
    generate.add_argument("--env-file", default=".env")
    generate.set_defaults(func=cmd_generate)

    review = subparsers.add_parser("review")
    review.add_argument("--tasks", required=True)
    review.add_argument("--generations", required=True)
    review.add_argument("--models-config", required=True)
    review.add_argument("--reviewer-keys", required=True, help="Comma-separated model keys")
    review.add_argument("--out", required=True)
    review.add_argument("--env-file", default=".env")
    review.set_defaults(func=cmd_review)

    repair = subparsers.add_parser("repair")
    repair.add_argument("--tasks", required=True)
    repair.add_argument("--generations", required=True)
    repair.add_argument("--reviews", required=True)
    repair.add_argument("--models-config", required=True)
    repair.add_argument("--out", required=True)
    repair.add_argument("--env-file", default=".env")
    repair.set_defaults(func=cmd_repair)

    list_models = subparsers.add_parser("list-models")
    list_models.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    list_models.add_argument("--query", default="", help="Case-insensitive substring filter")
    list_models.add_argument("--limit", type=int, default=20)
    list_models.set_defaults(func=cmd_list_models)

    write_model_config = subparsers.add_parser("write-model-config")
    write_model_config.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    write_model_config.add_argument("--out", default="configs/models.local.json")
    write_model_config.add_argument("--gpt", required=True)
    write_model_config.add_argument("--claude", required=True)
    write_model_config.add_argument("--deepseek", required=False)
    write_model_config.add_argument("--qwen", required=False)
    write_model_config.set_defaults(func=cmd_write_model_config)

    check_env = subparsers.add_parser("check-env")
    check_env.add_argument("--env-file", default=".env")
    check_env.set_defaults(func=cmd_check_env)

    args = parser.parse_args()
    args.func(args)


def cmd_validate_config(args: argparse.Namespace) -> None:
    experiment = read_json(args.experiment)
    models = read_json(args.models)
    required_experiment_keys = {"run_id", "dataset_path", "output_dir", "prompt_versions", "models"}
    required_model_keys = {"base_url", "api_key_env", "models"}
    missing_experiment = sorted(required_experiment_keys - set(experiment))
    missing_models = sorted(required_model_keys - set(models))
    if missing_experiment or missing_models:
        raise SystemExit(
            json.dumps(
                {
                    "valid": False,
                    "missing_experiment_keys": missing_experiment,
                    "missing_model_keys": missing_models,
                },
                indent=2,
            )
        )
    print(json.dumps({"valid": True, "run_id": experiment["run_id"]}, indent=2))


def cmd_run_tests(args: argparse.Namespace) -> None:
    tasks = {task["task_id"]: task for task in read_jsonl(args.tasks)}
    generations = read_jsonl(args.generations)
    executions = []
    for generation in generations:
        task_id = generation["task_id"]
        if task_id not in tasks:
            raise SystemExit(f"Unknown task_id in generation: {task_id}")
        tests = list(tasks[task_id].get("hidden_tests", []))
        result = run_python_solution(
            code=generation["code"],
            tests=tests,
            timeout_seconds=args.timeout_seconds,
        )
        executions.append(
            {
                "generation_id": generation["generation_id"],
                "task_id": task_id,
                "generator_model": generation.get("generator_model"),
                **result,
            }
        )
    write_jsonl(args.out, executions)
    print(json.dumps({"executions": len(executions), "out": args.out}, indent=2))


def cmd_run_repair_tests(args: argparse.Namespace) -> None:
    tasks = {task["task_id"]: task for task in read_jsonl(args.tasks)}
    repairs = read_jsonl(args.repairs)
    executions = []
    for repair in repairs:
        task_id = repair["task_id"]
        if task_id not in tasks:
            raise SystemExit(f"Unknown task_id in repair: {task_id}")
        tests = list(tasks[task_id].get("hidden_tests", []))
        result = run_python_solution(
            code=repair["code"],
            tests=tests,
            timeout_seconds=args.timeout_seconds,
        )
        executions.append(
            {
                "repair_id": repair["repair_id"],
                "review_id": repair["review_id"],
                "generation_id": repair["generation_id"],
                "task_id": task_id,
                "repair_model": repair.get("repair_model"),
                **result,
            }
        )
    write_jsonl(args.out, executions)
    print(json.dumps({"repair_executions": len(executions), "out": args.out}, indent=2))


def cmd_compute_metrics(args: argparse.Namespace) -> None:
    executions = read_jsonl(args.executions)
    reviews = read_jsonl(args.reviews)
    metrics = detection_metrics(executions, reviews)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": args.out, "groups": sorted(metrics)}, indent=2))


def cmd_compute_repair_metrics(args: argparse.Namespace) -> None:
    executions = read_jsonl(args.executions)
    repair_executions = read_jsonl(args.repair_executions)
    metrics = repair_metrics(executions, repair_executions)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": args.out, "repair_attempts": metrics["repair_attempts"]}, indent=2))


def cmd_generate(args: argparse.Namespace) -> None:
    load_env_file(args.env_file)
    tasks = read_jsonl(args.tasks)
    if args.limit is not None:
        tasks = tasks[: args.limit]
    model_config = load_model_config(args.models_config)
    client = OpenRouterClient(base_url=model_config["base_url"])
    records = []
    out_path = Path(args.out)
    existing = read_jsonl(out_path) if out_path.exists() else []
    completed_generation_ids = {str(row["generation_id"]) for row in existing if "generation_id" in row}
    for task in tasks:
        for model_key in split_keys(args.model_keys):
            generation_id = f"{task['task_id']}__{model_key}__0"
            if generation_id in completed_generation_ids:
                continue
            spec = resolve_model(model_config, model_key)
            prompt = generation_prompt(task["prompt"])
            try:
                response = chat_completion_with_retries(client, prompt, spec["call"])
            except Exception as exc:
                append_api_error(args.out, generation_id, task["task_id"], model_key, exc)
                continue
            text = response_text(response)
            record = {
                    "generation_id": generation_id,
                    "task_id": task["task_id"],
                    "generator_model": model_key,
                    "model_id": spec["model_id"],
                    "prompt_version": "generation_v1",
                    "code": extract_code(text),
                    "raw_response_text": text,
                    "usage": response.get("usage", {}),
                    "latency_ms": response.get("latency_ms"),
                }
            records.append(record)
            append_jsonl(args.out, record)
            completed_generation_ids.add(generation_id)
    print(
        json.dumps(
            {
                "generations_added": len(records),
                "generations_total": len(completed_generation_ids),
                "out": args.out,
            },
            indent=2,
        )
    )


def cmd_review(args: argparse.Namespace) -> None:
    load_env_file(args.env_file)
    tasks = {task["task_id"]: task for task in read_jsonl(args.tasks)}
    generations = read_jsonl(args.generations)
    model_config = load_model_config(args.models_config)
    client = OpenRouterClient(base_url=model_config["base_url"])
    records = []
    out_path = Path(args.out)
    existing = read_jsonl(out_path) if out_path.exists() else []
    completed_review_ids = {str(row["review_id"]) for row in existing if "review_id" in row}
    for generation in generations:
        task = tasks[generation["task_id"]]
        for reviewer_key in split_keys(args.reviewer_keys):
            review_id = f"{generation['generation_id']}__reviewed_by__{reviewer_key}"
            if review_id in completed_review_ids:
                continue
            spec = resolve_model(model_config, reviewer_key)
            prompt = review_prompt(task["prompt"], generation["code"])
            try:
                response = chat_completion_with_retries(client, prompt, spec["call"])
            except Exception as exc:
                append_api_error(args.out, review_id, generation["task_id"], reviewer_key, exc)
                continue
            text = response_text(response)
            valid_review_json = True
            parse_error = None
            try:
                parsed = normalize_review(extract_json_object(text))
            except ValueError as exc:
                valid_review_json = False
                parse_error = str(exc)
                parsed = normalize_review({})
            generator_model = generation.get("generator_model")
            generator_model_id = generation.get("model_id")
            reviewer_model_id = spec["model_id"]
            if generator_model_id:
                review_type = "self" if generator_model_id == reviewer_model_id else "cross"
            else:
                review_type = "self" if generator_model == reviewer_key else "cross"
            record = {
                    "review_id": review_id,
                    "generation_id": generation["generation_id"],
                    "task_id": generation["task_id"],
                    "generator_model": generator_model,
                    "generator_model_id": generator_model_id,
                    "reviewer_model": reviewer_key,
                    "reviewer_model_id": reviewer_model_id,
                    "model_id": reviewer_model_id,
                    "review_type": review_type,
                    "prompt_version": "review_v1",
                    "valid_review_json": valid_review_json,
                    "raw_response_text": text,
                    "usage": response.get("usage", {}),
                    "latency_ms": response.get("latency_ms"),
                    **parsed,
                }
            if parse_error:
                record["parse_error"] = parse_error
            records.append(record)
            append_jsonl(args.out, record)
            completed_review_ids.add(review_id)
    print(
        json.dumps(
            {
                "reviews_added": len(records),
                "reviews_total": len(completed_review_ids),
                "out": args.out,
            },
            indent=2,
        )
    )


def cmd_repair(args: argparse.Namespace) -> None:
    load_env_file(args.env_file)
    tasks = {task["task_id"]: task for task in read_jsonl(args.tasks)}
    generations = {row["generation_id"]: row for row in read_jsonl(args.generations)}
    reviews = read_jsonl(args.reviews)
    model_config = load_model_config(args.models_config)
    client = OpenRouterClient(base_url=model_config["base_url"])
    out_path = Path(args.out)
    existing = read_jsonl(out_path) if out_path.exists() else []
    completed_repair_ids = {str(row["repair_id"]) for row in existing if "repair_id" in row}
    records = []
    for review in reviews:
        if not review.get("bug_found", False):
            continue
        repair_id = f"{review['review_id']}__repair"
        if repair_id in completed_repair_ids:
            continue
        reviewer_key = review["reviewer_model"]
        spec = resolve_model(model_config, reviewer_key)
        generation = generations[review["generation_id"]]
        task = tasks[review["task_id"]]
        prompt = repair_prompt(task["prompt"], generation["code"], review)
        try:
            response = chat_completion_with_retries(client, prompt, spec["call"])
        except Exception as exc:
            append_api_error(args.out, repair_id, review["task_id"], reviewer_key, exc)
            continue
        text = response_text(response)
        record = {
                "repair_id": repair_id,
                "review_id": review["review_id"],
                "generation_id": review["generation_id"],
                "task_id": review["task_id"],
                "repair_model": reviewer_key,
                "model_id": spec["model_id"],
                "prompt_version": "repair_v1",
                "code": extract_code(text),
                "raw_response_text": text,
                "usage": response.get("usage", {}),
                "latency_ms": response.get("latency_ms"),
            }
        records.append(record)
        append_jsonl(args.out, record)
        completed_repair_ids.add(repair_id)
    print(
        json.dumps(
            {
                "repairs_added": len(records),
                "repairs_total": len(completed_repair_ids),
                "out": args.out,
            },
            indent=2,
        )
    )


def cmd_list_models(args: argparse.Namespace) -> None:
    models = list_openrouter_models(args.base_url)
    query = args.query.lower().strip()
    if query:
        models = [
            model
            for model in models
            if query in str(model.get("id", "")).lower()
            or query in str(model.get("name", "")).lower()
        ]
    rows = []
    for model in models[: args.limit]:
        rows.append(
            {
                "id": model.get("id"),
                "name": model.get("name"),
                "context_length": model.get("context_length"),
                "pricing": model.get("pricing", {}),
            }
        )
    print(json.dumps({"count": len(models), "models": rows}, indent=2, ensure_ascii=False))


def cmd_write_model_config(args: argparse.Namespace) -> None:
    selected = {
        "gpt": args.gpt,
        "claude": args.claude,
    }
    if args.deepseek:
        selected["deepseek"] = args.deepseek
    if args.qwen:
        selected["qwen"] = args.qwen

    available_ids = {str(model.get("id")) for model in list_openrouter_models(args.base_url)}
    missing = sorted(model_id for model_id in selected.values() if model_id not in available_ids)
    if missing:
        raise SystemExit(
            json.dumps(
                {
                    "valid": False,
                    "missing_model_ids": missing,
                    "message": "One or more model IDs were not found in the current OpenRouter /models list.",
                },
                indent=2,
            )
        )

    config = {
        "base_url": args.base_url,
        "api_key_env": "OPENROUTER_API_KEY",
        "models": {
            key: {
                "model_id": model_id,
                "temperature": 0.2,
                "top_p": 1.0,
                "max_tokens": 4096,
            }
            for key, model_id in selected.items()
        },
    }
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(output), "models": selected}, indent=2, ensure_ascii=False))


def cmd_check_env(args: argparse.Namespace) -> None:
    loaded = load_env_file(args.env_file)
    openrouter_key = __import__("os").environ.get("OPENROUTER_API_KEY")
    has_key = not is_placeholder_secret(openrouter_key)
    has_base_url = bool(__import__("os").environ.get("OPENROUTER_BASE_URL"))
    print(
        json.dumps(
            {
                "env_file": args.env_file,
                "loaded_keys": sorted(loaded),
                "openrouter_api_key_set": has_key,
                "openrouter_api_key_placeholder": bool(openrouter_key) and not has_key,
                "openrouter_base_url_set": has_base_url,
            },
            indent=2,
        )
    )


def load_model_config(path: str) -> dict[str, object]:
    config = read_json(path)
    if "models" not in config or not isinstance(config["models"], dict):
        raise SystemExit("Model config must contain a models object")
    return config


def split_keys(value: str) -> list[str]:
    keys = [item.strip() for item in value.split(",") if item.strip()]
    if not keys:
        raise SystemExit("At least one model key is required")
    return keys


def resolve_model(config: dict[str, object], model_key: str) -> dict[str, object]:
    models = config["models"]
    assert isinstance(models, dict)
    if model_key not in models:
        raise SystemExit(f"Unknown model key: {model_key}")
    raw = models[model_key]
    if not isinstance(raw, dict):
        raise SystemExit(f"Model spec must be an object: {model_key}")
    model_id = str(raw.get("model_id", ""))
    if not model_id or "<fill-exact-openrouter-model-slug>" in model_id:
        raise SystemExit(f"Model key {model_key} has a placeholder model_id")
    return {
        "model_id": model_id,
        "call": {
            "model": model_id,
            "temperature": float(raw.get("temperature", 0.2)),
            "top_p": float(raw.get("top_p", 1.0)),
            "max_tokens": int(raw.get("max_tokens", 4096)),
        },
    }


def chat_completion_with_retries(
    client: OpenRouterClient,
    prompt: str,
    call: dict[str, Any],
    attempts: int = 3,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return client.chat_completion(prompt=prompt, **call)
        except Exception as exc:
            last_error = exc
            if attempt == attempts:
                break
            sleep_seconds = 2 * attempt
            print(
                f"API call failed on attempt {attempt}/{attempts}: {exc}; retrying in {sleep_seconds}s",
                file=sys.stderr,
            )
            time.sleep(sleep_seconds)
    assert last_error is not None
    raise last_error


def append_api_error(out_path: str, record_id: str, task_id: str, model_key: str, exc: Exception) -> None:
    error_path = str(Path(out_path).with_suffix(".errors.jsonl"))
    append_jsonl(
        error_path,
        {
            "record_id": record_id,
            "task_id": task_id,
            "model_key": model_key,
            "error_type": type(exc).__name__,
            "error": str(exc),
        },
    )
    print(f"API call failed after retries for {record_id}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    main()
