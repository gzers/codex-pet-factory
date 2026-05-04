# Codex Pet 制作参考

English documentation: [pet-production.md](pet-production.md)

## 输入

可以接受以下任意来源：

- 用户照片或参考图。
- 纯文字角色描述。
- 已有 sprite sheet 或旧版 Codex Pet。
- 品牌或吉祥物 brief。

必须把输入归档到 `assets/reference/`，并记录它们如何被使用。

## 默认 Atlas

| 行号 | 状态 | 帧数 | 用途 |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | 休息、啃咬、眨眼、呼吸 |
| 1 | `running-right` | 8 | 向右移动 |
| 2 | `running-left` | 8 | 镜像得到的向左移动 |
| 3 | `waving` | 4 | 打招呼或吸引注意 |
| 4 | `jumping` | 5 | 跳跃、蹦跳、翻滚或兴奋动作 |
| 5 | `failed` | 8 | 难过、哭泣、困惑或错误状态 |
| 6 | `waiting` | 6 | 等待、躺下、滚动、犯困 |
| 7 | `running` | 6 | 原地循环，例如转圈 |
| 8 | `review` | 6 | 有趣彩蛋或特殊反应 |

单元格尺寸是 `192 x 208`。网格宽度是 8 列。未使用的格子保持透明。

## 图像生成建议

使用图像生成时：

- 尽量生成动作条，而不是互不相关的孤立帧。
- 要求透明背景 sprite 帧，或使用容易移除的纯色背景。
- 在各状态中保持同一角色身份、配饰、比例和配色。
- 照片转宠物时，先做紧凑角色设定图，再从设定图派生动作。
- 避免桌面宠物尺寸下看不清的小细节。

## QA

必须检查：

- `spritesheet.webp` 存在，且是 WebP RGBA。
- `pet.json` 包含 `id`、`displayName`、`description`、`spritesheetPath`。
- 每个已使用帧都不是空图。
- 每个 normalized frame 都严格是 `192 x 208`。
- 左右奔跑的大小、节奏、基线匹配。
- Contact sheet 通过视觉验收。

常见失败：

- 奔跑帧大小漂移。
- 一两帧脸或配饰变形。
- 透明边缘有彩色 halo。
- 左右奔跑分别生成，导致不再匹配。
- 可爱特殊动作过于写实或视觉噪声太多。
