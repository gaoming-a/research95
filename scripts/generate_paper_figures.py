from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


COLORS = {
    "ink": "#202124",
    "muted": "#5f6368",
    "grid": "#d8dee9",
    "paper": "#ffffff",
    "blue": "#2f5597",
    "cyan": "#2a9d8f",
    "orange": "#e76f51",
    "yellow": "#f4a261",
    "green": "#4c956c",
    "purple": "#7b5ea7",
    "red": "#c44536",
    "gray": "#e9ecef",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def ensure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "research95-paper-figures",
            "figure.facecolor": COLORS["paper"],
            "axes.facecolor": COLORS["paper"],
        }
    )


def save_figure(fig: plt.Figure, out_dir: Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ["pdf", "svg", "png"]:
        path = out_dir / f"{stem}.{suffix}"
        metadata = {"Creator": "research95 scripts/generate_paper_figures.py"}
        if suffix == "svg":
            metadata["Date"] = None
        elif suffix == "pdf":
            metadata["CreationDate"] = None
            metadata["ModDate"] = None
        fig.savefig(path, bbox_inches="tight", dpi=300, metadata=metadata)
        if suffix == "svg":
            strip_trailing_whitespace(path)
    plt.close(fig)


def strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    label: str,
    fc: str,
    ec: str | None = None,
    fontsize: int = 8,
    weight: str = "regular",
) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.1,
        edgecolor=ec or COLORS["ink"],
        facecolor=fc,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        label,
        ha="center",
        va="center",
        color=COLORS["ink"],
        fontsize=fontsize,
        weight=weight,
        linespacing=1.15,
    )


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#4b5563") -> None:
    arrow = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.2, color=color)
    ax.add_patch(arrow)


def prefixed_group(groups: dict[str, Any], prefix: str) -> dict[str, Any]:
    for key, value in groups.items():
        if key.startswith(prefix):
            if not isinstance(value, dict):
                raise ValueError(f"{key} must be a JSON object")
            return value
    raise KeyError(f"missing group with prefix {prefix}")


def merged_metrics(prompt_metrics: dict[str, Any], tool_gate: dict[str, Any]) -> dict[str, dict[str, float]]:
    groups = prompt_metrics.get("groups", {})
    if not isinstance(groups, dict):
        raise ValueError("metrics.json groups must be an object")
    tool_metrics = tool_gate.get("metrics", {})
    if not isinstance(tool_metrics, dict):
        raise ValueError("tool gate metrics must be an object")
    return {
        "LLM-only": prefixed_group(groups, "llm_only::"),
        "Prompt-only\nEvidence-first": prefixed_group(groups, "evidence_first::"),
        "Tool-augmented\nEvidence": tool_metrics,
    }


def fig_framework(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.95, "Patch verification workflow", fontsize=11, weight="bold", color=COLORS["ink"])
    ax.text(0.02, 0.89, "A candidate patch is judged by progressively stronger evidence.", fontsize=8, color=COLORS["muted"])

    add_box(ax, (0.04, 0.56), 0.16, 0.18, "Real bug task\n+ candidate patch", COLORS["gray"], fontsize=8, weight="bold")
    add_box(ax, (0.27, 0.70), 0.20, 0.16, "LLM-only\nplausibility review", "#dbeafe", ec=COLORS["blue"])
    add_box(ax, (0.27, 0.45), 0.20, 0.16, "Prompt-only\nevidence-first review", "#fff3cd", ec=COLORS["yellow"])
    add_box(ax, (0.54, 0.56), 0.20, 0.18, "Tool-augmented\nverification", "#d8f3dc", ec=COLORS["green"], weight="bold")
    add_box(ax, (0.81, 0.70), 0.14, 0.12, "Accept", "#d8f3dc", ec=COLORS["green"], weight="bold")
    add_box(ax, (0.81, 0.54), 0.14, 0.12, "Reject", "#fde2e1", ec=COLORS["red"], weight="bold")
    add_box(ax, (0.81, 0.38), 0.14, 0.12, "Escalate", "#e9ecef", ec=COLORS["muted"], weight="bold")

    add_arrow(ax, (0.20, 0.65), (0.27, 0.78))
    add_arrow(ax, (0.20, 0.65), (0.27, 0.53))
    add_arrow(ax, (0.47, 0.78), (0.54, 0.67), color=COLORS["blue"])
    add_arrow(ax, (0.47, 0.53), (0.54, 0.63), color=COLORS["yellow"])
    add_arrow(ax, (0.74, 0.66), (0.81, 0.76), color=COLORS["green"])
    add_arrow(ax, (0.74, 0.63), (0.81, 0.60), color=COLORS["red"])
    add_arrow(ax, (0.74, 0.60), (0.81, 0.43), color=COLORS["muted"])

    ax.text(
        0.54,
        0.33,
        "Visible execution evidence: patch apply status + behavior summaries",
        fontsize=7.6,
        color=COLORS["green"],
        ha="left",
    )
    ax.text(0.25, 0.20, "Hidden evaluator labels and oracle paths remain unavailable to the reviewer.", fontsize=7.6, color=COLORS["muted"])
    save_figure(fig, out_dir, "fig1_framework")


