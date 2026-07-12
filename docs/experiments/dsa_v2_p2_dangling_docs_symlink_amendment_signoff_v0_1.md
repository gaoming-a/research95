# V2-P2 Dangling Documentation Symlink Amendment Sign-off

日期：2026-07-12
状态：`AUTHOR_SIGNED_IMMUTABLE / SOURCE_EXTRACTION_AUTHORIZED / NO_API`

Black_4 的两个 official archives 含相同的 dangling documentation symlinks。Windows 当前权限不能原样创建。

manifest SHA-256：`6d07262076da1d29f9fdc4edb7e837ca35d38094f8ab1a90082a2a2be2674847`；每个 archive 数量：`[13, 13]`。

提议规则：仅对严格位于 docs/、与 declared tests/project test root/package-build metadata 零交集的 dangling symbolic link，记录 path/target/kind 与 archive hashes，并只从 Windows materialized tree 省略该不可创建 link。其他 dangling link 触发 hard stop。

## Manifest

- `docs/authors.md` -> `_build/generated/authors.md`
- `docs/blackd.md` -> `_build/generated/blackd.md`
- `docs/change_log.md` -> `_build/generated/change_log.md`
- `docs/contributing_to_black.md` -> `_build/generated/contributing_to_black.md`
- `docs/editor_integration.md` -> `_build/generated/editor_integration.md`
- `docs/ignoring_unmodified_files.md` -> `_build/generated/ignoring_unmodified_files.md`
- `docs/installation_and_usage.md` -> `_build/generated/installation_and_usage.md`
- `docs/license.md` -> `_build/generated/license.md`
- `docs/pyproject_toml.md` -> `_build/generated/pyproject_toml.md`
- `docs/show_your_style.md` -> `_build/generated/show_your_style.md`
- `docs/testimonials.md` -> `_build/generated/testimonials.md`
- `docs/the_black_code_style.md` -> `_build/generated/the_black_code_style.md`
- `docs/version_control_integration.md` -> `_build/generated/version_control_integration.md`

作者高明已签核上述 manifest SHA-256，并授权该机械规则作为后续全部 V2-P2
orders 的通用 source-materialization rule。未来每个任务必须生成独立 hash manifest，
且全部 predicates 通过后才可自动省略对应 Windows 不可创建的 docs symlink；任一
predicate 不通过即 hard stop。

签核只授权恢复 Black_4 source extraction 和继续 V2-P2；不修改 environment policy、
candidate qualification、hidden oracle、prompt/schema/statistics，不进入 V2-P3，
不读取 API key，不调用模型 API。
