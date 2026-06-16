# Interaction Checklist

中文文档：[03-interaction-checklist.zh-CN.md](03-interaction-checklist.zh-CN.md)

Use this checklist before installing the pet. Mark items only after checking `build/qa/preview.html`, `build/qa/contact-sheet.png`, and the Codex Pet runtime when available.

## Build Outputs

- [ ] `codex-pet-factory build pets/example-pet` exits with no validation errors.
- [ ] `build/qa/preview.html` opens locally and animates every state.
- [ ] `build/qa/contact-sheet.png` shows all used frames in the correct rows.
- [ ] `build/final/pet.json` has the expected id, display name, and spritesheet path.
- [ ] Each row's used-frame count matches the production spec (`jumping` is 5 frames; the other rows use their listed counts).

## Preview Controls

- [ ] Play and pause work without jumping frames.
- [ ] Previous and next frame buttons step through the selected state correctly.
- [ ] FPS slider updates playback speed from slow to fast.
- [ ] Background toggles make transparent edges visible on checker, dark, light, and green.
- [ ] BBox and guide toggles help inspect cropping, center line, and baseline.

## Runtime Interactions

- [ ] Idle state loops calmly and reads as the character at desktop size.
- [ ] Running right moves with a stable rhythm and baseline.
- [ ] Running left matches running right as a mirrored motion.
- [ ] Waving clearly reads as an attention or greeting action.
- [ ] Jumping has a clean anticipation, lift, and landing.
- [ ] Failed state communicates failure, sadness, confusion, or error clearly.
- [ ] Waiting state feels distinct from idle and can loop for longer pauses.
- [ ] Running loop works as an in-place action without visual drift.
- [ ] Review state reads as a special reaction or easter egg.

## Visual QA

- [ ] Character identity, proportions, palette, and accessories stay consistent across states.
- [ ] No frame has colored halos, hard background remnants, or clipped body parts.
- [ ] Frame-to-frame scale changes are intentional and not distracting.
- [ ] Important facial or prop details remain legible at `192 x 208`.
- [ ] Empty cells in each row remain transparent.

## Install Gate

- [ ] User or reviewer has approved the preview page and contact sheet.
- [ ] `codex-pet-factory validate pets/example-pet` passes.
- [ ] `codex-pet-factory install pets/example-pet` is run only after the checklist above passes.
