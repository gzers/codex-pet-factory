# Codex Pet Factory

Codex Pet Factory is the project layer for Codex desktop pets: a small CLI, a thin agent skill, and a project template that keep pet work reproducible, previewable, and private.

It is not meant to replace the official pet-generation skill. The upstream skill can handle generation; this repo focuses on project structure, preview, validation, packaging, and install.

中文文档：[README.zh-CN.md](README.zh-CN.md)

## What stays here

- project scaffolding
- build / validate / install
- preview and QA outputs
- a thin project skill that bridges official generation output into this repo's layout, living in `.agents/skills/`
- a template for per-pet projects

## Target layout

```text
codex-pet-factory/              # this repo
├── src/                        # builder.py, spec.py, preview, validation, install
├── .agents/skills/             # Codex-recognized project skill entry
├── templates/                  # scaffold template
├── tests/
└── README.md
```

```text
.pets/<pet-id>/                 # generated pet project, created by scaffold
├── build/                      # all generated outputs, ignored by git
│   ├── input/                  # private references and working inputs
│   ├── work/                   # intermediate frames and normalized frames
│   ├── qa/                     # preview, contact sheet, validation
│   └── final/                  # spritesheet.webp, pet.json
├── pet-project.json
└── .gitignore
```

## What is committed

- `src/`
- `.agents/skills/`
- `templates/`
- `tests/`
- `README.md`

## What is local only

- `.pets/`
- `.pets/**/build/`
- private reference input
- install output

## Current commands

```bash
PYTHONPATH=src python3 -m builder scaffold ./.pets/juice --name "Juice" --id juice
PYTHONPATH=src python3 -m builder build ./.pets/juice
PYTHONPATH=src python3 -m builder validate ./.pets/juice
PYTHONPATH=src python3 -m builder install ./.pets/juice
```

## Refactor outline

1. Shrink the root skill to a thin project bridge.
2. Keep all pet output under `.pets/<pet-id>/build/`.
3. Move private references into `build/input/`.
4. Keep preview and QA as first-class outputs.
5. Keep the skill in `.agents/skills/` so Codex can discover it directly.

## Notes

- The official generation skill remains the source for pet art generation.
- This repo owns the local project structure and the installable outputs.
