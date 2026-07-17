# ruff: noqa: E402
"""Simulate conditional repeat-window precision for DSA Regular and Short."""

from __future__ import annotations

from audit_research_lineage_isolation import assert_prior_research_execution_blocked

assert_prior_research_execution_blocked("scripts/dsa2026_simulate_p2_precision.py")

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / "data/protocols/dsa_p2_source_selection_v0_1.json"
JSON_OUT = ROOT / "data/protocols/dsa_p2_precision_simulation_v0_1.json"
MD_OUT = ROOT / "docs/experiments/dsa_p2_precision_simulation_v0_1.md"
SEED_TEXT = "DSA-2026-P2-CONDITIONAL-PRECISION-20260711-V1"
SEED_SHA256 = hashlib.sha256(SEED_TEXT.encode()).hexdigest()
SIMULATED_RUN_WINDOWS = 20000
SCENARIOS = [
    *[(rate, rate, rho) for rate in (0.1, 0.25, 0.5, 0.75, 0.9) for rho in (0.0, 0.3, 0.6)],
    *((0.25, 0.5, rho) for rho in (0.0, 0.3, 0.6)),
    *((0.5, 0.25, rho) for rho in (0.0, 0.3, 0.6)),
]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def joint_probability(p0: float, p3: float, requested_rho: float) -> tuple[float, float]:
    scale = np.sqrt(p0 * (1.0 - p0) * p3 * (1.0 - p3))
    lower = max(0.0, p0 + p3 - 1.0)
    upper = min(p0, p3)
    requested_p11 = p0 * p3 + requested_rho * scale
    p11 = min(upper, max(lower, requested_p11))
    actual_rho = 0.0 if scale == 0 else (p11 - p0 * p3) / scale
    return float(p11), float(actual_rho)


def interval_width(values: np.ndarray) -> float:
    low, high = np.quantile(values, [0.025, 0.975])
    return float(high - low)


def simulate_scenario(
    rng: np.random.Generator,
    task_projects: list[str],
    models: int,
    repeats: int,
    p0: float,
    p3: float,
    requested_rho: float,
) -> dict[str, Any]:
    tasks = len(task_projects)
    p11, actual_rho = joint_probability(p0, p3, requested_rho)
    p10 = p0 - p11
    p01 = p3 - p11
    u = rng.random((SIMULATED_RUN_WINDOWS, tasks, models, repeats), dtype=np.float32)
    c0 = u < (p11 + p10)
    c3 = (u < p11) | ((u >= p11 + p10) & (u < p11 + p10 + p01))
    rate0 = c0.mean(axis=(1, 2, 3))
    rate3 = c3.mean(axis=(1, 2, 3))
    effect = rate3 - rate0
    task_effect = (c3.astype(np.int8) - c0.astype(np.int8)).mean(axis=(2, 3))
    project_values = sorted(set(task_projects), key=str.lower)
    loo = []
    task_projects_array = np.asarray(task_projects)
    for project in project_values:
        mask = task_projects_array != project
        loo.append(task_effect[:, mask].mean(axis=1))
    loo_matrix = np.stack(loo, axis=1)
    loo_range = loo_matrix.max(axis=1) - loo_matrix.min(axis=1)
    return {
        "p_c0": p0,
        "p_c3": p3,
        "requested_within_block_correlation": requested_rho,
        "actual_within_block_correlation": actual_rho,
        "c0_rate_interval_width": interval_width(rate0),
        "c3_rate_interval_width": interval_width(rate3),
        "paired_effect_interval_width": interval_width(effect),
        "paired_effect_median": float(np.median(effect)),
        "leave_one_project_out_effect_range_median": float(np.median(loo_range)),
        "leave_one_project_out_effect_range_p95": float(np.quantile(loo_range, 0.95)),
    }


