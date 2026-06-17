# Codex Pet Factory

Codex Pet Factory 是桌面宠物的项目层：一个小 CLI、一个很薄的 skill，以及一个项目模板，用来把宠物工作流做成可重复、可预览、可私有保存的工程。

它不负责替代官方的宠物生成 skill。官方 skill 负责生成，这个仓库负责本地项目结构、预览、校验、打包和安装。

English documentation: [README.md](README.md)

## 保留内容

- 项目脚手架
- build / validate / install
- 预览和 QA 输出
- 位于 `.agents/skills/` 的薄 skill
- 宠物项目模板

## 目标结构

```text
codex-pet-factory/              # 当前仓库
├── src/                        # builder.py、spec.py、预览、校验、安装
├── .agents/skills/             # Codex 可识别的项目 skill 入口
├── templates/                  # 脚手架模板
├── tests/
└── README.md
```

```text
.pets/<pet-id>/                 # scaffold 出来的宠物项目
├── build/                      # 所有生成产物，整棵忽略
│   ├── input/                  # 私有参考输入
│   ├── work/                   # 中间帧和规范化帧
│   ├── qa/                     # 预览、contact sheet、校验
│   └── final/                  # spritesheet.webp、pet.json
├── pet-project.json
└── .gitignore
```

## 会提交到 git 的内容

- `src/`
- `.agents/skills/`
- `templates/`
- `tests/`
- `README.md`

## 只保留在本地的内容

- `.pets/`
- `.pets/**/build/`
- 私密参考输入
- install 输出

## 当前命令

```bash
PYTHONPATH=src python3 -m builder scaffold ./.pets/juice --name "果汁" --id juice
PYTHONPATH=src python3 -m builder build ./.pets/juice
PYTHONPATH=src python3 -m builder validate ./.pets/juice
PYTHONPATH=src python3 -m builder install ./.pets/juice
```

## 重构大纲

1. 把根 skill 收成很薄的项目桥接层。
2. 把所有宠物产物统一放进 `.pets/<pet-id>/build/`。
3. 把私密参考输入放进 `build/input/`。
4. 保留预览和 QA 作为一级产物。
5. 把 skill 直接放在 `.agents/skills/`，让 Codex 能识别。

## 说明

- 官方生成 skill 继续作为宠物艺术生成来源。
- 这个仓库负责本地项目结构和可安装产物。
