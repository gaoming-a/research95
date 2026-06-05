from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge JSONL files, keeping the first record for each ID.")
    parser.add_argument("--input", action="append", required=True)
    parser.add_argument("--id-field", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    merged: dict[str, dict[str, Any]] = {}
    input_records = 0
    for input_path in args.input:
        for record in read_jsonl(Path(input_path)):
            input_records += 1
            record_id = str(record.get(args.id_field, ""))
            if not record_id:
                raise SystemExit(f"Missing id field {args.id_field} in {input_path}")
            merged.setdefault(record_id, record)

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output, list(merged.values()))
    print(
        json.dumps(
            {
                "inputs": len(args.input),
                "input_records": input_records,
                "output_records": len(merged),
                "duplicates_removed": input_records - len(merged),
                "out": str(output),
            },
            indent=2,
        )
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"Expected object at {path}:{line_number}")
            records.append(value)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


if __name__ == "__main__":
    main()