def simulate_protocol(
    protocol: str,
    selection: dict[str, Any],
    models: int,
    repeats: int,
    rate_width_threshold: float | None,
    effect_width_threshold: float,
) -> dict[str, Any]:
    task_projects = [record["project"] for record in selection[protocol.lower()]["primary"]]
    seed = int(hashlib.sha256(f"{SEED_SHA256}|{protocol}".encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(seed)
    scenarios = [
        simulate_scenario(rng, task_projects, models, repeats, p0, p3, rho)
        for p0, p3, rho in SCENARIOS
    ]
    maximum_rate_width = max(
        max(item["c0_rate_interval_width"], item["c3_rate_interval_width"])
        for item in scenarios
    )
    maximum_effect_width = max(item["paired_effect_interval_width"] for item in scenarios)
    checks = {
        "effect_interval_width_gate_passed": maximum_effect_width <= effect_width_threshold,
    }
    if rate_width_threshold is not None:
        checks["primary_rate_interval_width_gate_passed"] = maximum_rate_width <= rate_width_threshold
    return {
        "protocol": protocol,
        "tasks": len(task_projects),
        "projects": len(set(task_projects)),
        "models": models,
        "repeats": repeats,
        "simulated_run_windows_per_scenario": SIMULATED_RUN_WINDOWS,
        "rate_width_threshold": rate_width_threshold,
        "paired_effect_width_threshold": effect_width_threshold,
        "maximum_rate_interval_width": maximum_rate_width,
        "maximum_paired_effect_interval_width": maximum_effect_width,
        "maximum_leave_one_project_out_effect_range_p95": max(
            item["leave_one_project_out_effect_range_p95"] for item in scenarios
        ),
        "checks": checks,
        "passed": all(checks.values()),
        "scenarios": scenarios,
    }


def build() -> dict[str, Any]:
    selection = read_json(SELECTION)
    regular = simulate_protocol("Regular", selection, models=3, repeats=3, rate_width_threshold=0.35, effect_width_threshold=0.30)
    short = simulate_protocol("Short", selection, models=2, repeats=3, rate_width_threshold=None, effect_width_threshold=0.40)
    return {
        "simulation_id": "dsa_p2_precision_simulation_v0_1",
        "simulation_date": "2026-07-11",
        "status": "passed" if regular["passed"] and short["passed"] else "failed",
        "seed_sha256": SEED_SHA256,
        "estimand_boundary": "finite frozen cohort; intervals condition only on task/model and quantify stateless repeat-window decision stochasticity",
        "not_claimed": [
            "population sampling uncertainty across tasks or projects",
            "cross-project generalization confidence interval",
            "candidate-level independent sample size",
        ],
        "regular": regular,
        "short": short,
        "data_boundary": {
            "model_api_called": False,
            "model_output_read": False,
            "legacy_paper_metric_read": False,
            "candidate_hidden_result_read": False,
        },
    }


def render_markdown(value: dict[str, Any]) -> str:
    regular = value["regular"]
    short = value["short"]
    return "\n".join(
        [
            "# DSA 2026 P2 Conditional Precision Simulation v0.1",
            "",
            "日期：2026-07-11",
            "",
            "## 结论",
            "",
            f"- Regular：最大 primary-rate interval width = {regular['maximum_rate_interval_width']:.4f}（门限 0.35）；最大 paired-effect width = {regular['maximum_paired_effect_interval_width']:.4f}（门限 0.30）。",
            f"- Short：最大 paired-effect width = {short['maximum_paired_effect_interval_width']:.4f}（门限 0.40）。",
            f"- Gate：Regular={'PASS' if regular['passed'] else 'FAIL'}；Short={'PASS' if short['passed'] else 'FAIL'}。",
            "",
            "## 模拟边界",
            "",
            f"每个场景模拟 {SIMULATED_RUN_WINDOWS} 个固定 run window，覆盖 C0/C3 marginal rate 0.1、0.25、0.5、0.75、0.9，",
            "以及 requested within-block correlation 0、0.3、0.6；不可能的 Bernoulli correlation 按 Fréchet boundary 截断并记录实际值。",
            "",
            "区间只量化固定 task/model 下三次 stateless repeat 的 decision stochasticity。task 和 project 不是总体随机样本，",
            "因此这些宽度不得称为跨项目总体置信区间。leave-one-project-out effect range 只作为稳定性边界报告，不是 CI。",
            "",
            "本模拟未调用模型、未读取任何模型输出、旧论文指标或 candidate hidden result。",
            "",
        ]
    )


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    outputs = {JSON_OUT: serialize(value), MD_OUT: render_markdown(value)}
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != content]
        if stale:
            raise SystemExit(f"stale or missing outputs: {stale}")
        if value["status"] != "passed":
            raise SystemExit("conditional precision simulation failed")
    print(json.dumps({"status": value["status"], "regular": value["regular"]["checks"], "short": value["short"]["checks"]}, sort_keys=True))


if __name__ == "__main__":
    main()
