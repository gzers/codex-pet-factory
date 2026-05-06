# Codex Pet Production Reference

中文文档：[pet-production.zh-CN.md](pet-production.zh-CN.md)

## Inputs

Accept any of these as source material:

- User photo or reference image.
- Text-only character description.
- Existing sprite sheet or older Codex Pet.
- Brand or mascot brief.

Always archive inputs in `assets/reference/` and record how they are used.

## Default Atlas

| Row | State | Used Frames | Purpose |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | Resting, chewing, blinking, breathing |
| 1 | `running-right` | 8 | Rightward locomotion |
| 2 | `running-left` | 8 | Mirrored leftward locomotion |
| 3 | `waving` | 4 | Greeting or attention action |
| 4 | `jumping` | 5 | Jump, hop, flip, or excited action |
| 5 | `failed` | 8 | Sad, crying, confused, or error state |
| 6 | `waiting` | 6 | Waiting, lying down, rolling, sleepy |
| 7 | `running` | 6 | In-place loop such as spinning |
| 8 | `review` | 6 | Fun easter egg or special reaction |

Cell size is `192 x 208`. Grid width is 8 columns. This is not a global 5-frame cap: only `jumping` uses 5 frames. Keep unused cells after each row's final used frame transparent.

## Image Generation Guidance

When using image generation:

- Generate action strips where possible, not isolated unrelated frames.
- Ask for transparent-background sprite frames or a flat chroma background that can be removed.
- Keep the same character identity, accessories, proportions, and palette across states.
- For a photo-based pet, first create a compact character sheet, then generate actions from that sheet.
- Avoid tiny details that disappear at desktop pet scale.

## QA

Required checks:

- `spritesheet.webp` exists and is WebP RGBA.
- `pet.json` has `id`, `displayName`, `description`, and `spritesheetPath`.
- Every used frame is non-empty.
- Every normalized frame is exactly `192 x 208`.
- Left and right running have matching size, rhythm, and baseline.
- Contact sheet passes visual review.

Common failures:

- Run frames drift in size.
- One or two frames have a different face or accessory.
- Transparent edges contain colored halos.
- Mirrored run is independently generated and no longer matches.
- Cute special actions become too realistic or visually noisy.
