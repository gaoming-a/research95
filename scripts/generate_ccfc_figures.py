from __future__ import annotations

import argparse
import json
from pathlib import Path
from textwrap import wrap
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "figures" / "ccfc"
CLAIM_MAP_PATH = ROOT / "data" / "reviews" / "final_manuscript_claim_map_v0_1.json"
FORMATS = ("pdf", "svg", "png")
LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5", "E6")
MODEL_ORDER = (
    "deepseek/deepseek-v4-pro",
    "qwen/qwen3.7-max",
    "moonshotai/kimi-k2.6",
    "mistralai/devstral-2512",
    "google/gemini-2.5-flash",
)
MODEL_LABELS = {
    "deepseek/deepseek-v4-pro": "DeepSeek\nV4 Pro",
    "qwen/qwen3.7-max": "Qwen3.7\nMax",
    "moonshotai/kimi-k2.6": "Kimi\nK2.6",
    "mistralai/devstral-2512": "Devstral\n2",
    "google/gemini-2.5-flash": "Gemini 2.5\nFlash",
}

COLORS = {
    "ink": "#252A31",
    "muted": "#667085",
    "grid": "#D7DEE8",
    "paper": "#FFFFFF",
    "blue": "#2E5E9E",
    "blue_soft": "#DCE9F8",
    "teal": "#2C8C82",
    "teal_soft": "#DDF3EF",
    "green": "#4F8A5B",
    "green_soft": "#E1F1E4",
    "orange": "#D97A3A",
    "orange_soft": "#F7E3D1",
    "red": "#B84A4A",
    "red_soft": "#F3D6D6",
    "purple": "#6E5B9A",
    "purple_soft": "#E6E0F4",
    "gray": "#EEF1F4",
    "gray_2": "#CBD3DC",
    "gray_3": "#8792A2",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def apply_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 7,
            "axes.titlesize": 8,
            "axes.labelsize": 7,
            "xtick.labelsize": 6.5,
            "ytick.labelsize": 6.5,
            "legend.fontsize": 6.5,
            "legend.frameon": False,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.75,
            "figure.facecolor": COLORS["paper"],
            "axes.facecolor": COLORS["paper"],
            "savefig.facecolor": COLORS["paper"],
            "svg.hashsalt": "research95-ccfc-figures",
        }
    )


def strip_trailing_whitespace(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(line.rstrip() for line in lines) + "\n", encoding="utf-8")


def save_figure(fig: plt.Figure, stem: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in FORMATS:
        path = OUT_DIR / f"{stem}.{suffix}"
        metadata = {"Creator": "research95 scripts/generate_ccfc_figures.py"}
        if suffix == "svg":
            metadata["Date"] = None
        elif suffix == "pdf":
            metadata["CreationDate"] = None
            metadata["ModDate"] = None
        fig.savefig(path, bbox_inches="tight", dpi=360, metadata=metadata)
        if suffix == "svg":
            strip_trailing_whitespace(path)
    plt.close(fig)


def text_block(ax: plt.Axes, x: float, y: float, text: str, width: int, **kwargs: Any) -> None:
    ax.text(x, y, "\n".join(wrap(text, width=width)), **kwargs)


def add_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    label: str,
    fill: str,
    edge: str,
    fontsize: float = 7.0,
    weight: str = "regular",
) -> None:
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=0.9,
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
        linespacing=1.12,
    )


def add_arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str) -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=11, linewidth=1.0, color=color))


def add_panel_label(ax: plt.Axes, label: str, x: float = -0.02, y: float = 1.02) -> None:
    ax.text(x, y, label, transform=ax.transAxes, ha="left", va="bottom", fontsize=8, weight="bold")


