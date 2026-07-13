# DSA v0.2 72-call development pilot results v0.3

日期：2026-07-13
状态：`COMPLETE / INTEGRITY PASS / DEVELOPMENT ONLY`

## 执行完整性

- frozen requests：72；terminal records：72；valid model outputs：72；
- endpoint attempts：72；transport retries：0；HTTP 200：72；
- 三条 route 各24条，三个 repeat 各24条，8个 packets 各9条；
- ledger SHA-256：`bbafdf8ed402a1e107cddab7b9237af16ce2872eeec461543df002f069dabf5b`；全部 raw hashes、schema、identity、prompt/body hash 和 manifest binding 通过；
- raw provider payload 与 rationale 保留在 ignored `outputs/`，未进入 tracked summary。

## 描述性结果

单元格为三个 repeat 的 `accept/reject/escalate` 计数。`Delta` 是同一 development pair
内 C3 与 C0 的 accept-rate 差，不是确认性效果量。

| model | candidate role | C0 A/R/E | C1 A/R/E | C2 A/R/E | C3 A/R/E | Delta C3-C0 |
|---|---|---:|---:|---:|---:|---:|
| qwen3.7-plus-2026-05-26 | negative | 3/0/0 | 0/0/3 | 3/0/0 | 3/0/0 | +0.000 |
| qwen3.7-plus-2026-05-26 | positive | 0/3/0 | 3/0/0 | 3/0/0 | 3/0/0 | +1.000 |
| deepseek-v4-flash | negative | 3/0/0 | 3/0/0 | 3/0/0 | 3/0/0 | +0.000 |
| deepseek-v4-flash | positive | 3/0/0 | 3/0/0 | 3/0/0 | 3/0/0 | +0.000 |
| google/gemini-3.5-flash | negative | 0/3/0 | 0/1/2 | 2/0/1 | 2/1/0 | +0.667 |
| google/gemini-3.5-flash | positive | 0/1/2 | 2/0/1 | 3/0/0 | 3/0/0 | +1.000 |

- 24个 route × role × condition 单元中，19个三次重复完全一致；
- Qwen 对 negative 在 C1 转为 escalate，但 C2/C3 再次全部 accept；
- DeepSeek 对 positive 与 negative 的 C0--C3 均全部 accept；
- Gemini 对 positive 随证据增加趋向 accept，但对 negative 的 C2/C3 仍出现 accept；
- 因此 runner/prompt/schema/route 链路已被真实调用验证，但该单 pair 并未显示“更多证据
  一定减少错误接受”的稳定模式。

## 边界

这是一个机械选择旧证据 pair 的 development pilot，永久排除于确认性 cohort、
`Delta_minus`/`Delta_plus` 估计、样本量与 paper-facing effectiveness claim。结果方向没有
触发重跑、prompt/schema 修改、换模型或 route fallback。
