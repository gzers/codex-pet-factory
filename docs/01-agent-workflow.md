# Agent Workflow

中文文档：[01-agent-workflow.zh-CN.md](01-agent-workflow.zh-CN.md)

This document is for developer agents using Codex Pet Factory. The goal is to convert a user image or character description into an installable Codex Pet.

## 1. Collect Inputs

Inputs can include:

- An original photo.
- A character or pet description.
- Multiple visual references.
- An older Codex Pet or sprite sheet.

Rules:

- Put all references in `assets/reference/`.
- Do not overwrite the user's original files.
- Record source and usage in `docs/00-harness.md` or the project README.

## 2. Scaffold the Project

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory scaffold ./my-pet --name "Pet Name" --id pet-id
```

`--name` is the display name shown in Codex UI. `--id` should use lowercase letters, numbers, and hyphens.

## 3. Write the Action Design

Update `docs/01-action-design.md` before generating images. At minimum, define:

- The note for each state.
- The behavior each state should express.
- The frame budget for each state from the production reference.
- Whether props are needed.
- Which states should be mirrored.
- Manual acceptance criteria.

## 4. Create the Character Sheet

If the user provides an image:

- Extract a unified character design first.
- Preserve identity traits such as face shape, ears, colors, and accessories.
- Simplify details that will not read at desktop pet scale.

If the user provides only a description:

- Generate the character sheet first.
- Derive action states from that sheet.

## 5. Generate Action Frames

Recommended paths:

```text
assets/generated/<state>/frames/frame-00.png
assets/generated/<state>/normalized/frame-00.png
```

Requirements:

- Normalized frames must be `192 x 208`.
- Background must be transparent.
- Character proportions should stay stable inside each state.
- `running-left` should be mirrored from `running-right`.
- Follow the production reference's per-row frame budget. `jumping` is 5 frames, but the atlas is not globally capped at 5 frames.
- Keep any cells after the last used frame in a row transparent.

## 6. Build and Validate

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory build ./my-pet
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory validate ./my-pet
```

Review:

- `build/<pet-id>/contact-sheet.png`
- `build/<pet-id>/preview.html`
- `build/<pet-id>/validate.json`
- `build/<pet-id>/qa-notes.md`
- `docs/03-interaction-checklist.md`

## 7. Install

Install only after automatic validation, preview page review, contact sheet review, and interaction checklist pass:

```bash
PYTHONPATH=/path/to/codex-pet-factory/src python3 -m codex_pet_factory install ./my-pet
```

Install output:

```text
~/.codex/pets/<pet-id>/pet.json
~/.codex/pets/<pet-id>/spritesheet.webp
```

## 8. Iterate

When the user reports a frame issue:

- Prefer fixing the relevant action state.
- Do not blindly patch the final atlas.
- Re-run build, validation, preview page review, and contact sheet review after every fix.
