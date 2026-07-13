# DSA v0.2 72-call development pilot freeze v0.2

日期：2026-07-13
状态：`NO-API FREEZE PASS / AUTHOR SIGN-OFF PENDING`

## 结论

本包机械选择旧证据中的一个 development-only pair，使用同一隔离镜像重新验证 patch
apply、syntax、visible F2P 和三个 visible P2P checks，并冻结 2 candidates × C0--C3 ×
3 routes × 3 repeats = 72 requests。前8项只是执行 canary；答案方向不得成为停止、修改
prompt 或重跑的理由。

该 pair 永久排除于确认性 cohort、效果量和 paper-facing effectiveness claim。

## 机械选择

- eligible legacy pairs：4
- selection SHA-256：`12174ce222ced4433d88512c77922c75357fa49d8cd9b5f951b8f64eed27e8e6`
- task id 只保存在私有审计记录，model-visible packets 不含 task/project/role/label。

## 冻结结果

- model-visible packets：8
- planned requests：72
- canary requests：8
- prompt SHA-256：`08a485635924a6813a2d646518c02dacf9fa108b6a5271efb88fe35d79d4809e`
- schema SHA-256：`622212864170cbe6bb0677f230b5008947b9bf1a95f665f82cded1f44b91dbf9`
- aggregate SHA-256：`2ee6c3f03e14f64723b5ddb52187c63ed83cb4f2d5bb2dfea5d16a7c2412ebc3`
- model API calls：0

## 尚未授权

作者签核前不得读取 API key、调用 endpoint、把 pilot 回复接入确认性统计、修改 prompt/schema
或启动 order63。真实执行前还必须重新核验三条 exact route；OpenRouter route 固定
`google/gemini-3.5-flash` 与 `google-ai-studio/priority`、禁用 fallback 并要求全部参数受支持。
任一路由发生 alias/fallback/provider-tag/identity mismatch 时停止该 route，不得替换模型。
