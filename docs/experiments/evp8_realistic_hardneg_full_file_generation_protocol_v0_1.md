# EVP-8 Realistic Hard-Negative Full-File Generation Protocol v0.1

Date: 2026-06-30

This is a no-API protocol for a separately declared generation interface. It
does not run model APIs, read raw model outputs, store prompt text, or store
patch text.

## Motivation

The exact search/replace edit-plan interface failed before candidate
construction on `luigi_3` and `youtube-dl_7`. Continuing blind API retries
under that interface would mix source selection with generation-interface
instability.

This protocol tests a narrower full-file replacement interface for one
third-project task before any verifier API is considered.

## Interface

- prompt version: `agent_full_file_v1`
- target shape: one touched Python file
- model output schema:
  - `file_path`: relative touched file path
  - `content`: complete revised file content
  - `rationale`: short explanation
- materialization: overwrite the copied buggy file with `content`, then export
  a normal `git diff`

## Target

- task: `bugsinpy_youtube-dl_7`
- project: `youtube-dl`
- touched file: `youtube_dl/utils.py`
- buggy file size: `76925` bytes
- visible test: `test.test_utils.TestUtil.test_xpath_text`
- hidden oracle: `scripts/oracles/youtubedl_7_js_to_json.py`

## Boundary

This is a new generation-interface protocol, not a silent continuation of the
exact edit-plan supplement series. Only dry-run and prompt-boundary audit are
allowed first.

Verifier API remains blocked until generated candidates pass validation,
relabeling, visible-test execution, and the combined hard-negative gate.
