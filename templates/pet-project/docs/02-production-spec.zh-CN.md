# 制作规格

English documentation: [02-production-spec.md](02-production-spec.md)

## Atlas 约束

- 单元格：`192 x 208`
- 网格：`8 x 9`
- Atlas：`1536 x 1872`
- 格式：WebP RGBA
- Runtime manifest：`build/<pet-id>/pet.json`
- 这是一条按行计算的约束，不是全局 5 帧上限。`jumping` 使用 5 帧，其它行使用各自列出的帧数。
- 每行最后一个已使用帧之后的格子都要保持透明。

| 行号 | 状态 | 使用帧数 | 用途 |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | 待机、呼吸、眨眼、小动作 |
| 1 | `running-right` | 8 | 向右奔跑 |
| 2 | `running-left` | 8 | 向左奔跑，建议从右向镜像 |
| 3 | `waving` | 4 | 打招呼 |
| 4 | `jumping` | 5 | 跳跃、翻滚、兴奋动作 |
| 5 | `failed` | 8 | 失败、哭泣、困惑、错误反馈 |
| 6 | `waiting` | 6 | 等待、躺倒、滚动、犯困 |
| 7 | `running` | 6 | 原地循环 |
| 8 | `review` | 6 | 彩蛋或特殊反应 |
