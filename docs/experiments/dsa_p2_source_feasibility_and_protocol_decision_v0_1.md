# DSA 2026 P2 Source Feasibility and Protocol Decision v0.1

日期：2026-07-11

## 结论

P2 Gate：`PASSED`。稿型冻结为 `Regular`；Short 保留为预先模拟记录，但不再是结果不好时的 fallback。

## Source feasibility

- 开发排除：59 tasks；整项目排除：8 projects。
- 改进环境中 buggy=fail/fixed=pass 的新 source：304 tasks / 9 projects。
- Regular：30 primary + 10 reserve，9 projects，每项目 primary 不超过 4，且每个 primary project 至少有 1 个 reserve。
- primary project counts：`{'ansible': 3, 'black': 3, 'fastapi': 4, 'keras': 3, 'matplotlib': 4, 'pandas': 4, 'sanic': 2, 'spacy': 3, 'tornado': 4}`。
- source 排序由冻结 hash seed 决定；P2 未应用 transform、未查看 candidate hidden result。
- SCAM 2023 改进环境结果只证明 P2 source-level feasibility；P4 仍须两次全新 clean-environment 复跑。

## Transform、precision 与文献

- 四类 transform 已在排除开发任务上做结构适用性验证并冻结优先级；P3 作者签核前不得用于 source。
- Regular worst rate width=0.1185 <= 0.35；worst paired-effect width=0.1704 <= 0.30。
- Short worst paired-effect width=0.2500 <= 0.40，但因 Regular 已通过而 inactive。
- 最近邻共 12 篇；未发现 exact design match。允许定位：A controlled finite-cohort study of how cumulative real executable evidence changes fixed-LLM patch-gating policy; not a first/unique/SOTA claim and not APCA correctness proof.

## 边界与下一步

- 未调用模型 API、未创建 prompt、未读取旧论文指标或旧 raw output。
- 本轮不进入 P3。下一阶段必须由作者签核 RQ、estimands、C0--C3、transform、模型、统计、exclusion、prompt/schema 后才能继续。
- V0 外部投稿许可仍并行 pending；它不否定 P2 科学 Gate，但未通过时不得提交 DSA。

## Gate checks

- `p1_quarantine_passed`: PASS
- `development_source_task_overlap_zero`: PASS
- `base_excluded_project_overlap_zero`: PASS
- `official_source_frame_has_at_least_30_primary_and_10_reserve`: PASS
- `regular_has_at_least_eight_projects`: PASS
- `regular_primary_project_cap_at_most_four`: PASS
- `reserve_covers_every_primary_project`: PASS
- `all_regular_tasks_are_new_project_tasks`: PASS
- `new_project_requirement_at_least_15_tasks_and_4_projects`: PASS
- `all_selected_sources_have_improved_environment_reproduction`: PASS
- `all_selected_sources_have_visible_and_hidden_oracle_source_plan`: PASS
- `no_source_transform_applied_in_p2`: PASS
- `no_candidate_hidden_result_observed_in_p2`: PASS
- `transform_registry_frozen_for_author_review`: PASS
- `transform_validation_passed`: PASS
- `regular_precision_passed`: PASS
- `nearest_neighbor_positioning_passed`: PASS
- `nearest_neighbor_exact_design_match_absent`: PASS
- `no_api_prompt_or_old_result_use`: PASS
