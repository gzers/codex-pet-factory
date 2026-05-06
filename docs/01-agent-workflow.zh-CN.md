# Agent 工作流

English documentation: [01-agent-workflow.md](01-agent-workflow.md)

本文面向使用 Codex Pet Factory 的开发者 agent。目标是把用户给的图片或描述稳定转换成可安装的 Codex Pet。

## 1. 收集输入

输入可以是：

- 一张原始照片。
- 一个角色或宠物描述。
- 多张风格参考图。
- 旧版 Codex Pet 或 sprite sheet。

处理原则：

- 全部放入 `assets/reference/`。
- 不直接覆盖用户原图。
- 在 `docs/00-harness.md` 或项目 README 记录来源和用途。

## 2. 创建项目

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory scaffold ./my-pet --name "宠物名" --id pet-id
```

`--name` 是 Codex UI 里显示的名字。`--id` 建议使用小写英文、数字和短横线。

## 3. 写动作设计

先改 `docs/01-action-design.md`，再生成图。动作设计至少包含：

- 每个状态的中文备注。
- 每个状态要表达的行为。
- 生产参考里给出的每个状态帧数预算。
- 是否需要道具。
- 哪些状态需要镜像派生。
- 人工验收标准。

## 4. 生成角色设定

如果用户给图片：

- 先提炼为统一角色设定图。
- 保留关键身份特征，例如脸型、耳朵、毛色、配饰。
- 简化小尺寸不可读的细节。

如果用户只给描述：

- 先生成角色设定图。
- 再由角色设定图派生动作组。

## 5. 生成动作帧

推荐输出路径：

```text
assets/generated/<state>/frames/frame-00.png
assets/generated/<state>/normalized/frame-00.png
```

要求：

- normalized 帧必须是 `192 x 208`。
- 背景透明。
- 同一动作组中角色比例稳定。
- `running-left` 从 `running-right` 镜像得到。
- 遵循生产参考里的每行帧数预算。`jumping` 是 5 帧，但 atlas 不是全局 5 帧上限。
- 每行最后一个已使用帧之后的格子必须保持透明。

## 6. 构建和校验

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory build ./my-pet
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory validate ./my-pet
```

查看：

- `build/<pet-id>/contact-sheet.png`
- `build/<pet-id>/preview.html`
- `build/<pet-id>/validate.json`
- `build/<pet-id>/qa-notes.md`
- `docs/03-interaction-checklist.zh-CN.md`

## 7. 安装

只有在自动校验、预览页面、contact sheet 和交互清单都通过后安装：

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory install ./my-pet
```

安装输出：

```text
~/.codex/pets/<pet-id>/pet.json
~/.codex/pets/<pet-id>/spritesheet.webp
```

## 8. 迭代

如果用户指出某帧问题：

- 优先回到对应动作组修复。
- 不要直接在最终 atlas 上盲修。
- 动画绘制完成，或者帧数预算有变化后，要重跑 build、validate、预览页面和 contact sheet。
- 重新生成的输出确认无误后再 install，这样 `${HOME}/.codex/pets/<pet-id>/` 里的 `pet.json` 和 `spritesheet.webp` 才会更新。