def model_level_matrices(claim_map: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows = claim_map.get("per_model_level_counts")
    if not isinstance(rows, list):
        raise ValueError("claim map missing per_model_level_counts")
    reject = np.zeros((len(MODEL_ORDER), len(LEVELS)), dtype=float)
    escalate = np.zeros_like(reject)
    accept = np.zeros_like(reject)
    by_level = {row.get("level"): row for row in rows if isinstance(row, dict)}
    for level_idx, level in enumerate(LEVELS):
        row = by_level.get(level)
        if not isinstance(row, dict):
            raise ValueError(f"claim map missing level {level}")
        for model_idx, model in enumerate(MODEL_ORDER):
            counts = row.get(model)
            if not isinstance(counts, dict):
                raise ValueError(f"claim map missing {model} at {level}")
            reject[model_idx, level_idx] = float(counts.get("reject", 0) or 0)
            escalate[model_idx, level_idx] = float(counts.get("escalate", 0) or 0)
            accept[model_idx, level_idx] = float(counts.get("accept", 0) or 0)
    return reject, escalate, accept


def fig1_protocol(claim_map: dict[str, Any]) -> None:
    fig = plt.figure(figsize=(7.3, 4.05))
    grid = fig.add_gridspec(2, 1, height_ratios=[1.25, 0.8], hspace=0.18)
    ax = fig.add_subplot(grid[0, 0])
    ax2 = fig.add_subplot(grid[1, 0])
    for axis in (ax, ax2):
        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        axis.axis("off")

    add_panel_label(ax, "a")
    ax.text(0.02, 0.98, "Hidden-evaluator evidence-visibility protocol", fontsize=10.5, weight="bold", va="top")
    ax.text(
        0.02,
        0.83,
        "Model-visible packets are separated from evaluator-only labels until after the merge-gate decision.",
        fontsize=7.2,
        color=COLORS["muted"],
    )

    add_box(ax, (0.04, 0.53), 0.15, 0.18, "98 candidate\npatches", COLORS["blue_soft"], COLORS["blue"], weight="bold")
    add_box(ax, (0.26, 0.66), 0.19, 0.14, "Visible evidence\nlevels E0-E6", COLORS["teal_soft"], COLORS["teal"], weight="bold")
    add_box(ax, (0.26, 0.37), 0.19, 0.14, "Evaluator-only\nlabels withheld", COLORS["gray"], COLORS["gray_3"])
    add_box(ax, (0.53, 0.53), 0.16, 0.18, "5 model\nverifiers", COLORS["orange_soft"], COLORS["orange"], weight="bold")
    add_box(ax, (0.78, 0.69), 0.15, 0.10, "escalate", COLORS["gray"], COLORS["gray_3"], weight="bold")
    add_box(ax, (0.78, 0.53), 0.15, 0.10, "reject", COLORS["red_soft"], COLORS["red"], weight="bold")
    add_box(ax, (0.78, 0.37), 0.15, 0.10, "accept\n0 observed", COLORS["green_soft"], COLORS["green"])
    add_box(ax, (0.53, 0.18), 0.40, 0.10, "Post-decision join: hidden labels support analysis only", COLORS["purple_soft"], COLORS["purple"])

    add_arrow(ax, (0.19, 0.62), (0.26, 0.73), COLORS["blue"])
    add_arrow(ax, (0.45, 0.73), (0.53, 0.63), COLORS["teal"])
    add_arrow(ax, (0.69, 0.63), (0.78, 0.74), COLORS["gray_3"])
    add_arrow(ax, (0.69, 0.62), (0.78, 0.58), COLORS["red"])
    add_arrow(ax, (0.69, 0.61), (0.78, 0.42), COLORS["green"])
    add_arrow(ax, (0.36, 0.37), (0.58, 0.28), COLORS["purple"])
    add_arrow(ax, (0.86, 0.37), (0.82, 0.28), COLORS["purple"])

    add_panel_label(ax2, "b")
    ax2.text(0.02, 0.92, "Figure contract", fontsize=8.5, weight="bold", va="top")
    cards = [
        ("Scale", "98 candidates x 7 levels x 5 models = 3430 parse-valid decisions", COLORS["blue_soft"], COLORS["blue"]),
        ("Boundary", "No raw response text; hidden labels joined only after model decisions", COLORS["purple_soft"], COLORS["purple"]),
        ("Claim", "Evidence visibility shapes risk behavior, not autonomous correctness verification", COLORS["green_soft"], COLORS["green"]),
    ]
    x0 = 0.03
    for idx, (title, body, fill, edge) in enumerate(cards):
        x = x0 + idx * 0.315
        ax2.add_patch(Rectangle((x, 0.18), 0.285, 0.50, linewidth=0.9, edgecolor=edge, facecolor=fill))
        ax2.text(x + 0.02, 0.58, title, fontsize=7.4, weight="bold", color=COLORS["ink"])
        text_block(ax2, x + 0.02, 0.49, body, width=33, fontsize=6.6, color=COLORS["ink"], va="top", linespacing=1.15)

    save_figure(fig, "ccfc_fig1_protocol")


def fig2_decision_patterns(claim_map: dict[str, Any]) -> None:
    reject, escalate, accept = model_level_matrices(claim_map)
    aggregate_reject = reject.sum(axis=0)
    aggregate_escalate = escalate.sum(axis=0)
    aggregate_accept = accept.sum(axis=0)

    fig = plt.figure(figsize=(7.4, 4.65))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.25, 0.90], width_ratios=[1.2, 0.8], hspace=0.50, wspace=0.38)
    ax_heat = fig.add_subplot(grid[0, :])
    ax_stack = fig.add_subplot(grid[1, 0])
    ax_note = fig.add_subplot(grid[1, 1])
    fig.suptitle("Five-model evidence-level decision patterns", x=0.02, y=0.995, ha="left", fontsize=10.5, weight="bold")

    add_panel_label(ax_heat, "a", y=1.07)
    max_reject = max(40.0, float(reject.max()))
    im = ax_heat.imshow(reject, cmap="YlOrRd", vmin=0, vmax=max_reject, aspect="auto")
    for r in range(reject.shape[0]):
        for c in range(reject.shape[1]):
            val = int(reject[r, c])
            ax_heat.text(c, r, f"{val}", ha="center", va="center", fontsize=6.7, color=COLORS["ink"])
    ax_heat.set_xticks(np.arange(len(LEVELS)), LEVELS)
    ax_heat.set_yticks(np.arange(len(MODEL_ORDER)), [MODEL_LABELS[m] for m in MODEL_ORDER])
    ax_heat.set_title("Reject decisions per 98 packets; escalation dominates most cells", loc="left", fontsize=8.2, weight="bold")
    ax_heat.tick_params(length=0)
    for spine in ax_heat.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.028, pad=0.015)
    cbar.set_label("reject count", fontsize=6.5)
    cbar.ax.tick_params(labelsize=6.2)

    add_panel_label(ax_stack, "b", x=-0.055, y=1.10)
    x = np.arange(len(LEVELS))
    ax_stack.bar(x, aggregate_escalate, color=COLORS["gray_2"], width=0.64, label="escalate")
    ax_stack.bar(x, aggregate_reject, bottom=aggregate_escalate, color=COLORS["red"], width=0.64, label="reject")
    if aggregate_accept.any():
        ax_stack.bar(
            x,
            aggregate_accept,
            bottom=aggregate_escalate + aggregate_reject,
            color=COLORS["green"],
            width=0.64,
            label="accept",
        )
    ax_stack.set_xticks(x, LEVELS)
    ax_stack.set_ylabel("aggregate decisions")
    ax_stack.set_ylim(0, 515)
    ax_stack.grid(axis="y", color=COLORS["grid"], linewidth=0.65)
    ax_stack.set_title("Aggregate pattern is not monotonic", loc="left", fontsize=8.2, weight="bold")
    ax_stack.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.50, -0.22))
    for idx, val in enumerate(aggregate_reject):
        ax_stack.text(idx, aggregate_escalate[idx] + val + 8, f"R{int(val)}", ha="center", fontsize=6.5, color=COLORS["red"])

    add_panel_label(ax_note, "c", x=-0.055, y=1.10)
    ax_note.axis("off")
    ax_note.set_title("Interpretation boundary", loc="left", fontsize=8.2, weight="bold")
    notes = [
        ("Supported", "evidence visibility changes behavior"),
        ("Qualified", "model-dependent and non-monotonic"),
        ("Not shown", "autonomous correctness verification"),
    ]
    for idx, (head, body) in enumerate(notes):
        y = 0.82 - idx * 0.31
        color = [COLORS["green_soft"], COLORS["orange_soft"], COLORS["red_soft"]][idx]
        edge = [COLORS["green"], COLORS["orange"], COLORS["red"]][idx]
        ax_note.add_patch(Rectangle((0.02, y - 0.16), 0.94, 0.22, linewidth=0.85, edgecolor=edge, facecolor=color))
        ax_note.text(0.06, y + 0.010, head, fontsize=7.0, weight="bold", va="center")
        text_block(ax_note, 0.06, y - 0.045, body, width=42, fontsize=6.15, va="top", color=COLORS["ink"])

    save_figure(fig, "ccfc_fig2_decision_patterns")


