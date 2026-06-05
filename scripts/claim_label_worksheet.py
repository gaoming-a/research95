from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from cross_review.jsonl import read_jsonl, write_jsonl


READ_ONLY_COLUMNS = [
    "claim_label_id",
    "project",
    "bug_id",
    "candidate_id",
    "candidate_oracle_label",
    "reviewer",
    "claim_location",
    "claim_text",
    "target_behavior",
    "evidence_packet_path",
]
LABEL_COLUMNS = [
    "primary_label",
    "taxonomy_tags",
    "evidence_sources",
    "evidence_summary",
    "needs_additional_context",
    "labeler",
    "label_date",
]
CSV_COLUMNS = READ_ONLY_COLUMNS + LABEL_COLUMNS


def main() -> None:
    parser = argparse.ArgumentParser(description="Export or import real-bug claim-label worksheets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export claim-label JSONL to a CSV worksheet.")
    export_parser.add_argument("--labels", required=True, help="Input claim-label JSONL.")
    export_parser.add_argument("--out", required=True, help="Output CSV worksheet.")
    export_parser.add_argument(
        "--evidence-md-dir",
        help="Optional evidence packet markdown directory. Adds per-claim evidence packet path hints.",
    )
    export_parser.set_defaults(func=cmd_export)

    import_parser = subparsers.add_parser("import", help="Apply filled CSV worksheet labels to claim-label JSONL.")
    import_parser.add_argument("--labels", required=True, help="Input claim-label JSONL.")
    import_parser.add_argument("--worksheet", required=True, help="Filled CSV worksheet.")
    import_parser.add_argument("--out", required=True, help="Output updated claim-label JSONL.")
    import_parser.set_defaults(func=cmd_import)

    args = parser.parse_args()
    args.func(args)


def cmd_export(args: argparse.Namespace) -> None:
    records = read_jsonl(args.labels)
    evidence_dir = Path(args.evidence_md_dir) if args.evidence_md_dir else None
    rows = [record_to_csv_row(record, evidence_dir) for record in records]
    write_csv(Path(args.out), rows)
    print(f"exported_rows={len(rows)} out={args.out}")


def cmd_import(args: argparse.Namespace) -> None:
    records = read_jsonl(args.labels)
    worksheet_rows = read_csv(Path(args.worksheet))
    worksheet_by_id = {row["claim_label_id"]: row for row in worksheet_rows}

    missing = [record["claim_label_id"] for record in records if record["claim_label_id"] not in worksheet_by_id]
    if missing:
        raise SystemExit(f"Worksheet missing claim_label_id values: {missing[:5]}")

    updated: list[dict[str, Any]] = []
    for record in records:
        row = worksheet_by_id[str(record["claim_label_id"])]
        next_record = dict(record)
        next_record["primary_label"] = row.get("primary_label", "").strip()
        next_record["taxonomy_tags"] = split_list(row.get("taxonomy_tags", ""))
        next_record["evidence_sources"] = split_list(row.get("evidence_sources", ""))
        next_record["evidence_summary"] = row.get("evidence_summary", "").strip()
        next_record["needs_additional_context"] = parse_optional_bool(row.get("needs_additional_context", ""))
        next_record["labeler"] = row.get("labeler", "").strip()
        next_record["label_date"] = row.get("label_date", "").strip()
        updated.append(next_record)

    write_jsonl(args.out, updated)
    print(f"updated_rows={len(updated)} out={args.out}")


def record_to_csv_row(record: dict[str, Any], evidence_dir: Path | None) -> dict[str, str]:
    row: dict[str, str] = {}
    for column in READ_ONLY_COLUMNS:
        if column == "evidence_packet_path":
            row[column] = evidence_packet_path(record, evidence_dir)
        else:
            row[column] = stringify(record.get(column))
    for column in LABEL_COLUMNS:
        value = record.get(column)
        if isinstance(value, list):
            row[column] = ";".join(str(item) for item in value)
        elif value is None:
            row[column] = ""
        else:
            row[column] = str(value)
    return row


def evidence_packet_path(record: dict[str, Any], evidence_dir: Path | None) -> str:
    if evidence_dir is None:
        return ""
    packet_name = f"{record['claim_label_id']}.md"
    return str(evidence_dir / packet_name)


def stringify(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n")


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def parse_optional_bool(value: str) -> bool | None:
    normalized = value.strip().lower()
    if normalized == "":
        return None
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"false", "0", "no", "n"}:
        return False
    raise SystemExit(f"Invalid needs_additional_context value: {value!r}")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [column for column in CSV_COLUMNS if column not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"Worksheet missing required columns: {missing}")
        return [dict(row) for row in reader]


if __name__ == "__main__":
    main()
