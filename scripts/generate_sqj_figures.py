from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


COLORS = {
    "ink": "#202124",
    "muted": "#5f6368",
    "grid": "#d8dee9",
    "paper": "#ffffff",
    "blue": "#3867a9",
    "teal": "#2a9d8f",
    "green": "#4c956c",
    "orange": "#e76f51",
    "yellow": "#f4a261",
    "red": "#c44536",
    "purple": "#7b5ea7",
    "gray": "#e9ecef",
    "dark_gray": "#6b7280",
}

MODEL_LABELS = {
    "deepseek/deepseek-v4-pro": "DeepSeek\nV4 Pro",
    "qwen/qwen3.7-max": "Qwen3.7\nMax",
    "moonshotai/kimi-k2.6": "Kimi\nK2.6",
    "mistralai/devstral-2512": "Devstral\n2",
    "google/gemini-2.5-flash": "Gemini 2.5\nFlash",
}
MODEL_ORDER = list(MODEL_LABELS)
LEVELS = ["E0", "E1", "E2", "E3", "E4", "E5", "E6"]
FORMATS = ["pdf", "svg", "png"]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def ensure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.titlesize": 9,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "research95-sqj-figures",
            "figure.facecolor": COLORS["paper"],
            "axes.facecolor": COLORS["paper"],
        }
    )


def strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def save_figure(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for suffix in FORMATS:
        path = out_dir / f"{stem}.{suffix}"
        metadata = {"Creator": "research95 scripts/generate_sqj_figures.py"}
        if suffix == "svg":
            metadata["Date"] = None
        elif suffix == "pdf":
            metadata["CreationDate"] = None
            metadata["ModDate"] = None
        fig.savefig(path, bbox_inches="tight", dpi=300, metadata=metadata)
        if suffix == "svg":
            strip_trailing_whitespace(path)
    plt.close(fig)


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    label: str,
    fill: str,
    edge: str,
    fontsize: float = 7.5,
    weight: str = "regular",
) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.02",
        linewidth=1.0,
        edgecolor=edge,
        facecolor=fill,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        weight=weight,
        color=COLORS["ink"],
        linespacing=1.15,
    )


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#4b5563") -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, linewidth=1.1, color=color))


