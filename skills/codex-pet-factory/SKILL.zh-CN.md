# Codex Pet Factory Skill 中文说明

English documentation: [SKILL.md](SKILL.md)

这个 skill 用于从用户提供的图片、参考照片或文字描述制作 Codex 桌面宠物。

## 工作流

1. 用 `codex-pet-factory scaffold` 创建宠物项目。
2. 把用户输入放入 `assets/reference/`。
3. 在生成帧之前，先写或更新 `docs/01-action-design.md`。
4. 为每个动作状态生成或绘制透明 PNG 帧。
5. 把每帧规范化为 `192 x 208`。
6. 用 `codex-pet-factory build` 构建，并用 `validate` 校验。
7. 检查 `build/<pet-id>/contact-sheet.png`、`build/<pet-id>/preview.html` 和 `docs/03-interaction-checklist.zh-CN.md`。
8. 只有 QA 通过后才执行 `codex-pet-factory install`。

## 命令

```bash
codex-pet-factory scaffold ./my-pet --name "果汁" --id juice
codex-pet-factory build ./my-pet
codex-pet-factory validate ./my-pet
codex-pet-factory install ./my-pet
```

如果 CLI 尚未安装，可以从仓库运行：

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory scaffold ./my-pet --name "果汁" --id juice
```

## 制作规则

- 第一优先产出可用宠物：素材、atlas、manifest 和 QA 输出。
- 把 `docs/01-action-design.md` 当作动作设计的事实来源。
- 先制作 `running-right`，再镜像得到 `running-left`。
- 所有 normalized frames 必须是 `192 x 208` 透明 PNG。
- 如果 `validate.json` 有 errors，不要安装。
- 优先通过 preview page 和 contact sheet 审查整体动作，再做逐帧像素修复。
- 安装前完成生成的交互清单。

## 参考

制作状态、帧数、QA 标准，或把用户图片/描述转换成宠物项目时，阅读 [references/pet-production.md](references/pet-production.md)。

中文制作参考：[references/pet-production.zh-CN.md](references/pet-production.zh-CN.md)。
