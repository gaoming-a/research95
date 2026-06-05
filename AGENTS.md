# AGENTS.md

## 执行闭环要求

本项目必须使用“计划-执行-审计-修订”的闭环推进，不能只按清单机械执行。

每一轮继续任务时必须遵守：

1. **Inspect**
   - 先检查当前工作区、计划文档、最近输出和审计报告。
   - 不得只凭记忆继续执行。

2. **Plan**
   - 在执行前明确本轮小目标、边界和验收条件。
   - 涉及实验、API、数据、论文结论或 Git 同步时，必须同步更新
     `docs/plans/current_plan_zh.md`。

3. **Execute**
   - 只执行本轮计划允许范围内的动作。
   - 如果本轮目标是 dry-run、check-only 或本地审计，不得顺手调用真实 API。

4. **Verify**
   - 每完成一个关键动作后立刻运行最小验证。
   - 不能等多个步骤全部完成后才统一检查。

5. **Diagnose**
   - 如果验证失败，先定位问题类型：
     - 执行链路 bug；
     - 实验设计问题；
     - 数据或证据问题；
     - 论文结论问题；
     - API、成本或凭证问题。
   - 定位前不得继续执行后续实验步骤。

6. **Repair**
   - 根据问题类型修代码、修数据、修 prompt、修计划或降级论文 claim。
   - 修复必须保持最短路径，不允许引入无关兼容层或额外方案。

7. **Sync Docs**
   - 修复后必须同步更新相关文档：
     - `docs/plans/current_plan_zh.md`：当前计划、边界、下一步；
     - `docs/experience/engineering_notes.md`：问题、原因、处理方式；
     - `docs/INDEX.md` 或 README：新增入口或文件索引。

8. **Gate**
   - 修复后必须重新运行覆盖该问题的最小验证。
   - 验证未通过时不得进入下一阶段。

9. **Commit And Sync**
   - 代码或文档更新完成后，必须只暂存本轮相关文件，检查 diff 和敏感信息，
     然后提交并同步到对应 GitHub 仓库。
   - 不得提交 `.env`、local config、raw outputs、benchmark checkout 或 artifact ZIP。

## 当前研究特定规则

- `patch_verify_evidence_first_v1` 的 full run gate 为 `stop_or_redesign`；
  不得继续按旧 prompt 扩量。
- 新的 redesign smoke 必须先修复并验证 dry-run 条件选择，再考虑真实 API。
- `tool_augmented_evidence` 是单独的 tool-augmented verifier，不得用于修补
  prompt-only evidence-first 的正向结论。
- 如果 dry-run、preflight 或 prompt-boundary 检查发现问题，必须暂停 API 调用，
  先更新计划并修复执行链路。
