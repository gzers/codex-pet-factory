# Example: Build a Pet from a Photo

中文文档：[from-photo.zh-CN.md](from-photo.zh-CN.md)

User input:

> Here is a photo of my pet. Please turn it into a Codex Pet named Juice.

Agent steps:

1. `scaffold ./juice-pet --name "Juice" --id juice`
2. Save the photo in `build/input/original/`.
3. Write the action design.
4. Generate a character sheet.
5. Generate frames for all 9 states.
6. Normalize frames to `192 x 208`.
7. Run `build` and `validate`.
8. Review the contact sheet.
9. Run `install` after user approval.
