# EVP-8 Five-Model Synthesis v0.1

- Status: `passed`
- First-batch synthesis status: `passed`
- Later-model audit status: `passed`
- API call attempted by synthesis: `false`
- Raw outputs read: `false`
- Later summaries present: `3` / `3`

## Models

- `deepseek/deepseek-v4-pro`
- `qwen/qwen3.7-max`
- `moonshotai/kimi-k2.6`
- `mistralai/devstral-2512`
- `google/gemini-2.5-flash`

## Per-Level Decision Counts

- `E0`: `{"deepseek/deepseek-v4-pro": {"escalate": 66, "reject": 32}, "google/gemini-2.5-flash": {"escalate": 98}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 98}, "qwen/qwen3.7-max": {"escalate": 75, "reject": 23}}`
- `E1`: `{"deepseek/deepseek-v4-pro": {"escalate": 58, "reject": 40}, "google/gemini-2.5-flash": {"escalate": 98}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 92, "reject": 6}, "qwen/qwen3.7-max": {"escalate": 70, "reject": 28}}`
- `E2`: `{"deepseek/deepseek-v4-pro": {"escalate": 65, "reject": 33}, "google/gemini-2.5-flash": {"escalate": 98}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 91, "reject": 7}, "qwen/qwen3.7-max": {"escalate": 71, "reject": 27}}`
- `E3`: `{"deepseek/deepseek-v4-pro": {"escalate": 81, "reject": 17}, "google/gemini-2.5-flash": {"escalate": 96, "reject": 2}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 98}, "qwen/qwen3.7-max": {"escalate": 79, "reject": 19}}`
- `E4`: `{"deepseek/deepseek-v4-pro": {"escalate": 74, "reject": 24}, "google/gemini-2.5-flash": {"escalate": 97, "reject": 1}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 97, "reject": 1}, "qwen/qwen3.7-max": {"escalate": 80, "reject": 18}}`
- `E5`: `{"deepseek/deepseek-v4-pro": {"escalate": 71, "reject": 27}, "google/gemini-2.5-flash": {"escalate": 98}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 98}, "qwen/qwen3.7-max": {"escalate": 78, "reject": 20}}`
- `E6`: `{"deepseek/deepseek-v4-pro": {"escalate": 86, "reject": 12}, "google/gemini-2.5-flash": {"escalate": 98}, "mistralai/devstral-2512": {"escalate": 98}, "moonshotai/kimi-k2.6": {"escalate": 98}, "qwen/qwen3.7-max": {"escalate": 91, "reject": 7}}`

## Checks

- first_batch_synthesis_passed: `true`
- first_batch_no_api: `true`
- first_batch_raw_outputs_not_read: `true`
- first_batch_models: `true`
- later_audit_status_supported: `true`
- later_audit_no_api: `true`
- later_audit_raw_outputs_not_read: `true`
- later_models: `true`
- passed_status_requires_all_later_models: `true`
- per_level_counts_have_expected_levels: `true`

## Claim Boundary

- Allowed: Only after status is passed, report descriptive five-model per-level decision patterns for the frozen EVP-8 v0.1 packet set.
- Forbidden: Do not report five-model journal conclusions, LLM superiority over deterministic baselines, or final evidence-level effectiveness while this scaffold is waiting or partial.
