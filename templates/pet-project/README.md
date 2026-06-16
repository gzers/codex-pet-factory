# Example Codex Pet

中文文档：[README.zh-CN.md](README.zh-CN.md)

This template becomes a pet project at `.pets/<pet-id>/`.
The Codex-recognized project skill lives in `.agents/skills/` in the repo root.

## Portal

| English | 中文 |
| --- | --- |
| [Docs](docs/README.md) | [文档](docs/README.zh-CN.md) |
| [Harness](docs/00-harness.md) | [Harness](docs/00-harness.zh-CN.md) |
| [Action Design](docs/01-action-design.md) | [动作设计](docs/01-action-design.zh-CN.md) |
| [Production Spec](docs/02-production-spec.md) | [制作规格](docs/02-production-spec.zh-CN.md) |
| [Interaction Checklist](docs/03-interaction-checklist.md) | [交互清单](docs/03-interaction-checklist.zh-CN.md) |

## Layout

- `build/input/`: source inputs.
- `build/work/`: working frames and intermediate files.
- `build/qa/`: preview, contact sheet, and validation outputs.
- `build/final/`: installed pet package.

## Commands

```bash
codex-pet-factory build .
codex-pet-factory validate .
codex-pet-factory install .
```

Review `build/qa/preview.html` and `docs/03-interaction-checklist.md` before installing.
If you change animation frames or frame counts, run `build` again before `install` so `build/final/` stays current.
