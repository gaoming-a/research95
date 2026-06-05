from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def main() -> None:
    parser = argparse.ArgumentParser(description="Split a JSONL file into deterministic shards.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--shards", type=int, required=True)
    parser.add_argument("--prefix", default="shard")
    args = parser.parse_args()

    if args.shards <= 0:
        raise SystemExit("--shards must be positive")

    records = read_jsonl(Path(args.input))
    shards: list[list[dict[str, Any]]] = [[] for _ in range(args.shards)]
    for index, record in enumerate(records):
        shards[index % args.shards].append(record)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for index, shard in enumerate(shards):
        out_path = out_dir / f"{args.prefix}_{index:02d}.jsonl"
        write_jsonl(out_path, shard)
        outputs.append({"path": str(out_path), "records": len(shard)})

    print(json.dumps({"input_records": len(records), "outputs": outputs}, indent=2))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
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
