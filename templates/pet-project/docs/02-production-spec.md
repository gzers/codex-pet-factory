# Production Spec

中文文档：[02-production-spec.zh-CN.md](02-production-spec.zh-CN.md)

## Atlas Contract

- Cell: `192 x 208`
- Grid: `8 x 9`
- Atlas: `1536 x 1872`
- Format: WebP RGBA
- Runtime manifest: `build/<pet-id>/pet.json`
- This is a per-row contract, not a global 5-frame cap. `jumping` uses 5 frames; the other rows use their listed counts.
- Unused cells after each row's final used frame stay transparent.

| Row | State | Used Frames | Purpose |
| --- | --- | ---: | --- |
| 0 | `idle` | 6 | Idle breathing, blinking, tiny character actions |
| 1 | `running-right` | 8 | Rightward run |
| 2 | `running-left` | 8 | Leftward run, preferably mirrored from rightward run |
| 3 | `waving` | 4 | Greeting |
| 4 | `jumping` | 5 | Jump, flip, hop, or excited action |
| 5 | `failed` | 8 | Failure, crying, confused, or error reaction |
| 6 | `waiting` | 6 | Waiting, lying down, rolling, sleepy behavior |
| 7 | `running` | 6 | In-place loop |
| 8 | `review` | 6 | Easter egg or special reaction |