def claim_source_matrix(claims: list[dict[str, Any]]) -> tuple[list[str], np.ndarray]:
    sources = [
        "five-model\nsynthesis",
        "accept-aware\nrepair",
        "no-verdict /\ncontestation",
        "realistic\ngate",
        "validity\naudit",
    ]
    matrix = np.zeros((len(claims), len(sources)), dtype=float)
    for idx, claim in enumerate(claims):
        evidence = " ".join(str(x) for x in claim.get("evidence", []))
        claim_id = str(claim.get("id", ""))
        if "five_model" in evidence or "per-level" in evidence:
            matrix[idx, 0] = 1
        if "accept_aware" in evidence or "label_conditioned" in evidence or claim_id == "C3":
            matrix[idx, 1] = 1
        if "no_verdict" in evidence or "tool_contestation" in evidence or "EVP-8-HARD" in evidence:
            matrix[idx, 2] = 1
        if "realistic" in evidence or claim_id == "C6":
            matrix[idx, 3] = 1
        matrix[idx, 4] = 1
    return sources, matrix


def fig3_claim_boundary(claim_map: dict[str, Any]) -> None:
    claims = claim_map.get("claims")
    checks = claim_map.get("checks")
    forbidden = claim_map.get("forbidden_claims")
    if not isinstance(claims, list) or not isinstance(checks, list) or not isinstance(forbidden, list):
        raise ValueError("claim map missing claims/checks/forbidden_claims")
    status_labels = {
        "supported": "supported",
        "supported_as_setting_repair": "repair",
        "supported_qualified": "qualified",
        "supported_negative_boundary": "negative boundary",
    }
    claim_rows = [
        f"{claim.get('id')}: {status_labels.get(str(claim.get('status')), str(claim.get('status')))}"
        for claim in claims
        if isinstance(claim, dict)
    ]
    sources, matrix = claim_source_matrix([c for c in claims if isinstance(c, dict)])

    fig = plt.figure(figsize=(7.5, 4.65))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.15, 0.85], width_ratios=[1.25, 0.95], hspace=0.44, wspace=0.28)
    ax_matrix = fig.add_subplot(grid[:, 0])
    ax_checks = fig.add_subplot(grid[0, 1])
    ax_forbidden = fig.add_subplot(grid[1, 1])
    fig.suptitle("Claim boundary and setting-validity map", x=0.02, y=0.995, ha="left", fontsize=10.5, weight="bold")

    add_panel_label(ax_matrix, "a", y=1.08)
    im = ax_matrix.imshow(matrix, cmap=matplotlib.colors.ListedColormap([COLORS["gray"], COLORS["green_soft"]]), vmin=0, vmax=1, aspect="auto")
    _ = im
    ax_matrix.set_xticks(np.arange(len(sources)), sources)
    ax_matrix.set_yticks(np.arange(len(claim_rows)), claim_rows)
    ax_matrix.set_title("Each paper claim is bounded by tracked evidence", loc="left", fontsize=8.2, weight="bold")
    ax_matrix.tick_params(length=0)
    for r in range(matrix.shape[0]):
        for c in range(matrix.shape[1]):
            ax_matrix.text(c, r, "x" if matrix[r, c] else "", ha="center", va="center", fontsize=7.2, weight="bold", color=COLORS["green"])
    for spine in ax_matrix.spines.values():
        spine.set_visible(False)
    ax_matrix.set_xticklabels(sources, rotation=28, ha="right", rotation_mode="anchor")

    add_panel_label(ax_checks, "b", x=-0.055, y=1.12)
    ax_checks.axis("off")
    ax_checks.set_title("Validity gates", loc="left", fontsize=8.2, weight="bold")
    compact_checks = [
        ("validity audit", "passed with bounded claims"),
        ("five-model synthesis", "passed"),
        ("tool-contestation", "risk triage, not strict correction"),
        ("realistic gate", "26/30 cases; 2/3 projects"),
    ]
    for idx, (head, body) in enumerate(compact_checks):
        y = 0.86 - idx * 0.22
        fill = COLORS["green_soft"] if idx < 3 else COLORS["orange_soft"]
        edge = COLORS["green"] if idx < 3 else COLORS["orange"]
        ax_checks.add_patch(Rectangle((0.02, y - 0.14), 0.94, 0.17, linewidth=0.85, edgecolor=edge, facecolor=fill))
        ax_checks.text(0.06, y + 0.005, head, fontsize=6.9, weight="bold", va="center")
        text_block(ax_checks, 0.06, y - 0.040, body, width=42, fontsize=6.2, va="top", color=COLORS["ink"])

    add_panel_label(ax_forbidden, "c", x=-0.055, y=1.12)
    ax_forbidden.axis("off")
    ax_forbidden.set_title("Forbidden overclaims", loc="left", fontsize=8.2, weight="bold")
    short_forbidden = [
        "reliable autonomous correctness verifier",
        "monotonic evidence-level correctness gain",
        "escalation equals strict correction",
        "three-project realistic verifier readiness",
    ]
    for idx, item in enumerate(short_forbidden):
        y = 0.82 - idx * 0.21
        ax_forbidden.add_patch(Rectangle((0.03, y - 0.10), 0.08, 0.08, linewidth=0.85, edgecolor=COLORS["red"], facecolor=COLORS["red_soft"]))
        ax_forbidden.text(0.07, y - 0.06, "no", fontsize=5.8, weight="bold", ha="center", va="center", color=COLORS["red"])
        text_block(ax_forbidden, 0.15, y, item, width=43, fontsize=6.5, va="top", color=COLORS["ink"])

    save_figure(fig, "ccfc_fig3_claim_boundary")