def fig_evidence_visibility(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.35))
    rows = [
        "Issue summary + patch diff",
        "Apply/static evidence",
        "F2P/P2P test outcomes",
        "Tool / behavior summary",
        "Evaluator truth labels",
    ]
    cols = ["E0", "E2", "E4", "E6"]
    matrix = np.array(
        [
            [1, 1, 1, 1],
            [0, 1, 1, 1],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [0, 0, 0, 0],
        ]
    )
    color_map = np.empty(matrix.shape, dtype=object)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            color_map[i, j] = COLORS["green"] if matrix[i, j] else COLORS["gray"]
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            edge = COLORS["red"] if i == matrix.shape[0] - 1 else "white"
            ax.add_patch(Rectangle((j, i), 1, 1, facecolor=color_map[i, j], edgecolor=edge, linewidth=1.5))
            ax.text(
                j + 0.5,
                i + 0.5,
                "visible" if matrix[i, j] else "hidden",
                ha="center",
                va="center",
                fontsize=8,
                color=COLORS["ink"],
            )
    ax.set_xlim(0, len(cols))
    ax.set_ylim(0, len(rows))
    ax.invert_yaxis()
    ax.set_xticks(np.arange(len(cols)) + 0.5, cols)
    ax.set_yticks(np.arange(len(rows)) + 0.5, rows)
    ax.tick_params(length=0)
    ax.set_title("EVP-7 evidence visibility boundary by level", loc="left", weight="bold")
    fig.text(
        0.30,
        0.07,
        "Evaluator truth labels include reference correctness, hidden final labels, and final oracle outcomes; "
        "they never enter the reviewer prompt and are used only for metric computation.",
        fontsize=7.2,
        color=COLORS["muted"],
    )
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.subplots_adjust(left=0.30, right=0.98, top=0.84, bottom=0.22)
    save_figure(fig, out_dir, "fig2_evidence_visibility")


def fig_dataset(out_dir: Path, dataset_summary: dict[str, Any]) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.8), gridspec_kw={"width_ratios": [1.0, 1.3, 1.0]})
    fig.suptitle("Pilot dataset composition and executable validation", x=0.02, y=1.03, ha="left", weight="bold", fontsize=12)

    project_counts = dataset_summary["project_counts"]
    axes[0].bar(project_counts.keys(), project_counts.values(), color=[COLORS["blue"], COLORS["cyan"]], width=0.65)
    axes[0].set_ylabel("Candidates")
    axes[0].set_title("Projects", loc="left", fontsize=10, weight="bold")
    axes[0].grid(axis="y", color=COLORS["grid"], linewidth=0.7)

    type_counts = dataset_summary["candidate_type_counts"]
    type_labels = ["Correct\nreference", "Buggy\nnoop", "Irrelevant\npatch", "Partial\nfix"]
    type_values = [type_counts["correct_reference"], type_counts["buggy_noop"], type_counts["irrelevant_patch"], type_counts["partial_fix"]]
    axes[1].bar(type_labels, type_values, color=[COLORS["green"], COLORS["gray"], COLORS["purple"], COLORS["orange"]], width=0.68)
    axes[1].set_title("Candidate types", loc="left", fontsize=10, weight="bold")
    axes[1].grid(axis="y", color=COLORS["grid"], linewidth=0.7)

    validation = [dataset_summary["candidate_count"], dataset_summary["candidate_count"], dataset_summary["expected_outcome_counts"]["correct"]]
    axes[2].bar(["Patch\napplied", "Oracle\nran", "Oracle\npassed"], validation, color=[COLORS["blue"], COLORS["cyan"], COLORS["green"]], width=0.65)
    axes[2].set_title("Executable validation", loc="left", fontsize=10, weight="bold")
    axes[2].grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    axes[2].set_ylim(0, max(validation) + 5)

    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(axis="x", rotation=0)
    save_figure(fig, out_dir, "fig3_dataset_composition")


