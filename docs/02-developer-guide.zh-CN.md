# 开发者说明

English documentation: [02-developer-guide.md](02-developer-guide.md)

## 设计目标

Codex Pet Factory 只负责稳定工程部分：

- 建立宠物项目结构。
- 定义 Codex Pet 默认 atlas 规格。
- 从 normalized PNG 帧打包 `spritesheet.webp`。
- 生成 `pet.json`。
- 输出 contact sheet、`preview.html`、`validate.json` 和 QA notes。
- 在 scaffold 项目中生成交互清单。
- 强制执行官方 atlas 约束：8 x 9 网格、每行帧数预算、以及未使用格子的透明保留。
- 安装到 Codex Pets 目录。

它不强制绑定某个图像生成服务。agent 可以使用任何可用的图片生成或编辑能力，只要最终落到 normalized frames。

## CLI 模块

入口：

```text
src/codex_pet_factory/cli.py
```

命令：

- `scaffold`：创建项目目录和 `pet-project.json`。
- `build`：打包 atlas、runtime manifest、contact sheet、预览页面、校验输出和 QA notes。
- `validate`：重新生成校验结果，遇到错误退出非零。
- `install`：复制到 `${HOME}/.codex/pets/<pet-id>/`。

## 项目 Manifest

`pet-project.json` 是项目级 manifest，不是 Codex Pet runtime manifest。

示例：

```json
{
  "id": "juice",
  "displayName": "果汁",
  "description": "Custom Codex Pet named 果汁.",
  "cell": [192, 208],
  "grid": [8, 9]
}
```

`build/<pet-id>/pet.json` 才是 Codex Pets 使用的 runtime manifest。

## QA 产物

每次成功 build 会在 `build/<pet-id>/` 写入：

- `spritesheet.webp`：运行时 sprite atlas。
- `pet.json`：运行时 manifest。
- `contact-sheet.png`：按行展示的静态检查图。
- `preview.html`：本地交互动画预览页，按 Codex Pet 状态播放。
- `validate.json`：机器可读的帧指标和错误列表。
- `qa-notes.md`：简短 QA 记录。

## Normalized Frames

构建器只读取：

```text
assets/generated/<state>/normalized/frame-00.png
```

如果有更复杂的抠图、缩放、镜像、修边逻辑，应放在具体宠物项目自己的脚本里。Factory 保持通用。

## 测试

使用标准库运行测试：

```bash
python3 -m unittest discover -s tests
```

如果当前环境没有 Pillow，构建测试会跳过。`--help` 和 `scaffold` 必须在没有 Pillow 时仍然可用。

## Skill

Skill 位于：

```text
skills/codex-pet-factory/
```

它用于告诉 agent 如何按 harness 工作，而不是替代 CLI。

Skill 文档：

- 英文：[SKILL.md](../skills/codex-pet-factory/SKILL.md)
- 中文：[SKILL.zh-CN.md](../skills/codex-pet-factory/SKILL.zh-CN.md)
- 制作参考英文：[pet-production.md](../skills/codex-pet-factory/references/pet-production.md)
- 制作参考中文：[pet-production.zh-CN.md](../skills/codex-pet-factory/references/pet-production.zh-CN.md)