def export_source_data(claim_map: dict[str, Any]) -> None:
    reject, escalate, accept = model_level_matrices(claim_map)
    source_data = {
        "source": str(CLAIM_MAP_PATH.relative_to(ROOT)).replace("\\", "/"),
        "backend": "python/matplotlib",
        "levels": list(LEVELS),
        "models": list(MODEL_ORDER),
        "reject_matrix": reject.astype(int).tolist(),
        "escalate_matrix": escalate.astype(int).tolist(),
        "accept_matrix": accept.astype(int).tolist(),
        "decision_totals_by_level": claim_map.get("decision_totals_by_level", {}),
        "claims": claim_map.get("claims", []),
        "checks": claim_map.get("checks", []),
        "forbidden_claims": claim_map.get("forbidden_claims", []),
        "figure_contract": {
            "core_conclusion": "Evidence visibility shapes LLM merge-gate risk behavior under bounded validity controls.",
            "backend": "Python",
            "archetypes": {
                "ccfc_fig1_protocol": "schematic-led composite",
                "ccfc_fig2_decision_patterns": "quantitative grid",
                "ccfc_fig3_claim_boundary": "asymmetric mixed-modality figure",
            },
            "export_formats": list(FORMATS),
            "source_data_needed": "tracked aggregate claim-map JSON only",
            "statistics_needed": "descriptive counts; no new inferential test",
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "figure_source_data.json").write_text(json.dumps(source_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_manifest() -> None:
    manifest = {
        "figure_count": 3,
        "backend": "python/matplotlib",
        "formats": list(FORMATS),
        "core_conclusion": "Evidence visibility shapes LLM merge-gate risk behavior, with claims bounded by the final setting-validity audit.",
        "figures": [
            {
                "id": "ccfc_fig1_protocol",
                "title": "Hidden-evaluator evidence-visibility protocol",
                "purpose": "show model-visible/evaluator-only separation and post-decision label join",
            },
            {
                "id": "ccfc_fig2_decision_patterns",
                "title": "Five-model evidence-level decision patterns",
                "purpose": "show model-dependent non-monotonic rejection/escalation patterns",
            },
            {
                "id": "ccfc_fig3_claim_boundary",
                "title": "Claim boundary and setting-validity map",
                "purpose": "show supported claims, validity gates, and forbidden overclaims",
            },
        ],
    }
    (OUT_DIR / "figure_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_qa_note() -> None:
    note = """# CCF-C Figure QA

Backend: Python / matplotlib only.

Generated figures:

- `ccfc_fig1_protocol`: schematic-led composite for the hidden-evaluator protocol.
- `ccfc_fig2_decision_patterns`: quantitative grid for five-model evidence-level patterns.
- `ccfc_fig3_claim_boundary`: asymmetric mixed-modality map for claim and validity boundaries.

Export contract:

- Formats: PDF, SVG, PNG.
- SVG text is configured with `svg.fonttype = none`.
- PDF text is configured with `pdf.fonttype = 42`.
- Source data: `figure_source_data.json`, derived from tracked aggregate claim-map JSON.
- Statistics: descriptive counts only; no new inferential test is introduced.

Review boundary:

- These figures support bounded evidence-conditioned risk-behavior claims.
- They do not support autonomous patch correctness verification, monotonic correctness improvement, or escalation-as-strict-correction claims.
"""
    (OUT_DIR / "figure_qa.md").write_text(note, encoding="utf-8")


def validate_outputs() -> None:
    stems = ("ccfc_fig1_protocol", "ccfc_fig2_decision_patterns", "ccfc_fig3_claim_boundary")
    missing: list[str] = []
    too_small: list[str] = []
    svg_without_text: list[str] = []
    for stem in stems:
        for suffix in FORMATS:
            path = OUT_DIR / f"{stem}.{suffix}"
            if not path.exists():
                missing.append(str(path))
                continue
            if path.stat().st_size < 2000:
                too_small.append(str(path))
            if suffix == "svg" and "<text" not in path.read_text(encoding="utf-8", errors="ignore"):
                svg_without_text.append(str(path))
    for extra in ("figure_manifest.json", "figure_source_data.json", "figure_qa.md"):
        path = OUT_DIR / extra
        if not path.exists():
            missing.append(str(path))
        elif path.stat().st_size < 100:
            too_small.append(str(path))
    if missing or too_small or svg_without_text:
        raise SystemExit(
            json.dumps(
                {
                    "missing": missing,
                    "too_small": too_small,
                    "svg_without_text": svg_without_text,
                },
                indent=2,
            )
        )


def generate() -> None:
    apply_style()
    claim_map = read_json(CLAIM_MAP_PATH)
    fig1_protocol(claim_map)
    fig2_decision_patterns(claim_map)
    fig3_claim_boundary(claim_map)
    export_source_data(claim_map)
    write_manifest()
    write_qa_note()
    validate_outputs()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate existing CCF-C figure outputs without regenerating")
    args = parser.parse_args()
    if args.check:
        validate_outputs()
    else:
        generate()


if __name__ == "__main__":
    main()
