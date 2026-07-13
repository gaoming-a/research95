# DSA v0.2 72-call development pilot v0.2 terminal audit

日期：2026-07-13
状态：`TERMINAL EXECUTION-CHAIN FAILURE / VALID MODEL OUTPUTS=0`

8项 Qwen canary 均在推理前返回 HTTP 400：`'max_tokens' must be Integer`。冻结 route
同时包含整数 `max_completion_tokens=1024` 与文档哨兵字符串 `max_tokens="omitted"`，
runner 未删除哨兵便序列化请求。HTTP 400 非冻结 retry 类型，因此没有 transport retry；
但 runner 未在第一条 non-retryable 400 后 hard stop，形成第二个执行链路 bug。

本轮有8个 endpoint HTTP requests、0个有效模型输出、0个科学决策、0个剩余64项请求。
这不是 prompt、证据或模型效果结果。v0.2 authorization 已从 active path 移除，ledger
和 raw errors 保留在 ignored outputs；其 hashes 由机器 terminal audit 绑定。v0.2 不得恢复、
覆盖或重跑。修复必须使用新 request domain、runner、aggregate、签核、授权和 output 路径。
