from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

from .spec import CELL_HEIGHT, CELL_WIDTH, COLUMNS, DEFAULT_STATES, pet_id_from_name


ROOT = Path(__file__).resolve().parents[2]


def require_pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ModuleNotFoundError as error:
        raise SystemExit(
            "Pillow is required for build/validate/install. Install it with `python3 -m pip install Pillow` "
            "or run with the bundled Codex Python runtime."
        ) from error
    return Image, ImageDraw, ImageFont


def load_font(size: int):
    _image, _image_draw, image_font = require_pillow()
    for path in (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        try:
            return image_font.truetype(path, size)
        except Exception:
            continue
    return image_font.load_default()


def alpha_bbox(image) -> tuple[int, int, int, int] | None:
    return image.getchannel("A").getbbox()


def ensure_empty_cell(atlas, row: int, column: int) -> bool:
    x = column * CELL_WIDTH
    y = row * CELL_HEIGHT
    cell = atlas.crop((x, y, x + CELL_WIDTH, y + CELL_HEIGHT))
    return alpha_bbox(cell) is None


def load_manifest(project: Path) -> dict[str, object]:
    path = project / "pet-project.json"
    if not path.exists():
        raise SystemExit(f"Missing project manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_root(project: Path) -> Path:
    return project / "build"


def input_root(project: Path) -> Path:
    return build_root(project) / "input"


def work_root(project: Path) -> Path:
    return build_root(project) / "work"


def qa_root(project: Path) -> Path:
    return build_root(project) / "qa"


def final_root(project: Path) -> Path:
    return build_root(project) / "final"


def normalized_state_root(project: Path, state: str) -> Path:
    return work_root(project) / state / "normalized"


def legacy_state_root(project: Path, state: str) -> Path:
    return project / "assets" / "generated" / state / "normalized"


def state_source(project: Path, state: str) -> Path:
    for candidate in (normalized_state_root(project, state), legacy_state_root(project, state)):
        if candidate.exists():
            return candidate
    return normalized_state_root(project, state)


def ensure_build_layout(project: Path) -> None:
    (input_root(project) / "original").mkdir(parents=True, exist_ok=True)
    (input_root(project) / "visual").mkdir(parents=True, exist_ok=True)
    for spec in DEFAULT_STATES:
        (work_root(project) / spec.state / "frames").mkdir(parents=True, exist_ok=True)
        (work_root(project) / spec.state / "normalized").mkdir(parents=True, exist_ok=True)
    qa_root(project).mkdir(parents=True, exist_ok=True)
    final_root(project).mkdir(parents=True, exist_ok=True)


def build_atlas(project: Path) -> dict[str, object]:
    image, _image_draw, _image_font = require_pillow()
    manifest = load_manifest(project)
    pet_id = str(manifest["id"])
    ensure_build_layout(project)
    rows = len(DEFAULT_STATES)
    atlas = image.new("RGBA", (CELL_WIDTH * COLUMNS, CELL_HEIGHT * rows), (0, 0, 0, 0))
    validation: dict[str, object] = {
        "id": pet_id,
        "displayName": manifest["displayName"],
        "atlas_size": list(atlas.size),
        "cell": [CELL_WIDTH, CELL_HEIGHT],
        "grid": [COLUMNS, rows],
        "states": [],
        "errors": [],
    }

    for spec in DEFAULT_STATES:
        record = {
            "row": spec.row,
            "state": spec.state,
            "note": spec.note,
            "frames": spec.frames,
            "source": str(state_source(project, spec.state)),
            "frame_metrics": [],
        }
        for index in range(spec.frames):
            path = state_source(project, spec.state) / f"frame-{index:02d}.png"
            if not path.exists():
                validation["errors"].append(f"Missing frame: {path}")
                continue
            frame = image.open(path).convert("RGBA")
            if frame.size != (CELL_WIDTH, CELL_HEIGHT):
                validation["errors"].append(f"Bad frame size: {path} -> {frame.size}")
                continue
            bbox = alpha_bbox(frame)
            if bbox is None:
                validation["errors"].append(f"Empty frame: {path}")
                continue
            x = index * CELL_WIDTH
            y = spec.row * CELL_HEIGHT
            atlas.alpha_composite(frame, (x, y))
            record["frame_metrics"].append(
                {
                    "frame": index,
                    "bbox": list(bbox),
                    "size": [bbox[2] - bbox[0], bbox[3] - bbox[1]],
                    "baseline": bbox[3],
                }
            )
        for index in range(spec.frames, COLUMNS):
            if not ensure_empty_cell(atlas, spec.row, index):
                validation["errors"].append(f"Unused cell is not transparent: {spec.state} column {index}")
        validation["states"].append(record)

    atlas.save(final_root(project) / "spritesheet.webp", "WEBP", lossless=True, quality=100, method=6)
    (qa_root(project) / "validate.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_pet_json(final_root(project), manifest)
    write_contact_sheet(qa_root(project), final_root(project), validation)
    write_qa_notes(qa_root(project), validation)
    write_preview_html(qa_root(project), manifest, validation)
    return validation


def write_pet_json(out_dir: Path, manifest: dict[str, object]) -> None:
    pet_json = {
        "id": manifest["id"],
        "displayName": manifest["displayName"],
        "description": manifest.get("description", ""),
        "spritesheetPath": "spritesheet.webp",
    }
    (out_dir / "pet.json").write_text(json.dumps(pet_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_contact_sheet(out_dir: Path, final_dir: Path, validation: dict[str, object]) -> None:
    image, image_draw, _image_font = require_pillow()
    label_width = 180
    footer_height = 34
    rows = len(DEFAULT_STATES)
    sheet = image.new(
        "RGBA",
        (label_width + CELL_WIDTH * COLUMNS, CELL_HEIGHT * rows + footer_height),
        (31, 36, 44, 255),
    )
    draw = image_draw.Draw(sheet)
    font = load_font(12)
    atlas = image.open(final_dir / "spritesheet.webp").convert("RGBA")

    for spec in DEFAULT_STATES:
        y = spec.row * CELL_HEIGHT
        draw.text((10, y + 12), f"{spec.row} {spec.state}\n{spec.note}", fill=(255, 255, 255, 255), font=font)
        for column in range(COLUMNS):
            x = label_width + column * CELL_WIDTH
            draw.rectangle((x, y, x + CELL_WIDTH, y + CELL_HEIGHT), outline=(78, 86, 96, 255), width=1)
            frame = atlas.crop((column * CELL_WIDTH, y, (column + 1) * CELL_WIDTH, y + CELL_HEIGHT))
            sheet.alpha_composite(frame, (x, y))
            draw.text((x + 6, y + CELL_HEIGHT - 20), str(column), fill=(220, 225, 230, 255), font=font)

    status = "PASS" if not validation["errors"] else "FAIL"
    draw.text((10, CELL_HEIGHT * rows + 10), f"QA: {status}", fill=(255, 255, 255, 255), font=font)
    sheet.convert("RGB").save(out_dir / "contact-sheet.png")


def write_qa_notes(out_dir: Path, validation: dict[str, object]) -> None:
    status = "自动校验通过。" if not validation["errors"] else "自动校验未通过，详见 `validate.json`。"
    text = "\n".join(
        [
            f"# QA Notes: {validation['displayName']}",
            "",
            "## Status",
            "",
            status,
            "",
            "## Outputs",
            "",
            "- `final/spritesheet.webp`",
            "- `final/pet.json`",
            "- `qa/contact-sheet.png`",
            "- `qa/preview.html`",
            "- `qa/validate.json`",
        ]
    )
    (out_dir / "qa-notes.md").write_text(text + "\n", encoding="utf-8")


def script_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def write_preview_html(out_dir: Path, manifest: dict[str, object], validation: dict[str, object]) -> None:
    states = []
    for state in validation["states"]:
        states.append(
            {
                "row": state["row"],
                "state": state["state"],
                "note": state["note"],
                "frames": state["frames"],
                "frame_metrics": state["frame_metrics"],
            }
        )
    payload = {
        "pet": {
            "id": manifest["id"],
            "displayName": manifest["displayName"],
            "description": manifest.get("description", ""),
        },
        "cell": validation["cell"],
        "grid": validation["grid"],
        "atlas_size": validation["atlas_size"],
        "states": states,
        "errors": validation["errors"],
        "spritesheetPath": "../final/spritesheet.webp",
    }
    title = html.escape(f"{manifest['displayName']} Sprite Preview", quote=True)
    text = (
        PREVIEW_HTML.replace("__PREVIEW_TITLE__", title)
        .replace("__PREVIEW_DATA__", script_json(payload))
        .replace("__SPRITESHEET_PATH__", "../final/spritesheet.webp")
    )
    (out_dir / "preview.html").write_text(text + "\n", encoding="utf-8")


PREVIEW_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>__PREVIEW_TITLE__</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #171b21;
      --panel: #20262e;
      --panel-2: #262d36;
      --line: #3b4652;
      --text: #edf3f8;
      --muted: #9eabb8;
      --accent: #6cc7ff;
      --accent-2: #ff7aa8;
      --good: #83d986;
      --warn: #ffd166;
      --cell-w: 192px;
      --cell-h: 208px;
      --atlas-w: 1536px;
      --atlas-h: 1872px;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    button,
    input {
      font: inherit;
    }

    button {
      min-height: 34px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: var(--panel-2);
      color: var(--text);
      padding: 0 12px;
      cursor: pointer;
    }

    button:hover,
    button[aria-pressed="true"] {
      border-color: var(--accent);
      color: #fff;
    }

    button.primary {
      background: #215978;
      border-color: #2d7aa5;
    }

    input[type="range"] {
      accent-color: var(--accent);
    }

    .app {
      display: grid;
      grid-template-columns: 272px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      border-right: 1px solid var(--line);
      background: #151a20;
      padding: 18px 14px;
      overflow: auto;
    }

    .brand {
      margin: 0 0 4px;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 0;
    }

    .description {
      margin: 0 0 16px;
      color: var(--muted);
      font-size: 12px;
    }

    .state-list {
      display: grid;
      gap: 6px;
    }

    .state-button {
      display: grid;
      grid-template-columns: 24px minmax(0, 1fr) auto;
      align-items: center;
      gap: 8px;
      width: 100%;
      padding: 9px 10px;
      text-align: left;
    }

    .state-button .index,
    .state-button .frames,
    .thumb-label,
    .metric,
    .footer {
      color: var(--muted);
      font-variant-numeric: tabular-nums;
    }

    .state-button .name {
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .state-button small {
      color: var(--muted);
      font-size: 11px;
    }

    .main {
      display: grid;
      grid-template-rows: auto minmax(420px, 1fr) auto;
      min-width: 0;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      padding: 12px 16px;
    }

    .tool-group {
      display: flex;
      gap: 6px;
      align-items: center;
      min-height: 36px;
      padding-right: 10px;
      border-right: 1px solid var(--line);
    }

    .tool-group:last-child {
      border-right: 0;
    }

    .range-label,
    .metric,
    .strip-title {
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    .metric strong,
    .range-label strong {
      color: var(--text);
      font-weight: 650;
    }

    .stage-wrap {
      min-width: 0;
      overflow: auto;
      padding: 24px;
    }

    .stage {
      display: grid;
      grid-template-columns: minmax(280px, 430px) minmax(340px, 1fr);
      gap: 22px;
      align-items: start;
      min-width: 760px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }

    .player-panel,
    .strip-panel,
    .metrics-panel,
    .errors-panel {
      padding: 14px;
    }

    .preview-box {
      position: relative;
      width: min(100%, 370px);
      aspect-ratio: 192 / 208;
      margin: 4px auto 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background-color: #20252c;
      background-image:
        linear-gradient(45deg, rgba(255,255,255,.07) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(255,255,255,.07) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(255,255,255,.07) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(255,255,255,.07) 75%);
      background-size: 26px 26px;
      background-position: 0 0, 0 13px, 13px -13px, -13px 0;
    }

    .preview-box.light {
      background: #f4f6f8;
    }

    .preview-box.green {
      background: #00c853;
    }

    .preview-box.dark {
      background: #101318;
    }

    .sprite-frame,
    .overlay-cell,
    .overlay-bbox,
    .overlay-center,
    .overlay-baseline {
      position: absolute;
      pointer-events: none;
      transform-origin: top left;
    }

    .sprite-frame {
      left: 50%;
      top: 50%;
      width: var(--cell-w);
      height: var(--cell-h);
      transform-origin: center;
      background-image: url("__SPRITESHEET_PATH__");
      background-repeat: no-repeat;
      background-size: var(--atlas-w) var(--atlas-h);
    }

    .overlay-cell {
      border: 1px solid rgba(255,255,255,.32);
    }

    .overlay-bbox {
      border: 1px solid var(--accent-2);
      box-shadow: 0 0 0 1px rgba(255,122,168,.18);
    }

    .overlay-center {
      width: 1px;
      background: rgba(108,199,255,.55);
    }

    .overlay-baseline {
      height: 1px;
      background: rgba(131,217,134,.65);
    }

    .now-title {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin: 14px 0 4px;
    }

    .now-title h1 {
      margin: 0;
      font-size: 20px;
      letter-spacing: 0;
    }

    .note {
      margin: 0;
      color: var(--muted);
    }

    .strip-title {
      display: flex;
      justify-content: space-between;
      margin-bottom: 10px;
    }

    .frame-strip {
      display: grid;
      grid-template-columns: repeat(8, minmax(84px, 1fr));
      gap: 8px;
    }

    .thumb {
      min-width: 0;
      border: 1px solid var(--line);
      border-radius: 7px;
      overflow: hidden;
      background: #1b2027;
      padding: 0;
      cursor: pointer;
    }

    .thumb.active {
      border-color: var(--accent);
      box-shadow: 0 0 0 1px rgba(108,199,255,.45);
    }

    .thumb.empty {
      opacity: .35;
      cursor: default;
    }

    .thumb-frame {
      width: 100%;
      aspect-ratio: 192 / 208;
      background-image: url("__SPRITESHEET_PATH__");
      background-repeat: no-repeat;
      background-size: var(--thumb-bg-size);
    }

    .thumb-label {
      display: flex;
      justify-content: space-between;
      gap: 6px;
      padding: 5px 7px;
      font-size: 12px;
    }

    .metrics-panel,
    .errors-panel {
      grid-column: 1 / -1;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(120px, 1fr));
      gap: 10px;
    }

    .metric-card {
      background: var(--panel-2);
      border: 1px solid var(--line);
      border-radius: 7px;
      padding: 10px;
    }

    .metric-card .label {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }

    .metric-card .value {
      font-size: 18px;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }

    .errors-panel {
      border-color: #6a4d20;
      background: #251e15;
    }

    .errors-panel h2 {
      margin: 0 0 8px;
      font-size: 14px;
    }

    .errors-panel ul {
      margin: 0;
      padding-left: 18px;
      color: #ffd166;
      max-height: 160px;
      overflow: auto;
    }

    .footer {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      border-top: 1px solid var(--line);
      background: #151a20;
      padding: 10px 16px;
      font-size: 12px;
    }

    @media (max-width: 920px) {
      .app {
        grid-template-columns: 1fr;
      }

      .sidebar {
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }

      .state-list {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .stage {
        grid-template-columns: 1fr;
        min-width: 0;
      }

      .frame-strip {
        grid-template-columns: repeat(4, minmax(76px, 1fr));
      }

      .metrics-grid {
        grid-template-columns: repeat(2, minmax(120px, 1fr));
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <h2 class="brand" id="petName"></h2>
      <p class="description" id="petDescription"></p>
      <div class="state-list" id="stateList"></div>
    </aside>

    <main class="main">
      <div class="toolbar">
        <div class="tool-group">
          <button id="playPause" class="primary" type="button">暂停</button>
          <button id="prevFrame" type="button">上一帧</button>
          <button id="nextFrame" type="button">下一帧</button>
        </div>
        <div class="tool-group">
          <span class="range-label">FPS <strong id="fpsValue">8</strong></span>
          <input id="fps" type="range" min="1" max="18" step="1" value="8">
        </div>
        <div class="tool-group">
          <button id="bgChecker" type="button" aria-pressed="true">棋盘</button>
          <button id="bgDark" type="button" aria-pressed="false">深色</button>
          <button id="bgLight" type="button" aria-pressed="false">浅色</button>
          <button id="bgGreen" type="button" aria-pressed="false">绿底</button>
        </div>
        <div class="tool-group">
          <button id="toggleBbox" type="button" aria-pressed="true">BBox</button>
          <button id="toggleGuide" type="button" aria-pressed="true">中心线</button>
        </div>
        <div class="metric">当前：<strong id="currentReadout">-</strong></div>
      </div>

      <div class="stage-wrap">
        <section class="stage">
          <div class="panel player-panel">
            <div id="previewBox" class="preview-box">
              <div id="spriteFrame" class="sprite-frame"></div>
              <div id="cellOverlay" class="overlay-cell"></div>
              <div id="bboxOverlay" class="overlay-bbox"></div>
              <div id="centerOverlay" class="overlay-center"></div>
              <div id="baselineOverlay" class="overlay-baseline"></div>
            </div>
            <div class="now-title">
              <h1 id="stateTitle">-</h1>
              <span id="frameTitle">Frame 0</span>
            </div>
            <p class="note" id="stateNote"></p>
          </div>

          <div class="panel strip-panel">
            <div class="strip-title">
              <span>整行动作</span>
              <span>点击缩略图锁定单帧</span>
            </div>
            <div class="frame-strip" id="frameStrip"></div>
          </div>

          <div class="panel metrics-panel">
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="label">BBox 宽度</div>
                <div class="value" id="metricWidth">-</div>
              </div>
              <div class="metric-card">
                <div class="label">BBox 高度</div>
                <div class="value" id="metricHeight">-</div>
              </div>
              <div class="metric-card">
                <div class="label">底部基线</div>
                <div class="value" id="metricBaseline">-</div>
              </div>
              <div class="metric-card">
                <div class="label">行内宽度范围</div>
                <div class="value" id="metricRange">-</div>
              </div>
            </div>
          </div>

          <div class="panel errors-panel" id="errorsPanel" hidden>
            <h2>Validation Errors</h2>
            <ul id="errorsList"></ul>
          </div>
        </section>
      </div>

    <footer class="footer">
      <span>资源：final/spritesheet.webp / qa/validate.json / qa/contact-sheet.png</span>
      <span id="gridReadout"></span>
    </footer>
    </main>
  </div>

  <script>
    const data = __PREVIEW_DATA__;
    const states = data.states;
    const [cellWidth, cellHeight] = data.cell;
    const [columns, rows] = data.grid;
    const [atlasWidth, atlasHeight] = data.atlas_size;
    const spritesheetPath = data.spritesheetPath;

    document.documentElement.style.setProperty("--cell-w", `${cellWidth}px`);
    document.documentElement.style.setProperty("--cell-h", `${cellHeight}px`);
    document.documentElement.style.setProperty("--atlas-w", `${atlasWidth}px`);
    document.documentElement.style.setProperty("--atlas-h", `${atlasHeight}px`);
    document.documentElement.style.setProperty("--thumb-bg-size", `${columns * 100}% ${rows * 100}%`);

    let selectedState = states[0];
    let frame = 0;
    let fps = 8;
    let playing = true;
    let lastTick = 0;
    let showBbox = true;
    let showGuide = true;

    const stateList = document.getElementById("stateList");
    const frameStrip = document.getElementById("frameStrip");
    const spriteFrame = document.getElementById("spriteFrame");
    const previewBox = document.getElementById("previewBox");
    const bboxOverlay = document.getElementById("bboxOverlay");
    const centerOverlay = document.getElementById("centerOverlay");
    const baselineOverlay = document.getElementById("baselineOverlay");
    const cellOverlay = document.getElementById("cellOverlay");
    const playPause = document.getElementById("playPause");
    const currentReadout = document.getElementById("currentReadout");
    const stateTitle = document.getElementById("stateTitle");
    const stateNote = document.getElementById("stateNote");
    const frameTitle = document.getElementById("frameTitle");

    spriteFrame.style.backgroundImage = `url(${spritesheetPath})`;
    for (const thumbFrame of document.querySelectorAll(".thumb-frame")) {
      thumbFrame.style.backgroundImage = `url(${spritesheetPath})`;
    }

    document.getElementById("petName").textContent = data.pet.displayName;
    document.getElementById("petDescription").textContent = data.pet.description || data.pet.id;
    document.getElementById("gridReadout").textContent = `单元格 ${cellWidth} x ${cellHeight}，网格 ${columns} x ${rows}`;

    function getFrameMetric(state, index) {
      return state.frame_metrics.find((item) => item.frame === index) || null;
    }

    function renderStates() {
      stateList.innerHTML = "";
      states.forEach((state) => {
        const button = document.createElement("button");
        button.className = "state-button";
        button.type = "button";
        button.setAttribute("aria-pressed", state === selectedState ? "true" : "false");
        button.innerHTML = `<span class="index">${state.row}</span><span class="name">${state.state}<br><small>${state.note}</small></span><span class="frames">${state.frames}f</span>`;
        button.addEventListener("click", () => {
          selectedState = state;
          frame = 0;
          playing = true;
          renderAll();
        });
        stateList.append(button);
      });
    }

    function spritePosition(column, row) {
      return `-${column * cellWidth}px -${row * cellHeight}px`;
    }

    function thumbPosition(column, row) {
      const x = columns <= 1 ? 0 : (column / (columns - 1)) * 100;
      const y = rows <= 1 ? 0 : (row / (rows - 1)) * 100;
      return `${x}% ${y}%`;
    }

    function renderStrip() {
      frameStrip.innerHTML = "";
      for (let index = 0; index < columns; index += 1) {
        const thumb = document.createElement("button");
        thumb.type = "button";
        thumb.className = `thumb${index === frame ? " active" : ""}${index >= selectedState.frames ? " empty" : ""}`;
        thumb.disabled = index >= selectedState.frames;
        const metric = getFrameMetric(selectedState, index);
        const size = metric ? `${metric.size[0]}x${metric.size[1]}` : "-";
        thumb.innerHTML = `<div class="thumb-frame"></div><div class="thumb-label"><span>${index}</span><span>${size}</span></div>`;
        thumb.querySelector(".thumb-frame").style.backgroundPosition = thumbPosition(index, selectedState.row);
        thumb.addEventListener("click", () => {
          frame = index;
          playing = false;
          renderAll();
        });
        frameStrip.append(thumb);
      }
    }

    function previewScale() {
      return Math.min((previewBox.clientWidth - 24) / cellWidth, (previewBox.clientHeight - 24) / cellHeight);
    }

    function renderFrame() {
      const scale = previewScale();
      const stageWidth = previewBox.clientWidth;
      const stageHeight = previewBox.clientHeight;
      const offsetX = (stageWidth - cellWidth * scale) / 2;
      const offsetY = (stageHeight - cellHeight * scale) / 2;

      spriteFrame.style.backgroundPosition = spritePosition(frame, selectedState.row);
      spriteFrame.style.transform = `translate(-50%, -50%) scale(${scale})`;
      stateTitle.textContent = selectedState.state;
      stateNote.textContent = selectedState.note;
      frameTitle.textContent = `Frame ${frame}`;
      currentReadout.textContent = `${selectedState.state} ${frame}/${selectedState.frames - 1}`;
      playPause.textContent = playing ? "暂停" : "播放";
      playPause.classList.toggle("primary", playing);

      const metric = getFrameMetric(selectedState, frame);
      if (metric) {
        const [left, top, right, bottom] = metric.bbox;
        bboxOverlay.style.display = showBbox ? "block" : "none";
        bboxOverlay.style.left = `${offsetX + left * scale}px`;
        bboxOverlay.style.top = `${offsetY + top * scale}px`;
        bboxOverlay.style.width = `${(right - left) * scale}px`;
        bboxOverlay.style.height = `${(bottom - top) * scale}px`;
        document.getElementById("metricWidth").textContent = `${metric.size[0]}px`;
        document.getElementById("metricHeight").textContent = `${metric.size[1]}px`;
        document.getElementById("metricBaseline").textContent = `${bottom}px`;
      } else {
        bboxOverlay.style.display = "none";
        document.getElementById("metricWidth").textContent = "-";
        document.getElementById("metricHeight").textContent = "-";
        document.getElementById("metricBaseline").textContent = "-";
      }

      const widths = selectedState.frame_metrics.map((item) => item.size[0]);
      document.getElementById("metricRange").textContent = widths.length ? `${Math.min(...widths)}-${Math.max(...widths)}px` : "-";

      cellOverlay.style.display = showGuide ? "block" : "none";
      cellOverlay.style.left = `${offsetX}px`;
      cellOverlay.style.top = `${offsetY}px`;
      cellOverlay.style.width = `${cellWidth * scale}px`;
      cellOverlay.style.height = `${cellHeight * scale}px`;
      centerOverlay.style.display = showGuide ? "block" : "none";
      centerOverlay.style.left = `${stageWidth / 2}px`;
      centerOverlay.style.top = `${offsetY}px`;
      centerOverlay.style.height = `${cellHeight * scale}px`;
      baselineOverlay.style.display = showGuide ? "block" : "none";
      baselineOverlay.style.left = `${offsetX}px`;
      baselineOverlay.style.top = `${offsetY + Math.round(cellHeight * 0.92) * scale}px`;
      baselineOverlay.style.width = `${cellWidth * scale}px`;
    }

    function renderErrors() {
      const panel = document.getElementById("errorsPanel");
      const list = document.getElementById("errorsList");
      panel.hidden = data.errors.length === 0;
      list.innerHTML = "";
      data.errors.forEach((error) => {
        const item = document.createElement("li");
        item.textContent = error;
        list.append(item);
      });
    }

    function renderAll() {
      renderStates();
      renderStrip();
      renderFrame();
      renderErrors();
    }

    function tick(time) {
      if (playing && selectedState.frames > 0 && time - lastTick >= 1000 / fps) {
        frame = (frame + 1) % selectedState.frames;
        lastTick = time;
        renderStrip();
        renderFrame();
      }
      requestAnimationFrame(tick);
    }

    function setBackground(mode) {
      previewBox.classList.remove("dark", "light", "green");
      if (mode !== "checker") previewBox.classList.add(mode);
      for (const id of ["bgChecker", "bgDark", "bgLight", "bgGreen"]) {
        document.getElementById(id).setAttribute("aria-pressed", "false");
      }
      document.getElementById(`bg${mode[0].toUpperCase()}${mode.slice(1)}`).setAttribute("aria-pressed", "true");
    }

    document.getElementById("fps").addEventListener("input", (event) => {
      fps = Number(event.target.value);
      document.getElementById("fpsValue").textContent = String(fps);
    });

    playPause.addEventListener("click", () => {
      playing = !playing;
      renderFrame();
    });

    document.getElementById("prevFrame").addEventListener("click", () => {
      playing = false;
      frame = (frame - 1 + selectedState.frames) % selectedState.frames;
      renderAll();
    });

    document.getElementById("nextFrame").addEventListener("click", () => {
      playing = false;
      frame = (frame + 1) % selectedState.frames;
      renderAll();
    });

    document.getElementById("bgChecker").addEventListener("click", () => setBackground("checker"));
    document.getElementById("bgDark").addEventListener("click", () => setBackground("dark"));
    document.getElementById("bgLight").addEventListener("click", () => setBackground("light"));
    document.getElementById("bgGreen").addEventListener("click", () => setBackground("green"));

    document.getElementById("toggleBbox").addEventListener("click", (event) => {
      showBbox = !showBbox;
      event.currentTarget.setAttribute("aria-pressed", String(showBbox));
      renderFrame();
    });

    document.getElementById("toggleGuide").addEventListener("click", (event) => {
      showGuide = !showGuide;
      event.currentTarget.setAttribute("aria-pressed", String(showGuide));
      renderFrame();
    });

    window.addEventListener("resize", renderFrame);
    renderAll();
    requestAnimationFrame(tick);
  </script>
</body>
</html>"""


def scaffold_project(args: argparse.Namespace) -> None:
    pet_id = args.id or pet_id_from_name(args.name)
    target = Path(args.path).expanduser().resolve() if args.path else (Path.cwd() / ".pets" / pet_id).resolve()
    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"Target exists and is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)

    ensure_build_layout(target)
    (target / "docs").mkdir(parents=True, exist_ok=True)

    manifest = {
        "id": pet_id,
        "displayName": args.name,
        "description": args.description or f"Custom Codex Pet named {args.name}.",
        "cell": [CELL_WIDTH, CELL_HEIGHT],
        "grid": [COLUMNS, len(DEFAULT_STATES)],
        "states": [spec.__dict__ for spec in DEFAULT_STATES],
    }
    (target / "pet-project.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_project_docs(target, manifest)
    print(json.dumps({"project": str(target), "id": pet_id, "displayName": args.name}, ensure_ascii=False, indent=2))


def write_project_docs(target: Path, manifest: dict[str, object]) -> None:
    name = str(manifest["displayName"])
    pet_id = str(manifest["id"])
    (target / "README.md").write_text(
        f"# {name} Codex Pet\n\n"
        "中文文档：[README.zh-CN.md](README.zh-CN.md)\n\n"
        "This project was created by Codex Pet Factory to build a Codex Pet from images or text descriptions.\n\n"
        "## Portal\n\n"
        "| English | 中文 |\n"
        "| --- | --- |\n"
        "| [Docs](docs/README.md) | [文档](docs/README.zh-CN.md) |\n"
        "| [Harness](docs/00-harness.md) | [Harness](docs/00-harness.zh-CN.md) |\n"
        "| [Action Design](docs/01-action-design.md) | [动作设计](docs/01-action-design.zh-CN.md) |\n"
        "| [Production Spec](docs/02-production-spec.md) | [制作规格](docs/02-production-spec.zh-CN.md) |\n"
        "| [Interaction Checklist](docs/03-interaction-checklist.md) | [交互清单](docs/03-interaction-checklist.zh-CN.md) |\n\n"
        "## Layout\n\n"
        "- `build/input/`: private images, descriptions, and visual references.\n"
        "- `build/work/<state>/frames/`: raw action frames.\n"
        "- `build/work/<state>/normalized/`: transparent normalized `192 x 208` frames.\n"
        "- `build/qa/`: validation, preview, contact sheet, and QA notes.\n"
        "- `build/final/`: final `spritesheet.webp` and `pet.json`.\n"
        "- `docs/`: action design, production notes, and QA.\n\n"
        "## Build\n\n"
        "```bash\n"
        "codex-pet-factory build .\n"
        "codex-pet-factory validate .\n"
        "codex-pet-factory install .\n"
        "```\n",
        encoding="utf-8",
    )
    (target / "README.zh-CN.md").write_text(
        f"# {name} Codex Pet\n\n"
        "English documentation: [README.md](README.md)\n\n"
        "这个项目由 Codex Pet Factory 创建，用于从图片或文字描述制作 Codex Pet。\n\n"
        "## 传送门\n\n"
        "| English | 中文 |\n"
        "| --- | --- |\n"
        "| [Docs](docs/README.md) | [文档](docs/README.zh-CN.md) |\n"
        "| [Harness](docs/00-harness.md) | [Harness](docs/00-harness.zh-CN.md) |\n"
        "| [Action Design](docs/01-action-design.md) | [动作设计](docs/01-action-design.zh-CN.md) |\n"
        "| [Production Spec](docs/02-production-spec.md) | [制作规格](docs/02-production-spec.zh-CN.md) |\n"
        "| [Interaction Checklist](docs/03-interaction-checklist.md) | [交互清单](docs/03-interaction-checklist.zh-CN.md) |\n\n"
        "## 目录\n\n"
        "- `build/input/`：私有图片、描述、视觉参考。\n"
        "- `build/work/<state>/frames/`：动作原始帧。\n"
        "- `build/work/<state>/normalized/`：透明 `192 x 208` 规范帧。\n"
        "- `build/qa/`：校验、预览、contact sheet 和 QA notes。\n"
        "- `build/final/`：最终 `spritesheet.webp` 和 `pet.json`。\n"
        "- `docs/`：动作设计、制作记录和 QA。\n\n"
        "## 构建\n\n"
        "```bash\n"
        "codex-pet-factory build .\n"
        "codex-pet-factory validate .\n"
        "codex-pet-factory install .\n"
        "```\n",
        encoding="utf-8",
    )
    (target / "docs/README.md").write_text(
        "# Documentation Index\n\n"
        "中文文档：[README.zh-CN.md](README.zh-CN.md)\n\n"
        "| English | 中文 |\n"
        "| --- | --- |\n"
        "| [Project README](../README.md) | [项目说明](../README.zh-CN.md) |\n"
        "| [Harness](00-harness.md) | [Harness](00-harness.zh-CN.md) |\n"
        "| [Action Design](01-action-design.md) | [动作设计](01-action-design.zh-CN.md) |\n"
        "| [Production Spec](02-production-spec.md) | [制作规格](02-production-spec.zh-CN.md) |\n"
        "| [Interaction Checklist](03-interaction-checklist.md) | [交互清单](03-interaction-checklist.zh-CN.md) |\n",
        encoding="utf-8",
    )
    (target / "docs/README.zh-CN.md").write_text(
        "# 文档传送门\n\n"
        "English documentation: [README.md](README.md)\n\n"
        "| English | 中文 |\n"
        "| --- | --- |\n"
        "| [Project README](../README.md) | [项目说明](../README.zh-CN.md) |\n"
        "| [Harness](00-harness.md) | [Harness](00-harness.zh-CN.md) |\n"
        "| [Action Design](01-action-design.md) | [动作设计](01-action-design.zh-CN.md) |\n"
        "| [Production Spec](02-production-spec.md) | [制作规格](02-production-spec.zh-CN.md) |\n"
        "| [Interaction Checklist](03-interaction-checklist.md) | [交互清单](03-interaction-checklist.zh-CN.md) |\n",
        encoding="utf-8",
    )
    (target / "docs/00-harness.md").write_text(
        f"# {name} Pet Harness\n\n"
        "中文文档：[00-harness.zh-CN.md](00-harness.zh-CN.md)\n\n"
        "## Stages\n\n"
        "1. H0 Inputs: save images, descriptions, and references.\n"
        "2. H1 Character: define a unified character sheet.\n"
        "3. H2 Motion: generate sprite frames for each state.\n"
        "4. H3 Normalize: produce transparent `192 x 208` PNG frames.\n"
        "5. H4 Package: build the Codex Pet atlas and manifest.\n"
        "6. H5 QA: run validation and inspect the contact sheet.\n"
        "7. H6 Install: copy outputs into Codex Pets.\n",
        encoding="utf-8",
    )
    (target / "docs/00-harness.zh-CN.md").write_text(
        f"# {name} Pet Harness\n\n"
        "English documentation: [00-harness.md](00-harness.md)\n\n"
        "## 阶段\n\n"
        "1. H0 输入：保存图片、描述、旧版参考。\n"
        "2. H1 角色：确定统一角色设定。\n"
        "3. H2 动作：生成每个状态的 sprite frames。\n"
        "4. H3 规范化：统一为 `192 x 208` 透明 PNG。\n"
        "5. H4 打包：生成 Codex Pet atlas 和 manifest。\n"
        "6. H5 QA：自动校验和 contact sheet 肉眼验收。\n"
        "7. H6 安装：复制到 Codex Pets 目录。\n",
        encoding="utf-8",
    )
    (target / "docs/01-action-design.md").write_text(
        "# Action Design\n\n"
        "中文文档：[01-action-design.zh-CN.md](01-action-design.zh-CN.md)\n\n"
        "| Row | State | Frames | Note | Design |\n"
        "| --- | --- | ---: | --- | --- |\n"
        + "\n".join(
            f"| {spec.row} | `{spec.state}` | {spec.frames} | {spec.note} | TBD |"
            for spec in DEFAULT_STATES
        )
        + "\n",
        encoding="utf-8",
    )
    (target / "docs/01-action-design.zh-CN.md").write_text(
        "# 动作设计\n\n"
        "English documentation: [01-action-design.md](01-action-design.md)\n\n"
        "| 行号 | 状态 | 帧数 | 中文备注 | 设计说明 |\n"
        "| --- | --- | ---: | --- | --- |\n"
        + "\n".join(
            f"| {spec.row} | `{spec.state}` | {spec.frames} | {spec.note} | 待补充 |"
            for spec in DEFAULT_STATES
        )
        + "\n",
        encoding="utf-8",
    )
    (target / "docs/02-production-spec.md").write_text(
        "# Production Spec\n\n"
        "中文文档：[02-production-spec.zh-CN.md](02-production-spec.zh-CN.md)\n\n"
        f"- Pet id: `{pet_id}`\n"
        f"- Display name: `{name}`\n"
        f"- Atlas: `{CELL_WIDTH * COLUMNS} x {CELL_HEIGHT * len(DEFAULT_STATES)}`\n"
        f"- Cell: `{CELL_WIDTH} x {CELL_HEIGHT}`\n"
        "- Format: WebP RGBA + `pet.json`\n"
        "- `running-left` should be mirrored from `running-right`.\n",
        encoding="utf-8",
    )
    (target / "docs/02-production-spec.zh-CN.md").write_text(
        "# 制作规格\n\n"
        "English documentation: [02-production-spec.md](02-production-spec.md)\n\n"
        f"- 宠物 id：`{pet_id}`\n"
        f"- 显示名：`{name}`\n"
        f"- Atlas：`{CELL_WIDTH * COLUMNS} x {CELL_HEIGHT * len(DEFAULT_STATES)}`\n"
        f"- 单元格：`{CELL_WIDTH} x {CELL_HEIGHT}`\n"
        "- 格式：WebP RGBA + `pet.json`\n"
        "- `running-left` 应由 `running-right` 镜像生成。\n",
        encoding="utf-8",
    )
    (target / "docs/03-interaction-checklist.md").write_text(
        f"# Interaction Checklist: {name}\n\n"
        "中文文档：[03-interaction-checklist.zh-CN.md](03-interaction-checklist.zh-CN.md)\n\n"
        "Use this checklist before installing the pet. Mark items only after checking `build/qa/preview.html`, "
        "`build/qa/contact-sheet.png`, and the Codex Pet runtime when available.\n\n"
        "## Build Outputs\n\n"
        "- [ ] `codex-pet-factory build .` exits with no validation errors.\n"
        "- [ ] `build/qa/preview.html` opens locally and animates every state.\n"
        "- [ ] `build/qa/contact-sheet.png` shows all used frames in the correct rows.\n"
        "- [ ] `build/final/pet.json` has the expected id, display name, and spritesheet path.\n\n"
        "## Preview Controls\n\n"
        "- [ ] Play and pause work without jumping frames.\n"
        "- [ ] Previous and next frame buttons step through the selected state correctly.\n"
        "- [ ] FPS slider updates playback speed from slow to fast.\n"
        "- [ ] Background toggles make transparent edges visible on checker, dark, light, and green.\n"
        "- [ ] BBox and guide toggles help inspect cropping, center line, and baseline.\n\n"
        "## Runtime Interactions\n\n"
        "- [ ] Idle state loops calmly and reads as the character at desktop size.\n"
        "- [ ] Running right moves with a stable rhythm and baseline.\n"
        "- [ ] Running left matches running right as a mirrored motion.\n"
        "- [ ] Waving clearly reads as an attention or greeting action.\n"
        "- [ ] Jumping has a clean anticipation, lift, and landing.\n"
        "- [ ] Failed state communicates failure, sadness, confusion, or error clearly.\n"
        "- [ ] Waiting state feels distinct from idle and can loop for longer pauses.\n"
        "- [ ] Running loop works as an in-place action without visual drift.\n"
        "- [ ] Review state reads as a special reaction or easter egg.\n\n"
        "## Visual QA\n\n"
        "- [ ] Character identity, proportions, palette, and accessories stay consistent across states.\n"
        "- [ ] No frame has colored halos, hard background remnants, or clipped body parts.\n"
        "- [ ] Frame-to-frame scale changes are intentional and not distracting.\n"
        "- [ ] Important facial or prop details remain legible at `192 x 208`.\n"
        "- [ ] Empty cells in each row remain transparent.\n\n"
        "## Install Gate\n\n"
        "- [ ] User or reviewer has approved the preview page and contact sheet.\n"
        "- [ ] `codex-pet-factory validate .` passes.\n"
        "- [ ] `codex-pet-factory install .` is run only after the checklist above passes.\n",
        encoding="utf-8",
    )
    (target / "docs/03-interaction-checklist.zh-CN.md").write_text(
        f"# 交互清单：{name}\n\n"
        "English documentation: [03-interaction-checklist.md](03-interaction-checklist.md)\n\n"
        "安装宠物前使用这份清单。请结合 `build/qa/preview.html`、`build/qa/contact-sheet.png`，以及可用时的 Codex Pet 运行时一起检查。\n\n"
        "## 构建产物\n\n"
        "- [ ] `codex-pet-factory build .` 无 validation errors。\n"
        "- [ ] `build/qa/preview.html` 可以本地打开，并能播放每个状态。\n"
        "- [ ] `build/qa/contact-sheet.png` 中所有有效帧都在正确行。\n"
        "- [ ] `build/final/pet.json` 的 id、显示名和 spritesheet 路径正确。\n\n"
        "## 预览控件\n\n"
        "- [ ] 播放/暂停不会跳帧或卡住。\n"
        "- [ ] 上一帧/下一帧能正确步进当前状态。\n"
        "- [ ] FPS 滑杆能从慢速到快速调整播放速度。\n"
        "- [ ] 棋盘、深色、浅色、绿底背景能暴露透明边缘问题。\n"
        "- [ ] BBox 和中心线开关能辅助检查裁切、中心线和基线。\n\n"
        "## 运行时交互\n\n"
        "- [ ] idle 待机循环稳定，并且桌面尺寸下仍能读出角色。\n"
        "- [ ] running-right 向右奔跑节奏和基线稳定。\n"
        "- [ ] running-left 与向右奔跑匹配，像镜像派生动作。\n"
        "- [ ] waving 能清楚读作招呼或吸引注意。\n"
        "- [ ] jumping 有清楚的蓄力、起跳和落地。\n"
        "- [ ] failed 能表达失败、难过、困惑或错误反馈。\n"
        "- [ ] waiting 与 idle 有明显区别，适合长时间等待循环。\n"
        "- [ ] running 原地循环无明显视觉漂移。\n"
        "- [ ] review 能读作特殊反应或彩蛋。\n\n"
        "## 视觉 QA\n\n"
        "- [ ] 所有状态中的角色身份、比例、色板和配饰保持一致。\n"
        "- [ ] 没有彩色毛边、背景残留或身体部位被裁掉。\n"
        "- [ ] 帧间缩放变化是有意设计，而不是抖动。\n"
        "- [ ] 关键表情或道具细节在 `192 x 208` 下仍然清楚。\n"
        "- [ ] 每行动作未使用的格子保持透明。\n\n"
        "## 安装门槛\n\n"
        "- [ ] 用户或审核者已经确认 preview page 和 contact sheet。\n"
        "- [ ] `codex-pet-factory validate .` 通过。\n"
        "- [ ] 只有上方清单通过后，才运行 `codex-pet-factory install .`。\n",
        encoding="utf-8",
    )


def validate_project(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    manifest = load_manifest(project)
    validation = build_atlas(project)
    print(
        json.dumps(
            {"qa_dir": str(qa_root(project)), "final_dir": str(final_root(project)), "errors": validation["errors"]},
            ensure_ascii=False,
            indent=2,
        )
    )
    if validation["errors"]:
        raise SystemExit(1)


def load_validation_errors(out_dir: Path) -> list[str]:
    path = out_dir / "validate.json"
    if not path.exists():
        raise SystemExit(f"Missing validation file: {path}. Run `codex-pet-factory build` first.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    errors = payload.get("errors", [])
    if not isinstance(errors, list):
        raise SystemExit(f"Invalid validation file: {path}. Expected an `errors` list.")
    return [str(error) for error in errors]


def install_project(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    manifest = load_manifest(project)
    pet_id = str(manifest["id"])
    out_dir = final_root(project)
    qa_dir = qa_root(project)
    if (
        not (out_dir / "spritesheet.webp").exists()
        or not (out_dir / "pet.json").exists()
        or not (qa_dir / "validate.json").exists()
    ):
        validation = build_atlas(project)
        errors = [str(error) for error in validation["errors"]]
    else:
        errors = load_validation_errors(qa_dir)
    if errors:
        raise SystemExit("Cannot install project with validation errors:\n- " + "\n- ".join(errors))
    pets_dir = Path(args.pets_dir).expanduser().resolve() if args.pets_dir else Path.home() / ".codex/pets"
    target = pets_dir / pet_id
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out_dir / "spritesheet.webp", target / "spritesheet.webp")
    shutil.copy2(out_dir / "pet.json", target / "pet.json")
    print(json.dumps({"installed": str(target), "displayName": manifest["displayName"]}, ensure_ascii=False, indent=2))


def build_project(args: argparse.Namespace) -> None:
    validation = build_atlas(Path(args.path).resolve())
    print(json.dumps({"errors": validation["errors"]}, ensure_ascii=False, indent=2))
    if validation["errors"]:
        raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="codex-pet-factory")
    sub = parser.add_subparsers(dest="command", required=True)

    scaffold = sub.add_parser("scaffold", help="Create a reusable Codex Pet project")
    scaffold.add_argument("path", nargs="?")
    scaffold.add_argument("--name", required=True)
    scaffold.add_argument("--id")
    scaffold.add_argument("--description")
    scaffold.add_argument("--force", action="store_true")
    scaffold.set_defaults(func=scaffold_project)

    build = sub.add_parser("build", help="Build spritesheet.webp, pet.json, and QA files")
    build.add_argument("path")
    build.set_defaults(func=build_project)

    validate = sub.add_parser("validate", help="Validate project build outputs")
    validate.add_argument("path")
    validate.set_defaults(func=validate_project)

    install = sub.add_parser("install", help="Install built pet into Codex Pets")
    install.add_argument("path")
    install.add_argument("--pets-dir")
    install.set_defaults(func=install_project)

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.func(args)
