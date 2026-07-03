from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANUSCRIPT = REPO_ROOT / "docs" / "paper" / "ccfc_manuscript_rewrite_v0_1.md"
DEFAULT_OUT_JSON = REPO_ROOT / "data" / "reviews" / "ccfc_figure_placement_audit_v0_1.json"
DEFAULT_OUT_MD = REPO_ROOT / "docs" / "paper" / "ccfc_figure_placement_audit_v0_1.md"

EXPECTED = [
    {
        "id": "Fig. 1",
        "section": "## 3. Evidence-Visibility Protocol",
        "image": "../figures/ccfc/ccfc_fig1_protocol.png",
        "caption_marker": "**Figure 1. Hidden-evaluator evidence-visibility protocol.**",
        "assets": [
            "docs/figures/ccfc/ccfc_fig1_protocol.pdf",
            "docs/figures/ccfc/ccfc_fig1_protocol.svg",
            "docs/figures/ccfc/ccfc_fig1_protocol.png",
        ],
    },
    {
        "id": "Fig. 2",
        "section": "### 5.1 Evidence visibility changed five-model decision patterns",
        "image": "../figures/ccfc/ccfc_fig2_decision_patterns.png",
        "caption_marker": "**Figure 2. Five-model evidence-level decision patterns.**",
        "assets": [
            "docs/figures/ccfc/ccfc_fig2_decision_patterns.pdf",
            "docs/figures/ccfc/ccfc_fig2_decision_patterns.svg",
            "docs/figures/ccfc/ccfc_fig2_decision_patterns.png",
        ],
    },
    {
        "id": "Fig. 3",
        "section": "## 6. Discussion",
        "image": "../figures/ccfc/ccfc_fig3_claim_boundary.png",
        "caption_marker": "**Figure 3. Claim boundary and setting-validity map.**",
        "assets": [
            "docs/figures/ccfc/ccfc_fig3_claim_boundary.pdf",
            "docs/figures/ccfc/ccfc_fig3_claim_boundary.svg",
            "docs/figures/ccfc/ccfc_fig3_claim_boundary.png",
        ],
    },
]


def line_index(lines: list[str], needle: str) -> int | None:
    for idx, line in enumerate(lines, start=1):
        if needle in line:
            return idx
    return None


def resolve_markdown_image(manuscript: Path, image_ref: str) -> Path:
    return (manuscript.parent / image_ref).resolve()


def audit(manuscript: Path) -> dict[str, Any]:
    text = manuscript.read_text(encoding="utf-8")
    lines = text.splitlines()
    image_refs = re.findall(r"!\[[^\]]+\]\(([^)]+)\)", text)
    rows: list[dict[str, Any]] = []
    for expected in EXPECTED:
        section_line = line_index(lines, expected["section"])
        image_line = line_index(lines, f"]({expected['image']})")
        caption_line = line_index(lines, expected["caption_marker"])
        assets = [
            {
                "path": asset,
                "exists": (REPO_ROOT / asset).exists(),
                "non_empty": (REPO_ROOT / asset).exists() and (REPO_ROOT / asset).stat().st_size > 2000,
            }
            for asset in expected["assets"]
        ]
        resolved_image = resolve_markdown_image(manuscript, expected["image"])
        section_before_image = section_line is not None and image_line is not None and section_line < image_line
        caption_after_image = image_line is not None and caption_line is not None and image_line < caption_line
        rows.append(
            {
                "id": expected["id"],
                "section": expected["section"],
                "section_line": section_line,
                "image_ref": expected["image"],
                "image_line": image_line,
                "image_exists": resolved_image.exists(),
                "caption_line": caption_line,
                "section_before_image": section_before_image,
                "caption_after_image": caption_after_image,
                "assets": assets,
                "passed": bool(
                    section_before_image
                    and caption_after_image
                    and resolved_image.exists()
                    and all(asset["exists"] and asset["non_empty"] for asset in assets)
                ),
            }
        )
    order = [row["image_line"] for row in rows]
    ordered = all(isinstance(value, int) for value in order) and order == sorted(order)
    unique_images = sorted(image_refs) == sorted({item["image"] for item in EXPECTED})
    checks = {
        "all_figures_present": all(row["passed"] for row in rows),
        "figures_in_expected_order": ordered,
        "no_extra_markdown_images": unique_images,
        "asset_summary_present": "## Figure Asset Summary" in text,
    }
    return {
        "artifact_id": "ccfc_figure_placement_audit_v0_1",
        "manuscript": str(manuscript.relative_to(REPO_ROOT)).replace("\\", "/"),
        "figures": rows,
        "checks": checks,
        "status": "passed" if all(checks.values()) else "failed",
    }


def write_outputs(result: dict[str, Any], out_json: Path, out_md: Path) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# CCF-C Figure Placement Audit v0.1",
        "",
        f"- status: `{result['status']}`",
        f"- manuscript: `{result['manuscript']}`",
        "",
        "## Checks",
        "",
        "| check | passed |",
        "| --- | ---: |",
    ]
    for key, value in result["checks"].items():
        lines.append(f"| `{key}` | {str(value).lower()} |")
    lines += [
        "",
        "## Figure Placement",
        "",
        "| figure | section line | image line | caption line | passed |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in result["figures"]:
        lines.append(
            f"| {row['id']} | {row['section_line']} | {row['image_line']} | "
            f"{row['caption_line']} | {str(row['passed']).lower()} |"
        )
    lines.append("")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manuscript", type=Path, default=DEFAULT_MANUSCRIPT)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = audit(args.manuscript)
    write_outputs(result, args.out_json, args.out_md)
    if args.check and result["status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
