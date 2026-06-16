# 示例宠物 Codex Pet

English documentation: [README.md](README.md)

这个模板会落到 `.pets/<pet-id>/` 作为宠物项目。
Codex 可识别的项目 skill 直接放在仓库根目录的 `.agents/skills/`。

## 传送门

| English | 中文 |
| --- | --- |
| [Docs](docs/README.md) | [文档](docs/README.zh-CN.md) |
| [Harness](docs/00-harness.md) | [Harness](docs/00-harness.zh-CN.md) |
| [Action Design](docs/01-action-design.md) | [动作设计](docs/01-action-design.zh-CN.md) |
| [Production Spec](docs/02-production-spec.md) | [制作规格](docs/02-production-spec.zh-CN.md) |
| [Interaction Checklist](docs/03-interaction-checklist.md) | [交互清单](docs/03-interaction-checklist.zh-CN.md) |

## 目录

- `build/input/`：源输入。
- `build/work/`：工作帧和中间文件。
- `build/qa/`：预览、contact sheet 和校验输出。
- `build/final/`：安装用的最终宠物包。

## 命令

```bash
codex-pet-factory build .
codex-pet-factory validate .
codex-pet-factory install .
```

安装前请检查 `build/qa/preview.html` 和 `docs/03-interaction-checklist.md`。
如果动画帧或帧数发生变化，先重新 `build` 再 `install`，这样 `build/final/` 才会保持最新。