def fig_result_tradeoff(out_dir: Path, metrics: dict[str, dict[str, float]]) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    labels = list(metrics.keys())
    x = np.arange(len(labels))
    width = 0.18
    series = [
        ("False accept", "false_accept_rate", COLORS["red"]),
        ("Accepted precision", "accepted_precision", COLORS["blue"]),
        ("Correct recall", "correct_patch_recall", COLORS["green"]),
        ("Invalid output", "invalid_output_rate", COLORS["purple"]),
    ]
    for idx, (name, key, color) in enumerate(series):
        values = [float(metrics[label].get(key, 0.0) or 0.0) for label in labels]
        offset = (idx - 1.5) * width
        bars = ax.bar(x + offset, values, width=width, label=name, color=color)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{value:.2f}", ha="center", va="bottom", fontsize=7)
    ax.axhline(1.0, color=COLORS["grid"], linewidth=0.8)
    ax.set_ylim(0, 1.18)
    ax.set_xticks(x, labels)
    ax.set_ylabel("Rate")
    ax.set_title("Safety/recall tradeoff across review conditions", loc="left", weight="bold")
    ax.legend(ncol=4, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.18))
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    save_figure(fig, out_dir, "fig4_result_tradeoff")


def fig_claim_boundary(out_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.02, 0.94, "What the evidence supports", fontsize=13, weight="bold", color=COLORS["ink"])

    add_box(ax, (0.05, 0.62), 0.25, 0.18, "LLM-only\nplausibility review", "#dbeafe", ec=COLORS["blue"], weight="bold")
    add_box(ax, (0.38, 0.62), 0.25, 0.18, "Prompt-only\nevidence-first", "#fff3cd", ec=COLORS["yellow"], weight="bold")
    add_box(ax, (0.70, 0.62), 0.25, 0.18, "Tool-augmented\nevidence verifier", "#d8f3dc", ec=COLORS["green"], weight="bold")
    add_arrow(ax, (0.30, 0.71), (0.38, 0.71), COLORS["muted"])
    add_arrow(ax, (0.63, 0.71), (0.70, 0.71), COLORS["muted"])

    ax.text(0.05, 0.48, "Evidence:\naccepts partial fixes", fontsize=8.5, color=COLORS["red"])
    ax.text(0.38, 0.48, "Evidence:\nzero observed false accepts\nbut recall drops", fontsize=8.5, color=COLORS["orange"])
    ax.text(0.70, 0.48, "Evidence:\nzero false accepts\nand full recall", fontsize=8.5, color=COLORS["green"])

    add_box(ax, (0.05, 0.18), 0.25, 0.16, "Claim boundary:\nunsafe merge gate", "#fde2e1", ec=COLORS["red"])
    add_box(ax, (0.38, 0.18), 0.25, 0.16, "Claim boundary:\nmixed/negative result", "#fff3cd", ec=COLORS["yellow"])
    add_box(ax, (0.70, 0.18), 0.25, 0.16, "Claim boundary:\nconditional tool-assisted\nverification", "#d8f3dc", ec=COLORS["green"])
    ax.text(0.03, 0.06, "Not supported: prompt-only evidence-first is generally better. Supported: executable evidence can repair this pilot's safety/recall tradeoff.", fontsize=8.5, color=COLORS["muted"])
    save_figure(fig, out_dir, "fig5_claim_boundary")


