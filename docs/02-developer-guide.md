# Developer Guide

中文文档：[02-developer-guide.zh-CN.md](02-developer-guide.zh-CN.md)

## Design Goal

Codex Pet Factory owns the stable engineering layer:

- Create the pet project structure.
- Define the default Codex Pet atlas specification.
- Package normalized PNG frames into `spritesheet.webp`.
- Generate `pet.json`.
- Output `contact-sheet.png`, `preview.html`, `validate.json`, and QA notes.
- Generate an interaction checklist in scaffolded projects.
- Enforce the official atlas contract: 8 x 9 grid, per-row frame budgets, and transparent unused cells.
- Install the pet into the Codex Pets directory.

It does not bind the workflow to a specific image generation provider. Agents may use any available image generation or image editing capability as long as the final output is normalized frames.

## CLI Module

Entry point:

```text
src/builder.py
```

Commands:

- `scaffold`: create the project directory and `pet-project.json`.
- `build`: package the atlas, runtime manifest, contact sheet, preview page, validation output, and QA notes.
- `validate`: rebuild validation output and exit non-zero when errors exist.
- `install`: copy outputs into `${HOME}/.codex/pets/<pet-id>/`.
  Re-running install refreshes the Codex Pets directory with the latest `pet.json` and `spritesheet.webp`.

## Project Manifest

`pet-project.json` is the project manifest. It is not the runtime Codex Pet manifest.

Example:

```json
{
  "id": "juice",
  "displayName": "Juice",
  "description": "Custom Codex Pet named Juice.",
  "cell": [192, 208],
  "grid": [8, 9]
}
```

`build/final/pet.json` is the runtime manifest used by Codex Pets.
When animation frames or per-row frame counts change, rebuild before install so the atlas preview, validation output, and runtime files stay in sync.

## QA Outputs

Each successful build writes these files to `build/`:

- `build/final/spritesheet.webp`: runtime sprite atlas.
- `build/final/pet.json`: runtime manifest.
- `build/qa/contact-sheet.png`: static row-by-row inspection sheet.
- `build/qa/preview.html`: local interactive animation preview modeled after the Codex Pet runtime states.
- `build/qa/validate.json`: machine-readable frame metrics and errors.
- `build/qa/qa-notes.md`: concise review notes.

## Normalized Frames

The builder reads only:

```text
build/work/<state>/normalized/frame-00.png
```

If a pet needs custom matting, scaling, mirroring, or pixel repair, keep that logic in the specific pet project. Factory should remain generic.

## Tests

Run tests with the standard library:

```bash
python3 -m unittest discover -s tests
```

The build test is skipped when Pillow is not available. `--help` and `scaffold` must work without Pillow.

## Skill

The Codex-recognized project skill lives at:

```text
.agents/skills/codex-pet-factory/
```

It teaches agents the harness workflow. It does not replace the CLI.

Skill documents:

- English: [SKILL.md](../.agents/skills/codex-pet-factory/SKILL.md)
- Chinese: [SKILL.zh-CN.md](../.agents/skills/codex-pet-factory/SKILL.zh-CN.md)
- Production reference: [pet-production.md](../.agents/skills/codex-pet-factory/references/pet-production.md)
- Chinese production reference: [pet-production.zh-CN.md](../.agents/skills/codex-pet-factory/references/pet-production.zh-CN.md)
