# Codex Pet Factory Skill 中文说明

English documentation: [SKILL.md](SKILL.md)

这个 skill 用于把官方宠物生成结果桥接到本仓库的本地 `.pets/<pet-id>/` 项目结构中。

## 工作流

1. 在 `.pets/<pet-id>/` 打开或创建宠物项目。
2. 把源输入放入 `build/input/`。
3. 在生成帧之前，先写或更新 `docs/01-action-design.md`。
4. 把工作帧生成到 `build/work/`，再规范化为透明的 `192 x 208` PNG。
5. 用 `codex-pet-factory build` 构建，并用 `validate` 校验。
6. 检查 `build/qa/contact-sheet.png`、`build/qa/preview.html` 和 `docs/03-interaction-checklist.zh-CN.md`。
7. 只有 QA 通过后才执行 `codex-pet-factory install`。

## 命令

```bash
codex-pet-factory scaffold .pets/juice --name "果汁" --id juice
codex-pet-factory build .pets/juice
codex-pet-factory validate .pets/juice
codex-pet-factory install .pets/juice
```

如果 CLI 尚未安装，可以从仓库运行：

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m builder scaffold .pets/juice --name "果汁" --id juice
```

## 制作规则

- 保持 skill 很薄，只负责把官方产物接到本地项目结构里，不重复展开完整制作手册。
- 所有生成工作都放在 `build/input/`、`build/work/`、`build/qa/` 和 `build/final/`。
- 把 `docs/01-action-design.md` 当作动作设计的事实来源。
- 遵循制作参考里的官方 atlas 约束：8 x 9 网格、每行帧数预算、以及未使用格子的透明保留。
- 先制作 `running-right`，再镜像得到 `running-left`。
- 所有 normalized frames 必须是 `192 x 208` 透明 PNG。
- 如果 `validate.json` 有 errors，不要安装。
- 优先通过 preview page 和 contact sheet 审查整体动作，再做逐帧像素修复。
- 安装前完成生成的交互清单。
