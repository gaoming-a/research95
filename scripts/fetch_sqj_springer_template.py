from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path
from typing import Any


OFFICIAL_AUTHOR_SUPPORT_URL = "https://www.springernature.com/gp/authors/campaigns/latex-author-support"
OFFICIAL_TEMPLATE_ZIP_URL = "https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12"
DEFAULT_OUTPUT_DIR = Path("outputs/sqj_springer_template")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_mark(value: Any) -> str:
    return "yes" if bool(value) else "no"


def safe_extract(zip_path: Path, extract_dir: Path) -> list[str]:
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[str] = []
    root = extract_dir.resolve()
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            target = (extract_dir / member.filename).resolve()
            if root != target and root not in target.parents:
                raise ValueError(f"unsafe ZIP member path: {member.filename}")
            archive.extract(member, extract_dir)
            if not member.is_dir():
                extracted.append(member.filename)
    return sorted(extracted)


def fetch_template(output_dir: Path = DEFAULT_OUTPUT_DIR, url: str = OFFICIAL_TEMPLATE_ZIP_URL) -> dict[str, Any]:
    zip_path = output_dir / "springer-nature-latex-template.zip"
    extract_dir = output_dir / "extracted"
    output_dir.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "research95-template-audit/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
        content_type = response.headers.get("Content-Type")
        content_length = response.headers.get("Content-Length")
    zip_path.write_bytes(payload)
    zip_sha256 = sha256_file(zip_path)
    extracted_files = safe_extract(zip_path, extract_dir)
    sn_jnl_files = sorted(str(path.as_posix()) for path in extract_dir.rglob("sn-jnl.cls"))
    bst_files = sorted(str(path.as_posix()) for path in extract_dir.rglob("*.bst"))
    cls_files = sorted(str(path.as_posix()) for path in extract_dir.rglob("*.cls"))
    result = {
        "audit_id": "sqj_springer_template_fetch",
        "official_author_support_url": OFFICIAL_AUTHOR_SUPPORT_URL,
        "official_template_zip_url": url,
        "output_dir": output_dir.as_posix(),
        "zip_path": zip_path.as_posix(),
        "extract_dir": extract_dir.as_posix(),
        "content_type": content_type,
        "content_length": content_length,
        "zip_size_bytes": zip_path.stat().st_size,
        "zip_sha256": zip_sha256,
        "extracted_file_count": len(extracted_files),
        "sn_jnl_cls_files": sn_jnl_files,
        "bst_files": bst_files,
        "cls_files": cls_files,
        "api_call_attempted": False,
        "raw_model_outputs_read": False,
        "tracked_template_files_committed": False,
        "passed": bool(sn_jnl_files),
    }
    result["gate_status"] = "springer_template_cached" if result["passed"] else "blocked_missing_sn_jnl_cls_in_zip"
    return result


def build_markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# SQJ Springer Template Fetch",
        "",
        "## Summary",
        "",
        f"- passed: {bool_mark(audit['passed'])}",
        f"- gate status: `{audit['gate_status']}`",
        f"- official author support URL: {audit['official_author_support_url']}",
        f"- official template ZIP URL: {audit['official_template_zip_url']}",
        f"- ZIP sha256: `{audit['zip_sha256']}`",
        f"- ZIP size bytes: {audit['zip_size_bytes']}",
        f"- extracted files: {audit['extracted_file_count']}",
        f"- sn-jnl.cls files: {len(audit['sn_jnl_cls_files'])}",
        f"- .bst files: {len(audit['bst_files'])}",
        f"- API call attempted: {bool_mark(audit['api_call_attempted'])}",
        f"- raw model outputs read: {bool_mark(audit['raw_model_outputs_read'])}",
        f"- tracked template files committed: {bool_mark(audit['tracked_template_files_committed'])}",
        "",
        "## sn-jnl.cls",
        "",
    ]
    if audit["sn_jnl_cls_files"]:
        lines.extend(f"- `{path}`" for path in audit["sn_jnl_cls_files"])
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The downloaded ZIP and extracted Springer Nature template files live under ignored `outputs/`. This report records the source and checksum only; it does not commit third-party template files, submit the manuscript, or mark final freeze complete.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch the official Springer Nature LaTeX journal template into an ignored local cache.")
    parser.add_argument("--url", default=OFFICIAL_TEMPLATE_ZIP_URL)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--out-json", default="outputs/sqj_springer_template/latest.json")
    parser.add_argument("--out-md", default="docs/experiments/sqj_springer_template_fetch.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    audit = fetch_template(Path(args.output_dir), args.url)
    write_json(Path(args.out_json), audit)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(build_markdown(audit), encoding="utf-8")
    print(
        json.dumps(
            {
                "out_json": args.out_json,
                "out_md": args.out_md,
                "passed": audit["passed"],
                "gate_status": audit["gate_status"],
            },
            indent=2,
        )
    )
    if not audit["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
