# Codex Pet Factory

Codex Pet Factory is a reusable toolkit for creating Codex desktop pets from a user image, a character description, or existing sprite assets. It turns one-off pet production into a repeatable project workflow with a scaffold, sprite atlas builder, validator, installer, and an agent-facing skill.

中文文档：[README.zh-CN.md](README.zh-CN.md)

## Documentation Portal

| English | 中文 |
| --- | --- |
| [Documentation Index](docs/README.md) | [文档传送门](docs/README.zh-CN.md) |
| [Agent Workflow](docs/01-agent-workflow.md) | [Agent 工作流](docs/01-agent-workflow.zh-CN.md) |
| [Developer Guide](docs/02-developer-guide.md) | [开发者说明](docs/02-developer-guide.zh-CN.md) |
| [Photo Example](examples/from-photo.md) | [照片示例](examples/from-photo.zh-CN.md) |
| [Skill](skills/codex-pet-factory/SKILL.md) | [Skill 中文说明](skills/codex-pet-factory/SKILL.zh-CN.md) |
| [Production Reference](skills/codex-pet-factory/references/pet-production.md) | [制作参考](skills/codex-pet-factory/references/pet-production.zh-CN.md) |

## Use Cases

- A user provides a pet, person, mascot, or object image and wants a Codex Pet.
- A user provides only a text description and wants an animated desktop pet.
- Existing sprite frames need to be packaged as `spritesheet.webp` and `pet.json`.
- A one-off pet build should become a repeatable engineering workflow.

## Project Layout

```text
codex-pet-factory/
├── src/codex_pet_factory/          # CLI source
├── skills/codex-pet-factory/       # Skill for Codex/agents
├── docs/                           # English and Chinese documentation
├── examples/                       # Example briefs and workflows
└── pyproject.toml
```

## Installation

For local development, create a virtual environment and install the package in editable mode:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests
```

## Core Commands

Run locally with `PYTHONPATH`:

```bash
PYTHONPATH=src python3 -m codex_pet_factory scaffold ./my-pet --name "Juice" --id juice
PYTHONPATH=src python3 -m codex_pet_factory build ./my-pet
PYTHONPATH=src python3 -m codex_pet_factory validate ./my-pet
PYTHONPATH=src python3 -m codex_pet_factory install ./my-pet
```

After installing the package:

```bash
codex-pet-factory scaffold ./my-pet --name "Juice" --id juice
codex-pet-factory build ./my-pet
codex-pet-factory validate ./my-pet
codex-pet-factory install ./my-pet
```

## Output Specification

- Frame: transparent PNG, `192 x 208`.
- Atlas: WebP RGBA, `1536 x 1872`.
- Grid: 8 columns x 9 rows.
- Manifest: `pet.json` with `id`, `displayName`, `description`, and `spritesheetPath`.
- Install path: `${HOME}/.codex/pets/<pet-id>/`.

## Default State Rows

| Row | State | Frames | Purpose |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | Idle breathing, blinking, tiny character actions |
| 1 | `running-right` | 8 | Rightward run |
| 2 | `running-left` | 8 | Leftward run, preferably mirrored from rightward run |
| 3 | `waving` | 4 | Greeting |
| 4 | `jumping` | 5 | Jump, flip, hop, or excited action |
| 5 | `failed` | 8 | Failure, crying, confused, or error reaction |
| 6 | `waiting` | 6 | Waiting, lying down, rolling, sleepy behavior |
| 7 | `running` | 6 | In-place loop |
| 8 | `review` | 6 | Easter egg or special reaction |

## Agent Usage

Recommended flow for developer agents:

1. Use the `$codex-pet-factory` skill.
2. Scaffold a pet project.
3. Put user images or text briefs into `assets/reference/`.
4. Write `docs/01-action-design.md`.
5. Generate `assets/generated/<state>/normalized/frame-XX.png`.
6. Run `build` and `validate`.
7. Review `contact-sheet.png`.
8. Install after user approval.