def decision_arrays(synthesis: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    by_level = synthesis.get("per_level_decision_counts_by_model", {})
    if not isinstance(by_level, dict):
        raise ValueError("synthesis missing per_level_decision_counts_by_model")
    reject = np.zeros((len(MODEL_ORDER), len(LEVELS)), dtype=float)
    escalate = np.zeros_like(reject)
    for level_idx, level in enumerate(LEVELS):
        per_model = by_level.get(level, {})
        if not isinstance(per_model, dict):
            raise ValueError(f"synthesis missing level {level}")
        for model_idx, model in enumerate(MODEL_ORDER):
            counts = per_model.get(model, {})
            if not isinstance(counts, dict):
                raise ValueError(f"synthesis missing model {model} at {level}")
            reject[model_idx, level_idx] = float(counts.get("reject", 0) or 0)
            escalate[model_idx, level_idx] = float(counts.get("escalate", 0) or 0)
    return reject, escalate


def fig_protocol(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.95, "EVP-8 hidden-evaluator study design", fontsize=11, weight="bold")
    ax.text(
        0.02,
        0.89,
        "A frozen packet set separates model-visible evidence from evaluator-only labels and cost accounting.",
        fontsize=7.5,
        color=COLORS["muted"],
    )

    add_box(ax, (0.04, 0.62), 0.18, 0.15, "98 candidate\npatches", "#e8f1ff", COLORS["blue"], weight="bold")
    add_box(ax, (0.29, 0.70), 0.20, 0.13, "7 evidence\nlevels E0-E6", "#ecfdf5", COLORS["teal"], weight="bold")
    add_box(ax, (0.29, 0.47), 0.20, 0.13, "Evaluator-only\nlabels hidden", "#f3f4f6", COLORS["dark_gray"])
    add_box(ax, (0.56, 0.62), 0.18, 0.15, "5 model\nverifiers", "#fff3cd", COLORS["yellow"], weight="bold")
    add_box(ax, (0.80, 0.72), 0.15, 0.10, "escalate", COLORS["gray"], COLORS["dark_gray"], weight="bold")
    add_box(ax, (0.80, 0.56), 0.15, 0.10, "reject", "#fde2e1", COLORS["red"], weight="bold")
    add_box(ax, (0.80, 0.40), 0.15, 0.10, "accept\n0 observed", "#ecfdf5", COLORS["green"])

    add_arrow(ax, (0.22, 0.70), (0.29, 0.77), COLORS["blue"])
    add_arrow(ax, (0.49, 0.77), (0.56, 0.70), COLORS["teal"])
    add_arrow(ax, (0.74, 0.70), (0.80, 0.77), COLORS["dark_gray"])
    add_arrow(ax, (0.74, 0.68), (0.80, 0.61), COLORS["red"])
    add_arrow(ax, (0.74, 0.65), (0.80, 0.45), COLORS["green"])

    ax.plot([0.39, 0.39], [0.60, 0.69], color=COLORS["grid"], linewidth=1.2)
    ax.text(0.29, 0.36, "Visible packets: task, patch, and level-specific evidence", fontsize=7.3, color=COLORS["teal"])
    ax.text(0.29, 0.29, "Hidden join after decision: oracle/correctness labels", fontsize=7.3, color=COLORS["dark_gray"])
    ax.text(0.56, 0.22, "Tracked summaries exclude raw response text", fontsize=7.3, color=COLORS["dark_gray"])
    ax.text(0.04, 0.12, "Scale: 98 candidates x 7 levels x 5 models = 3430 parse-valid decisions", fontsize=8.3, weight="bold")
    ax.text(0.04, 0.06, "Claim supported: descriptive evidence-conditioned behavior, not model superiority.", fontsize=7.3, color=COLORS["muted"])
    save_figure(fig, out_dir, "sqj_fig1_evp8_protocol")


def fig_decision_patterns(out_dir: Path, synthesis: dict[str, Any]) -> None:
    reject, escalate = decision_arrays(synthesis)
    aggregate_reject = reject.sum(axis=0)
    aggregate_escalate = escalate.sum(axis=0)

    fig = plt.figure(figsize=(7.4, 4.35))
    grid = fig.add_gridspec(2, 1, height_ratios=[1.25, 0.9], hspace=0.48)
    ax_heat = fig.add_subplot(grid[0, 0])
    ax_line = fig.add_subplot(grid[1, 0])
    fig.suptitle("EVP-8 five-model decision patterns", x=0.02, y=0.99, ha="left", fontsize=11, weight="bold")

    image = ax_heat.imshow(reject, cmap="YlOrRd", vmin=0, vmax=max(40, float(reject.max())), aspect="auto")
    for model_idx in range(reject.shape[0]):
        for level_idx in range(reject.shape[1]):
            value = int(reject[model_idx, level_idx])
            label = f"R{value}" if value else "R0"
            ax_heat.text(level_idx, model_idx, label, ha="center", va="center", fontsize=7, color=COLORS["ink"])
    ax_heat.set_xticks(np.arange(len(LEVELS)), LEVELS)
    ax_heat.set_yticks(np.arange(len(MODEL_ORDER)), [MODEL_LABELS[m] for m in MODEL_ORDER])
    ax_heat.set_title("Rejection count per 98 candidate-level packets", loc="left", fontsize=9, weight="bold")
    ax_heat.tick_params(length=0)
    for spine in ax_heat.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(image, ax=ax_heat, fraction=0.035, pad=0.02)
    cbar.set_label("reject decisions", fontsize=7)
    cbar.ax.tick_params(labelsize=7)

    ax_line.plot(LEVELS, aggregate_reject, marker="o", linewidth=2.0, color=COLORS["red"], label="reject")
    ax_line.plot(LEVELS, aggregate_escalate, marker="o", linewidth=2.0, color=COLORS["dark_gray"], label="escalate")
    ax_line.set_title("Aggregate decisions are non-monotonic across evidence levels", loc="left", fontsize=9, weight="bold")
    ax_line.set_ylabel("decisions")
    ax_line.set_ylim(0, 500)
    ax_line.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax_line.spines[["top", "right"]].set_visible(False)
    ax_line.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.25))
    for x_pos, value in enumerate(aggregate_reject):
        ax_line.text(x_pos, value + 9, str(int(value)), ha="center", va="bottom", fontsize=7, color=COLORS["red"])
    save_figure(fig, out_dir, "sqj_fig2_decision_patterns")


