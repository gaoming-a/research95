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
run_logged requirements_before \
    conda run -n "$env_name" python -m pip install -r "$metadata/requirements.txt" \
    || requirements_status=$?

setup_status=0
if [ -s "$metadata/setup.sh" ]; then
    index=0
    while IFS= read -r command || [ -n "$command" ]; do
        command="${command//$'\r'/}"
        [ -z "$command" ] && continue
        index=$((index + 1))
        run_logged "setup_${index}" \
            conda run -n "$env_name" /bin/bash -c "cd '$project' && $command" \
            || setup_status=$?
    done <"$metadata/setup.sh"
fi

requirements_after_status=0
run_logged requirements_after \
    conda run -n "$env_name" python -m pip install -r "$metadata/requirements.txt" \
    || requirements_after_status=$?

run_logged pip_check conda run -n "$env_name" python -m pip check || true
conda list -n "$env_name" --explicit >"$log_dir/conda-explicit.txt"
conda run -n "$env_name" python -m pip freeze --all >"$log_dir/pip-freeze.txt"

printf '%s\n' "$env_name" >"$log_dir/environment_name.txt"
printf '%s\n' "$requirements_status" >"$log_dir/requirements_before_status.txt"
printf '%s\n' "$setup_status" >"$log_dir/setup_status.txt"
printf '%s\n' "$requirements_after_status" >"$log_dir/requirements_after_status.txt"

if [ "$requirements_status" -ne 0 ] || [ "$setup_status" -ne 0 ] || [ "$requirements_after_status" -ne 0 ]; then
    echo "task dependency build failed; inspect $log_dir" >&2
    exit 1
fi
