# DSA v0.2 72-call development pilot 作者签核包 v0.3

状态：`UNSIGNED / NO API`

请作者独立核验并在对话中签署以下声明。当前文件本身不构成授权。

绑定 aggregate SHA-256：

`90e1eebc6ce182ccb5a5f8cf4efef1eca14ed2d9dc68ded55adf1efec3849d38`

建议签核声明：

> 我，高明，签核 DSA v0.2 72-call development pilot v0.3 及其 aggregate SHA-256。
> 我确认该 pilot 仅含一个机械选择的旧证据 pair，永久排除于确认性 cohort、效果量和
> paper-facing effectiveness claim；72项请求、8项 canary、prompt/schema、三条 route、
> 三次 repeat、hidden separation、transport-only retry 和 no-outcome-rerun 均已冻结；第三路线
> 固定为 OpenRouter `google/gemini-3.5-flash` 经 `google-ai-studio/priority`，禁止 provider/model fallback。
> 我确认 v0.2 仅产生8个推理前 HTTP 400 和0个有效模型输出，v0.3 使用新 request domain，
> 只修复 omitted-sentinel 序列化与 non-valid immediate hard-stop，不覆盖或重跑 v0.2。
> 我授权在 exact route 重新核验和执行 runner check-only 通过后读取所需 API key 并运行
> 该72-call pilot；仅执行故障可触发预注册 transport retry，模型答案方向不得触发重跑、
> 改 prompt 或换模型。该签核不授权启动 order63、进入确认性 V2-P3/P5、公开发布或投稿。
