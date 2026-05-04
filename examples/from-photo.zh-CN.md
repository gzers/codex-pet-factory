# 示例：从照片制作宠物

English documentation: [from-photo.md](from-photo.md)

用户输入：

> 这是一张我家宠物的照片，请做成 Codex Pet，名字叫果汁。

Agent 步骤：

1. `scaffold ./juice-pet --name "果汁" --id juice`
2. 保存照片到 `assets/reference/original/`。
3. 写动作设计。
4. 生成角色设定图。
5. 生成 9 个状态的动作帧。
6. 规范化为 `192 x 208`。
7. `build` 和 `validate`。
8. 看 contact sheet。
9. 用户验收后 `install`。
