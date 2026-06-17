---
name: codex-pet-factory
description: Use when a user wants to create, customize, package, validate, or install a Codex desktop pet. Bridges official pet-generation output into this repo's local `.pets/<pet-id>/` project layout.
metadata:
  short-description: Build reusable Codex desktop pets
---

# Codex Pet Factory

中文说明：[SKILL.zh-CN.md](SKILL.zh-CN.md)

Use this skill to bridge official pet-generation output into a local Codex pet project.

## Workflow

1. Create or open the pet project at `.pets/<pet-id>/`.
2. Put source inputs in `build/input/`.
3. Write or update `docs/01-action-design.md` before generating frames.
4. Generate working frames into `build/work/`, then normalize them to transparent `192 x 208` PNGs.
5. Build and validate with `codex-pet-factory build`.
6. Inspect `build/qa/contact-sheet.png`, `build/qa/preview.html`, and `docs/03-interaction-checklist.md`.
7. Install with `codex-pet-factory install` only after QA passes.

## Commands

```bash
codex-pet-factory scaffold .pets/juice --name "果汁" --id juice
codex-pet-factory build .pets/juice
codex-pet-factory validate .pets/juice
codex-pet-factory install .pets/juice
```

If the CLI is not installed, run it from the repo:

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m builder scaffold .pets/juice --name "果汁" --id juice
```

## Production Rules

- Keep the skill thin: use it to route into the local project layout, not to restate the full production manual.
- Keep generated work under `build/input/`, `build/work/`, `build/qa/`, and `build/final/`.
- Treat `docs/01-action-design.md` as the action truth source.
- Follow the official atlas contract from the production reference: 8 x 9 grid, per-row frame budgets, and transparent unused cells.
- Use `running-right` as the authored run; derive `running-left` by mirroring.
- Keep all normalized frames `192 x 208` transparent PNG.
- Do not install if `validate.json` contains errors.
- Prefer preview page and contact sheet review before per-frame pixel surgery.
- Complete the generated interaction checklist before install.
