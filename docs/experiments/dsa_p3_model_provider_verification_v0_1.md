# DSA P3 Model and Provider Verification v0.1

Verification date: 2026-07-11
Method: public official documentation only
Credentialed/model API calls: 0

## Frozen route 1: Alibaba Cloud Model Studio

- Exact dated snapshot: `qwen3.7-plus-2026-05-26`.
- Official model table records a 1M context, 64K maximum output, hybrid thinking
  control, and structured-output support for this snapshot.
- The official structured-output guide supports JSON object mode for the
  Qwen3.7 Plus series in non-thinking mode. The Chat Completions reference
  supports `max_completion_tokens` for this series.
- Beijing pay-as-you-go list price at 0--256K input is CNY 2 per million input
  tokens and CNY 8 per million output tokens.
- Sources: [model table](https://help.aliyun.com/zh/model-studio/text-generation-model),
  [structured output](https://help.aliyun.com/en/model-studio/qwen-structured-output),
  [thinking control](https://help.aliyun.com/en/model-studio/deep-thinking), and
  [pricing](https://help.aliyun.com/zh/model-studio/model-pricing).

## Frozen route 2: DeepSeek API

- Exact official model ID: `deepseek-v4-flash`.
- Official API documentation lists the V4 Flash ID, an explicit
  `thinking.type=disabled` control, JSON output, a 1M context, and a documented
  maximum output well above the study's 1,024-token cap.
- Cache-miss list price is USD 0.14 per million input tokens and USD 0.28 per
  million output tokens.
- The former compatibility aliases are scheduled for retirement; this freeze
  does not use either alias.
- Sources: [models and pricing](https://api-docs.deepseek.com/quick_start/pricing),
  [Chat Completions reference](https://api-docs.deepseek.com/api/create-chat-completion),
  [thinking mode](https://api-docs.deepseek.com/guides/thinking_mode), and
  [change log](https://api-docs.deepseek.com/updates/).

## Frozen route 3: Google Gemini Developer API

- Exact stable model ID: `gemini-3.5-flash`.
- The official stable model page lists structured output, a 1,048,576-token
  input limit, and a 65,536-token output limit.
- Current Gemini 3 documentation exposes `minimal` as the lowest thinking level
  for this model and recommends omitting temperature/top-p/top-k controls. The
  freeze records that provider-native asymmetry instead of inventing a common
  parameter.
- Standard paid price is USD 0.75 per million input tokens and USD 4.50 per
  million output tokens, including thinking tokens.
- Sources: [model page](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash),
  [version patterns](https://ai.google.dev/gemini-api/docs/models),
  [thinking controls](https://ai.google.dev/gemini-api/docs/thinking), and
  [pricing](https://ai.google.dev/gemini-api/docs/pricing).

## Verification conclusion and residual Gate

All three routes currently have an official model ID and documented structured
output. Route selection is based on current official availability, provider
diversity, pinnability, and bounded cost, not on any legacy study outcome.

Documentation verification does not prove that local credentials have account
access, quota, or regional entitlement. P5 must perform a no-inference
credential/endpoint preflight within its own boundary. Smoke must then verify
the returned model identity. Missing access, missing identity, alias drift,
price change, or fallback stops the route and does not authorize substitution.
