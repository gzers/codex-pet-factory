---
name: codex-pet-factory
description: Use when a user wants to create, customize, package, validate, or install a Codex desktop pet from an image, reference photo, character description, or existing sprite assets. Provides a reusable workflow for agent-built pets, including project scaffolding, sprite-state planning, atlas build, QA, and Codex Pets installation.
metadata:
  short-description: Build reusable Codex desktop pets
---

# Codex Pet Factory

中文说明：[SKILL.zh-CN.md](SKILL.zh-CN.md)

Use this skill to create a Codex desktop pet from a user-provided image, reference photo, or text description.

## Workflow

1. Create a project with `codex-pet-factory scaffold`.
2. Put user inputs in `assets/reference/`.
3. Write or update `docs/01-action-design.md` before generating frames.
4. Generate or draw each action state as transparent PNG frames.
5. Normalize every frame to `192 x 208`.
6. Build and validate with `codex-pet-factory build`.
7. Inspect `build/<pet-id>/contact-sheet.png`, `build/<pet-id>/preview.html`, and `docs/03-interaction-checklist.md`.
8. Install with `codex-pet-factory install` only after QA passes.

## Commands

```bash
codex-pet-factory scaffold ./my-pet --name "果汁" --id juice
codex-pet-factory build ./my-pet
codex-pet-factory validate ./my-pet
codex-pet-factory install ./my-pet
```

If the CLI is not installed, run it from the repo:

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory scaffold ./my-pet --name "果汁" --id juice
```

## Production Rules

- Build the first usable screen as the pet itself: assets, atlas, manifest, and QA outputs.
- Treat `docs/01-action-design.md` as the action truth source.
- Use `running-right` as the authored run; derive `running-left` by mirroring.
- Keep all normalized frames `192 x 208` transparent PNG.
- Do not install if `validate.json` contains errors.
- Prefer preview page and contact sheet review before per-frame pixel surgery.
- Complete the generated interaction checklist before install.

## References

Read [references/pet-production.md](references/pet-production.md) when deciding state design, frame counts, QA criteria, or how to convert a user image/description into a pet project.

Chinese reference: [references/pet-production.zh-CN.md](references/pet-production.zh-CN.md).
