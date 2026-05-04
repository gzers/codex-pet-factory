# Codex Pet Factory

Codex Pet Factory 是一个可复用的 Codex 桌面宠物制作工具。它可以从用户图片、角色描述或已有 sprite 素材出发，把一次性的宠物制作流程沉淀成脚手架、sprite atlas 构建器、自动校验器、安装器和给 agent 使用的 skill。

English documentation: [README.md](README.md)

## 文档传送门

| English | 中文 |
| --- | --- |
| [Documentation Index](docs/README.md) | [文档传送门](docs/README.zh-CN.md) |
| [Agent Workflow](docs/01-agent-workflow.md) | [Agent 工作流](docs/01-agent-workflow.zh-CN.md) |
| [Developer Guide](docs/02-developer-guide.md) | [开发者说明](docs/02-developer-guide.zh-CN.md) |
| [Photo Example](examples/from-photo.md) | [照片示例](examples/from-photo.zh-CN.md) |
| [Skill](skills/codex-pet-factory/SKILL.md) | [Skill 中文说明](skills/codex-pet-factory/SKILL.zh-CN.md) |
| [Production Reference](skills/codex-pet-factory/references/pet-production.md) | [制作参考](skills/codex-pet-factory/references/pet-production.zh-CN.md) |

## 适用场景

- 用户给一张宠物、人物、吉祥物或物品图片，要求做成 Codex Pet。
- 用户只给文字描述，要求生成一个有动作的桌面宠物。
- 已有 sprite 帧，需要整理成 Codex Pet 可识别的 `spritesheet.webp` 和 `pet.json`。
- 想把某次宠物制作沉淀成可重复执行的工程闭环。

## 项目结构

```text
codex-pet-factory/
├── src/codex_pet_factory/          # CLI 程序
├── skills/codex-pet-factory/       # 给 Codex/agent 使用的 skill
├── docs/                           # 中英文文档
├── examples/                       # 示例输入说明
└── pyproject.toml
```

## 安装

本地开发建议创建虚拟环境，并以 editable 模式安装：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests
```

## 核心命令

本地开发时可以直接用 `PYTHONPATH` 运行：

```bash
PYTHONPATH=src python3 -m codex_pet_factory scaffold ./my-pet --name "果汁" --id juice
PYTHONPATH=src python3 -m codex_pet_factory build ./my-pet
PYTHONPATH=src python3 -m codex_pet_factory validate ./my-pet
PYTHONPATH=src python3 -m codex_pet_factory install ./my-pet
```

安装成命令后：

```bash
codex-pet-factory scaffold ./my-pet --name "果汁" --id juice
codex-pet-factory build ./my-pet
codex-pet-factory validate ./my-pet
codex-pet-factory install ./my-pet
```

## 产物规范

- 单帧：`192 x 208` 透明 PNG。
- Atlas：`1536 x 1872` WebP RGBA。
- 网格：8 列 x 9 行。
- Manifest：`pet.json`，包含 `id`、`displayName`、`description`、`spritesheetPath`。
- 安装目录：`${HOME}/.codex/pets/<pet-id>/`。

## 标准动作行

| 行号 | 状态 | 帧数 | 用途 |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | 待机、呼吸、眨眼、小动作 |
| 1 | `running-right` | 8 | 向右奔跑 |
| 2 | `running-left` | 8 | 向左奔跑，建议从右向镜像 |
| 3 | `waving` | 4 | 打招呼 |
| 4 | `jumping` | 5 | 跳跃、翻滚、兴奋动作 |
| 5 | `failed` | 8 | 失败、哭泣、困惑 |
| 6 | `waiting` | 6 | 等待、躺倒、滚动 |
| 7 | `running` | 6 | 原地循环动作 |
| 8 | `review` | 6 | 彩蛋或特殊反应 |

## Agent 用法

给其他开发者或 agent 的推荐调用方式：

1. 使用 `$codex-pet-factory` skill。
2. 先 scaffold 项目。
3. 把用户图片或文字描述放入 `assets/reference/`。
4. 写 `docs/01-action-design.md`，明确每个状态的动作。
5. 生成 `assets/generated/<state>/normalized/frame-XX.png`。
6. 运行 build 和 validate。
7. 查看 contact sheet。
8. 用户确认后 install。
