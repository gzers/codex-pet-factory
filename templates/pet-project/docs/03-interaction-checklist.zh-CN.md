# 交互清单

English documentation: [03-interaction-checklist.md](03-interaction-checklist.md)

安装宠物前使用这份清单。请结合 `build/<pet-id>/preview.html`、`contact-sheet.png`，以及可用时的 Codex Pet 运行时一起检查。

## 构建产物

- [ ] `codex-pet-factory build .` 无 validation errors。
- [ ] `build/<pet-id>/preview.html` 可以本地打开，并能播放每个状态。
- [ ] `build/<pet-id>/contact-sheet.png` 中所有有效帧都在正确行。
- [ ] `build/<pet-id>/pet.json` 的 id、显示名和 spritesheet 路径正确。

## 预览控件

- [ ] 播放/暂停不会跳帧或卡住。
- [ ] 上一帧/下一帧能正确步进当前状态。
- [ ] FPS 滑杆能从慢速到快速调整播放速度。
- [ ] 棋盘、深色、浅色、绿底背景能暴露透明边缘问题。
- [ ] BBox 和中心线开关能辅助检查裁切、中心线和基线。

## 运行时交互

- [ ] idle 待机循环稳定，并且桌面尺寸下仍能读出角色。
- [ ] running-right 向右奔跑节奏和基线稳定。
- [ ] running-left 与向右奔跑匹配，像镜像派生动作。
- [ ] waving 能清楚读作招呼或吸引注意。
- [ ] jumping 有清楚的蓄力、起跳和落地。
- [ ] failed 能表达失败、难过、困惑或错误反馈。
- [ ] waiting 与 idle 有明显区别，适合长时间等待循环。
- [ ] running 原地循环无明显视觉漂移。
- [ ] review 能读作特殊反应或彩蛋。

## 视觉 QA

- [ ] 所有状态中的角色身份、比例、色板和配饰保持一致。
- [ ] 没有彩色毛边、背景残留或身体部位被裁掉。
- [ ] 帧间缩放变化是有意设计，而不是抖动。
- [ ] 关键表情或道具细节在 `192 x 208` 下仍然清楚。
- [ ] 每行动作未使用的格子保持透明。

## 安装门槛

- [ ] 用户或审核者已经确认 preview page 和 contact sheet。
- [ ] `codex-pet-factory validate .` 通过。
- [ ] 只有上方清单通过后，才运行 `codex-pet-factory install .`。
