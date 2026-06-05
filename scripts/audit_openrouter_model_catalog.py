from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


CATALOG_URL = "https://openrouter.ai/api/v1/models"


def fetch_catalog() -> list[dict[str, Any]]:
    request = Request(CATALOG_URL, headers={"User-Agent": "research95-model-catalog-audit/1.0"})
    with urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    data = payload.get("data", [])
    if not isinstance(data, list):
        raise ValueError("OpenRouter catalog payload must contain a data list")
    return [item for item in data if isinstance(item, dict)]


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def audit_models(slugs: list[str]) -> dict[str, Any]:
    catalog = fetch_catalog()
    by_id = {str(item.get("id")): item for item in catalog if item.get("id")}
    results = []
    for slug in slugs:
        item = by_id.get(slug)
        results.append(
            {
                "slug": slug,
                "available": item is not None,
                "name": item.get("name") if item else None,
                "context_length": item.get("context_length") if item else None,
                "created": item.get("created") if item else None,
            }
        )
    return {
        "audit_date": date.today().isoformat(),
        "catalog_url": CATALOG_URL,
        "catalog_model_count": len(catalog),
        "results": results,
        "all_available": all(item["available"] for item in results),
    }


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# OpenRouter Model Catalog Audit",
        "",
        "## Summary",
        "",
        f"- audit date: {audit['audit_date']}",
        f"- catalog URL: `{audit['catalog_url']}`",
        f"- catalog model count: {audit['catalog_model_count']}",
        f"- all requested slugs available: {bool_mark(audit['all_available'])}",
        "",
        "## Results",
        "",
        "| slug | available | name | context length |",
        "|---|---|---|---:|",
    ]
    for item in audit["results"]:
        lines.append(
            f"| `{item['slug']}` | {bool_mark(item['available'])} | "
            f"{item['name'] or ''} | {item['context_length'] or ''} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This audit only checks public OpenRouter catalog availability. It does not prove API-key access, pricing, provider routing, output quality, or paper suitability.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit whether candidate OpenRouter model slugs are visible in the public catalog.")
    parser.add_argument("--model", action="append", required=True, help="OpenRouter model slug. Can be repeated.")
    parser.add_argument("--out-json", default="outputs/model_selection/openrouter_catalog_audit.json")
    parser.add_argument("--out-md", default="outputs/model_selection/openrouter_catalog_audit.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = audit_models(args.model)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "all_available": audit["all_available"],
                "checked": len(audit["results"]),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    if not audit["all_available"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
