from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


DETERMINISTIC_FILES = [
    "candidates.jsonl",
    "evidence_packets.jsonl",
    "verifier_outputs.jsonl",
    "dataset_summary.json",
    "metrics.json",
    "validation_summary.json",
    "pilot_report.md",
]

VOLATILE_FILES = [
    "validation.jsonl",
    "api_pilot_dry_run_config.json",
    "api_prompt_dry_run/prompt_manifest.jsonl",
    "pipeline_summary.json",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def line_count(path: Path) -> int | None:
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except UnicodeDecodeError:
        return None


def file_record(run_dir: Path, relative_path: str) -> dict[str, Any]:
    path = run_dir / relative_path
    if not path.exists():
        return {
            "exists": False,
            "path": relative_path,
            "bytes": None,
            "nonempty_lines": None,
            "sha256": None,
        }
    return {
        "exists": True,
        "path": relative_path,
        "bytes": path.stat().st_size,
        "nonempty_lines": line_count(path),
        "sha256": sha256_file(path),
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_manifest(run_dir: Path) -> dict[str, Any]:
    deterministic = {name: file_record(run_dir, name) for name in DETERMINISTIC_FILES}
    volatile = {name: file_record(run_dir, name) for name in VOLATILE_FILES}
    return {
        "run_dir": run_dir.as_posix(),
        "deterministic_files": deterministic,
        "volatile_files": volatile,
        "deterministic_file_count": len(deterministic),
        "deterministic_missing": [
            name for name, record in deterministic.items() if not record["exists"]
        ],
    }


def compare_manifests(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    ref_files = reference.get("deterministic_files", {})
    cand_files = candidate.get("deterministic_files", {})
    if not isinstance(ref_files, dict) or not isinstance(cand_files, dict):
        raise ValueError("Both manifests must contain deterministic_files objects")

    all_names = sorted(set(ref_files) | set(cand_files))
    matches: list[str] = []
    mismatches: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []

    for name in all_names:
        ref_record = ref_files.get(name)
        cand_record = cand_files.get(name)
        if not isinstance(ref_record, dict) or not ref_record.get("exists"):
            missing.append({"file": name, "side": "reference"})
            continue
        if not isinstance(cand_record, dict) or not cand_record.get("exists"):
            missing.append({"file": name, "side": "candidate"})
            continue
        if ref_record.get("sha256") == cand_record.get("sha256"):
            matches.append(name)
        else:
            mismatches.append(
                {
                    "file": name,
                    "reference_sha256": ref_record.get("sha256"),
                    "candidate_sha256": cand_record.get("sha256"),
                    "reference_bytes": ref_record.get("bytes"),
                    "candidate_bytes": cand_record.get("bytes"),
                }
            )

    return {
        "reference_run_dir": reference.get("run_dir"),
        "candidate_run_dir": candidate.get("run_dir"),
        "matched": not missing and not mismatches,
        "matched_files": matches,
        "missing": missing,
        "mismatches": mismatches,
        "checked_file_count": len(all_names),
    }


def build_markdown(compare: dict[str, Any]) -> str:
    lines = [
        "# Reproducibility Comparison",
        "",
        "## Summary",
        "",
        f"- matched: {'yes' if compare['matched'] else 'no'}",
        f"- checked deterministic files: {compare['checked_file_count']}",
        f"- matched files: {len(compare['matched_files'])}",
        f"- missing files: {len(compare['missing'])}",
        f"- mismatched files: {len(compare['mismatches'])}",
        f"- reference run: `{compare['reference_run_dir']}`",
        f"- candidate run: `{compare['candidate_run_dir']}`",
        "",
    ]
    if compare["mismatches"]:
        lines.extend(["## Mismatches", ""])
        for item in compare["mismatches"]:
            lines.append(
                f"- `{item['file']}`: reference `{item['reference_sha256']}`, "
                f"candidate `{item['candidate_sha256']}`"
            )
        lines.append("")
    if compare["missing"]:
        lines.extend(["## Missing Files", ""])
        for item in compare["missing"]:
            lines.append(f"- `{item['file']}` missing on {item['side']}")
        lines.append("")
    lines.extend(
        [
            "## Scope",
            "",
            "This comparison covers deterministic no-API output files only. "
            "Runtime work directories, raw API responses, and other environment-dependent files are not treated as reproducibility evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write and compare no-API reproducibility manifests.")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--compare-to")
    parser.add_argument("--compare-out")
    parser.add_argument("--compare-md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_manifest(Path(args.run_dir))
    write_json(Path(args.out), manifest)
    result: dict[str, Any] = {"manifest": args.out}

    if args.compare_to:
        compare = compare_manifests(read_json(Path(args.compare_to)), manifest)
        compare_out = Path(args.compare_out) if args.compare_out else Path(args.out).with_name("reproducibility_compare.json")
        write_json(compare_out, compare)
        result["compare"] = str(compare_out)
        result["matched"] = compare["matched"]
        if args.compare_md:
            compare_md = Path(args.compare_md)
            compare_md.parent.mkdir(parents=True, exist_ok=True)
            compare_md.write_text(build_markdown(compare), encoding="utf-8")
            result["compare_md"] = str(compare_md)

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
