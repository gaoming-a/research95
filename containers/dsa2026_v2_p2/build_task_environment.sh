#!/bin/bash
set -u

env_name="$1"
task_root="/opt/dsa2026/task"
project="$task_root/buggy_source"
metadata="$task_root/metadata"
log_dir="$task_root/environment_build"
mkdir -p "$log_dir"

run_logged() {
    local name="$1"
    shift
    "$@" >"$log_dir/$name.log" 2>&1
    local status=$?
    printf '%s\n' "$status" >"$log_dir/$name.exit_code"
    return "$status"
}

requirements_status=0
run_logged requirements \
    conda run -n "$env_name" python -m pip install -r "$metadata/requirements.txt" \
    || requirements_status=$?

editable_status=0
run_logged editable_project \
    conda run -n "$env_name" /bin/bash -c "cd '$project' && python -m pip install -e ." \
    || editable_status=$?

pip_check_status=0
run_logged pip_check conda run -n "$env_name" python -m pip check \
    || pip_check_status=$?

conda list -n "$env_name" --explicit >"$log_dir/conda-explicit.txt"
conda run -n "$env_name" python -m pip freeze --all >"$log_dir/pip-freeze.txt"
printf '%s\n' "$env_name" >"$log_dir/environment_name.txt"
printf '%s\n' "$requirements_status" >"$log_dir/requirements_status.txt"
printf '%s\n' "$editable_status" >"$log_dir/editable_project_status.txt"
printf '%s\n' "$pip_check_status" >"$log_dir/pip_check_status.txt"
printf '%s\n' "false" >"$log_dir/official_setup_executed.txt"

if [ "$requirements_status" -ne 0 ] || [ "$editable_status" -ne 0 ] || [ "$pip_check_status" -ne 0 ]; then
    echo "V2-P2 task dependency build failed; no task-specific repair is permitted" >&2
    exit 1
fi
