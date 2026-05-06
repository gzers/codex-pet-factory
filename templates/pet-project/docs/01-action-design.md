# Action Design

中文文档：[01-action-design.zh-CN.md](01-action-design.zh-CN.md)

The frame budgets below follow the official production spec. Populate only the used frames in each row; any remaining cells stay transparent.

| Row | State | Used Frames | Note | Design |
| --- | --- | ---: | --- | --- |
| 0 | `idle` | 6 | Idle | TBD |
| 1 | `running-right` | 8 | Run right | TBD |
| 2 | `running-left` | 8 | Run left | Mirror from right |
| 3 | `waving` | 4 | Greeting | TBD |
| 4 | `jumping` | 5 | Jump | TBD |
| 5 | `failed` | 8 | Failure | TBD |
| 6 | `waiting` | 6 | Waiting | TBD |
| 7 | `running` | 6 | In-place loop | TBD |
| 8 | `review` | 6 | Easter egg | TBD |
