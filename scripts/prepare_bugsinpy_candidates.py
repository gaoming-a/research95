from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PROJECTS = ["httpie", "tqdm", "black", "cookiecutter"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare candidate metadata from a BugsInPy archive checkout.")
    parser.add_argument("--bugsinpy-root", required=True, help="Path to the BugsInPy repository or extracted archive.")
    parser.add_argument("--out", required=True, help="Output JSONL candidate metadata path.")
    parser.add_argument("--workspace-root", default="data/real_bugs/bugsinpy_workspace")
    parser.add_argument("--projects", default=",".join(DEFAULT_PROJECTS))
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    bugsinpy_root = Path(args.bugsinpy_root)
    projects = [item.strip() for item in args.projects.split(",") if item.strip()]
    records = collect_candidates(
        bugsinpy_root=bugsinpy_root,
        projects=projects,
        workspace_root=args.workspace_root.replace("\\", "/"),
        limit=args.limit,
    )
    write_jsonl(Path(args.out), records)
    print(json.dumps({"candidates": len(records), "out": args.out}, indent=2))


def collect_candidates(
    bugsinpy_root: Path,
    projects: list[str],
    workspace_root: str,
    limit: int,
) -> list[dict[str, Any]]:
    project_root = bugsinpy_root / "projects"
    framework_bin = to_bash_path(bugsinpy_root / "framework" / "bin")
    checkout_workspace_root = to_bash_path(workspace_root)
    records: list[dict[str, Any]] = []
    for project in projects:
        bugs_dir = project_root / project / "bugs"
        if not bugs_dir.exists():
            continue
        for bug_dir in sorted((path for path in bugs_dir.iterdir() if path.is_dir()), key=numeric_name):
            info = parse_info_file(bug_dir / "bug.info")
            run_test_commands = read_command_lines(bug_dir / "run_test.sh")
            sample_root = f"{workspace_root}/{project}_{bug_dir.name}"
            records.append(
                {
                    "bug_id": f"bugsinpy_{project}_{bug_dir.name}",
                    "source": "bugsinpy",
                    "project": project,
                    "language": "python",
                    "bugsinpy_bug_id": bug_dir.name,
                    "bugsinpy_root": to_posix(bugsinpy_root),
                    "python_version": info.get("python_version"),
                    "buggy_commit_id": info.get("buggy_commit_id"),
                    "fixed_commit_id": info.get("fixed_commit_id"),
                    "test_file": info.get("test_file"),
                    "run_test_commands": run_test_commands,
                    "bug_patch": to_posix(bug_dir / "bug_patch.txt"),
                    "requirements": to_posix(bug_dir / "requirements.txt"),
                    "buggy_checkout_command": (
                        f"bash {framework_bin}/bugsinpy-checkout -p {project} -i {bug_dir.name} "
                        f"-v 0 -w {checkout_workspace_root}/{project}_{bug_dir.name}/buggy"
                    ),
                    "fixed_checkout_command": (
                        f"bash {framework_bin}/bugsinpy-checkout -p {project} -i {bug_dir.name} "
                        f"-v 1 -w {checkout_workspace_root}/{project}_{bug_dir.name}/fixed"
                    ),
                    "buggy_workdir": f"{sample_root}/buggy/{project}",
                    "fixed_workdir": f"{sample_root}/fixed/{project}",
                    "buggy_compile_command": f"bash {framework_bin}/bugsinpy-compile -w .",
                    "fixed_compile_command": f"bash {framework_bin}/bugsinpy-compile -w .",
                    "buggy_test_command": f"bash {framework_bin}/bugsinpy-test -w .",
                    "fixed_test_command": f"bash {framework_bin}/bugsinpy-test -w .",
                    "buggy_expected_exit_code": "nonzero",
                    "fixed_expected_exit_code": 0,
                    "notes": "Candidate metadata only. Run checkout and compile commands before validation.",
                }
            )
            if len(records) >= limit:
                return records
    return records


def parse_info_file(path: Path) -> dict[str, str]:
    info: dict[str, str] = {}
    if not path.exists():
        return info
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        info[key.strip()] = value.strip().strip('"')
    return info


def read_command_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def numeric_name(path: Path) -> tuple[int, str]:
    try:
        return (int(path.name), path.name)
    except ValueError:
        return (10**9, path.name)


def to_posix(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def to_bash_path(path: Path | str) -> str:
    resolved = Path(path).resolve()
    text = to_posix(resolved)
    if len(text) >= 2 and text[1] == ":":
        drive = text[0].lower()
        return f"/mnt/{drive}{text[2:]}"
    return text


if __name__ == "__main__":
    main()
