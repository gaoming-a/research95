from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a cross-review experiment run.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    summary = summarize_run(run_dir)
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"out": str(output), "summary": summary}, indent=2, ensure_ascii=False))


def summarize_run(run_dir: Path) -> dict[str, Any]:
    generations = read_jsonl(run_dir / "generations.jsonl")
    executions = read_jsonl(run_dir / "executions.jsonl")
    reviews = read_jsonl(run_dir / "reviews.jsonl")
    repairs = read_jsonl(run_dir / "repairs.jsonl")
    repair_executions = read_jsonl(run_dir / "repair_executions.jsonl")
    detection_metrics = read_json(run_dir / "metrics.json")
    repair_metrics = read_json(run_dir / "repair_metrics.json")

    passed = sum(1 for row in executions if row.get("passed"))
    failed = sum(1 for row in executions if not row.get("passed"))
    bug_found = sum(1 for row in reviews if row.get("bug_found"))
    cost_by_stage = {
        "generation": sum_cost(generations),
        "review": sum_cost(reviews),
        "repair": sum_cost(repairs),
    }

    return {
        "run_dir": str(run_dir),
        "generation_records": len(generations),
        "execution_records": len(executions),
        "passed_generations": passed,
        "failed_generations": failed,
        "bug_yield": failed,
        "review_records": len(reviews),
        "reviews_reporting_bug": bug_found,
        "repair_records": len(repairs),
        "repair_execution_records": len(repair_executions),
        "detection_metrics": detection_metrics,
        "repair_metrics": repair_metrics,
        "cost_by_stage": cost_by_stage,
        "total_cost": sum(cost_by_stage.values()),
    }


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected object records in {path}")
            records.append(value)
    return records


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return value


def sum_cost(records: list[dict[str, Any]]) -> float:
    total = 0.0
    for record in records:
        usage = record.get("usage") or {}
        if isinstance(usage, dict):
            total += float(usage.get("cost") or 0.0)
    return total


if __name__ == "__main__":
    main()