def fig_cost_boundary(out_dir: Path, cost: dict[str, Any]) -> None:
    totals = cost.get("totals", {})
    if not isinstance(totals, dict):
        raise ValueError("cost summary missing totals")
    passed_costs = cost.get("passed_result_costs", [])
    blocked_costs = cost.get("blocked_attempt_costs", [])
    if not isinstance(passed_costs, list) or not isinstance(blocked_costs, list):
        raise ValueError("cost summary missing cost rows")

    passed_usd = float(totals.get("passed_result_usd_excluding_qwen", 0) or 0)
    blocked_usd = float(totals.get("blocked_attempt_usd", 0) or 0)
    qwen_cny = float(totals.get("passed_qwen_cny", 0) or 0)
    valid_reviews = sum(int(row.get("parse_valid_count", 0) or 0) for row in passed_costs if isinstance(row, dict))
    invalid_blocked = sum(int(row.get("invalid_parse_count", 0) or 0) for row in blocked_costs if isinstance(row, dict))

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.1, 1.0]})
    fig.suptitle("Cost observability separates valid results from blocked attempts", x=0.02, y=1.02, ha="left", fontsize=11, weight="bold")

    ax = axes[0]
    labels = ["passed\nUSD", "blocked\nUSD", "Qwen\nCNY"]
    values = [passed_usd, blocked_usd, qwen_cny]
    colors = [COLORS["green"], COLORS["orange"], COLORS["blue"]]
    bars = ax.bar(labels, values, color=colors, width=0.62)
    ax.set_title("Observable cost ledger", loc="left", fontsize=9, weight="bold")
    ax.set_ylabel("reported currency units")
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + max(values) * 0.03, f"{value:.3f}", ha="center", fontsize=7)

    ax2 = axes[1]
    ax2.bar(["valid\nmodel records", "blocked\ninvalid records"], [valid_reviews, invalid_blocked], color=[COLORS["green"], COLORS["red"]], width=0.58)
    ax2.set_title("Result validity boundary", loc="left", fontsize=9, weight="bold")
    ax2.set_ylabel("records")
    ax2.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.text(0, valid_reviews + 70, str(valid_reviews), ha="center", fontsize=7, color=COLORS["green"])
    ax2.text(1, invalid_blocked + 70, str(invalid_blocked), ha="center", fontsize=7, color=COLORS["red"])
    fig.text(
        0.02,
        -0.02,
        "Blocked attempts are engineering-risk evidence only and are excluded from five-model decision-pattern synthesis.",
        fontsize=7,
        color=COLORS["muted"],
    )
    save_figure(fig, out_dir, "sqj_fig3_cost_boundary")


def write_manifest(out_dir: Path) -> None:
    manifest = {
        "figure_count": 3,
        "formats": FORMATS,
        "core_conclusion": (
            "EVP-8 evidence visibility changes LLM merge-gate behavior, but the response is "
            "model-dependent and non-monotonic; cost risk is tracked separately from valid results."
        ),
        "figures": [
            {
                "id": "sqj_fig1_evp8_protocol",
                "purpose": "EVP-8 hidden-evaluator protocol and scale overview",
            },
            {
                "id": "sqj_fig2_decision_patterns",
                "purpose": "five-model per-level rejection/escalation patterns",
            },
            {
                "id": "sqj_fig3_cost_boundary",
                "purpose": "valid-result cost versus blocked-attempt cost boundary",
            },
        ],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "figure_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SQJ-specific EVP-8 publication figures.")
    parser.add_argument("--out-dir", default="docs/figures/sqj")
    parser.add_argument("--synthesis", default="data/protocols/evp8_five_model_synthesis_v0_1.json")
    parser.add_argument("--cost-accounting", default="data/reviews/evp8_cost_accounting_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_style()
    out_dir = Path(args.out_dir)
    synthesis = read_json(Path(args.synthesis))
    cost = read_json(Path(args.cost_accounting))
    fig_protocol(out_dir)
    fig_decision_patterns(out_dir, synthesis)
    fig_cost_boundary(out_dir, cost)
    write_manifest(out_dir)
    print(json.dumps({"out_dir": str(out_dir), "figure_count": 3, "formats": FORMATS}, indent=2))


if __name__ == "__main__":
    main()
