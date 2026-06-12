# P2P Scope Policy

## Official Test-Root Scope Policy

Project-level P2P-broad scopes are constructed from project-level official test
roots, not from task-local test files. For many Python projects this is the main
`tests/` directory or the test roots specified by project configuration.

When full-repository discovery from the repository root repeatedly times out or
traverses non-test resources, a task may use an official test-root scope if all
of the following conditions hold:

1. The selected root is the project's main test directory or documented test
   root, not a task-local test file.
2. The full-repository discovery timeout is recorded.
3. The selected test root is recorded in the P2P manifest.
4. The retained fail-to-pass oracle tests are excluded.
5. Only tests that pass stably on both the buggy baseline and reference-fixed
   version are included.
6. The task still satisfies `p2p_broad_size >= 3`.
7. No compatibility or test-fixture shim is introduced for the task.
8. The paper reports the scope as official-test-root project-level P2P, not as
   exhaustive repository-wide regression testing.

For `bugsinpy_fastapi_1`, full-repository discovery timed out twice without
producing a manifest. The allowed official test root is `tests/`. This is not a
task-file-level P2P scope and does not relax the `p2p_broad_main` inclusion
criteria.