def fig_evp7_visibility_curve(out_dir: Path, evp7_summary: dict[str, Any]) -> None:
    groups = evp7_summary.get("metrics", {}).get("metric_groups", {})
    if not isinstance(groups, dict):
        raise ValueError("EVP-7 summary must contain metrics.metric_groups")
    levels = ["E0", "E2", "E4", "E6"]
    x = np.arange(len(levels))
    false_accept = [float(groups[level]["false_accept_rate"]) for level in levels]
    correct_recall = [float(groups[level]["correct_recall"]) for level in levels]
    escalation = [float(groups[level]["escalation_rate"]) for level in levels]
    accepted_precision = [
        float(groups[level]["accepted_precision"]) if groups[level].get("accepted_precision") is not None else np.nan
        for level in levels
    ]
    evidence_gain = [float(groups[level]["evidence_gain_vs_e0"]) for level in levels]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.35, 1.0]})
    fig.suptitle("EVP-7 evidence visibility curve", x=0.02, y=1.02, ha="left", weight="bold", fontsize=12)

    ax = axes[0]
    ax.plot(x, false_accept, marker="o", linewidth=2.0, color=COLORS["red"], label="False accept")
    ax.plot(x, correct_recall, marker="o", linewidth=2.0, color=COLORS["green"], label="Correct recall")
    ax.plot(x, escalation, marker="o", linewidth=2.0, color=COLORS["orange"], label="Escalation")
    ax.scatter(x, accepted_precision, marker="D", s=48, color=COLORS["blue"], label="Accepted precision", zorder=3)
    ax.set_xticks(x, levels)
    ax.set_ylim(-0.04, 1.05)
    ax.set_ylabel("Rate")
    ax.set_title("Merge-gate metrics by evidence level", loc="left", fontsize=10, weight="bold")
    ax.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18))

    ax2 = axes[1]
    bars = ax2.bar(levels, evidence_gain, color=[COLORS["gray"], COLORS["purple"], COLORS["cyan"], COLORS["green"]], width=0.65)
    ax2.axhline(0, color=COLORS["ink"], linewidth=0.8)
    ax2.set_title("Utility gain vs E0", loc="left", fontsize=10, weight="bold")
    ax2.set_ylabel("Evidence Gain")
    ax2.grid(axis="y", color=COLORS["grid"], linewidth=0.7)
    ax2.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, evidence_gain):
        va = "bottom" if value >= 0 else "top"
        y = value + (0.45 if value >= 0 else -0.45)
        ax2.text(bar.get_x() + bar.get_width() / 2, y, f"{value:.2f}", ha="center", va=va, fontsize=7.5)

    fig.text(
        0.02,
        -0.02,
        "376 real DeepSeek G5 records; E0/E2/E4/E6 each contain 94 candidates. "
        "Accepted precision is undefined for E2 because it accepted no patches.",
        fontsize=7.5,
        color=COLORS["muted"],
    )
    save_figure(fig, out_dir, "fig6_evp7_visibility_curve")


def write_manifest(out_dir: Path) -> None:
    manifest = {
        "figure_count": 6,
        "formats": ["pdf", "svg", "png"],
        "figures": [
            {"id": "fig1_framework", "purpose": "overall workflow"},
            {"id": "fig2_evidence_visibility", "purpose": "EVP-7 evidence-level visibility boundary"},
            {"id": "fig3_dataset_composition", "purpose": "dataset and validation"},
            {"id": "fig4_result_tradeoff", "purpose": "first-pilot API result metrics"},
            {"id": "fig5_claim_boundary", "purpose": "claim boundary and interpretation"},
            {"id": "fig6_evp7_visibility_curve", "purpose": "EVP-7 evidence visibility curve"},
        ],
    }
    (out_dir / "figure_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate publication figures for the patch-verification paper.")
    parser.add_argument("--out-dir", default="docs/figures")
    parser.add_argument("--dataset-summary", default="outputs/patch_verification_pilot_001/dataset_summary.json")
    parser.add_argument("--prompt-metrics", default="outputs/patch_verification_api_pilot_002/metrics.json")
    parser.add_argument("--tool-gate", default="outputs/patch_verification_tool_augmented_full_001/tool_augmented_full_gate.json")
    parser.add_argument("--evp7-summary", default="data/reviews/evp7_g5_llm_376_full_summary.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_style()
    out_dir = Path(args.out_dir)
    dataset_summary = read_json(Path(args.dataset_summary))
    prompt_metrics = read_json(Path(args.prompt_metrics))
    tool_gate = read_json(Path(args.tool_gate))
    evp7_summary = read_json(Path(args.evp7_summary))
    metrics = merged_metrics(prompt_metrics, tool_gate)

    fig_framework(out_dir)
    fig_evidence_visibility(out_dir)
    fig_dataset(out_dir, dataset_summary)
    fig_result_tradeoff(out_dir, metrics)
    fig_claim_boundary(out_dir)
    fig_evp7_visibility_curve(out_dir, evp7_summary)
    write_manifest(out_dir)
    print(json.dumps({"out_dir": str(out_dir), "figure_count": 6, "formats": ["pdf", "svg", "png"]}, indent=2))


if __name__ == "__main__":
    main()
