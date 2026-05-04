from __future__ import annotations

import argparse
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


def state_source(project: Path, state: str) -> Path:
    return project / "assets/generated" / state / "normalized"


def build_atlas(project: Path) -> dict[str, object]:
    image, _image_draw, _image_font = require_pillow()
    manifest = load_manifest(project)
    pet_id = str(manifest["id"])
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

    out_dir = project / "build" / pet_id
    out_dir.mkdir(parents=True, exist_ok=True)
    atlas.save(out_dir / "spritesheet.webp", "WEBP", lossless=True, quality=100, method=6)
    (out_dir / "validate.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_pet_json(out_dir, manifest)
    write_contact_sheet(out_dir, validation)
    write_qa_notes(out_dir, validation)
    return validation


def write_pet_json(out_dir: Path, manifest: dict[str, object]) -> None:
    pet_json = {
        "id": manifest["id"],
        "displayName": manifest["displayName"],
        "description": manifest.get("description", ""),
        "spritesheetPath": "spritesheet.webp",
    }
    (out_dir / "pet.json").write_text(json.dumps(pet_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_contact_sheet(out_dir: Path, validation: dict[str, object]) -> None:
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
    atlas = image.open(out_dir / "spritesheet.webp").convert("RGBA")

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
            "- `spritesheet.webp`",
            "- `pet.json`",
            "- `contact-sheet.png`",
            "- `validate.json`",
        ]
    )
    (out_dir / "qa-notes.md").write_text(text + "\n", encoding="utf-8")


def scaffold_project(args: argparse.Namespace) -> None:
    target = Path(args.path).resolve()
    pet_id = args.id or pet_id_from_name(args.name)
    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"Target exists and is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)

    for spec in DEFAULT_STATES:
        (target / "assets/generated" / spec.state / "frames").mkdir(parents=True, exist_ok=True)
        (target / "assets/generated" / spec.state / "normalized").mkdir(parents=True, exist_ok=True)
    for directory in ("assets/reference/original", "assets/reference/visual", "docs", "build"):
        (target / directory).mkdir(parents=True, exist_ok=True)

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
        "| [Production Spec](docs/02-production-spec.md) | [制作规格](docs/02-production-spec.zh-CN.md) |\n\n"
        "## Layout\n\n"
        "- `assets/reference/`: user images, descriptions, and visual references.\n"
        "- `assets/generated/<state>/frames/`: raw action frames.\n"
        "- `assets/generated/<state>/normalized/`: transparent normalized `192 x 208` frames.\n"
        f"- `build/{pet_id}/`: final `spritesheet.webp`, `pet.json`, validation, and previews.\n"
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
        "| [Production Spec](docs/02-production-spec.md) | [制作规格](docs/02-production-spec.zh-CN.md) |\n\n"
        "## 目录\n\n"
        "- `assets/reference/`：用户图片、描述、风格参考。\n"
        "- `assets/generated/<state>/frames/`：动作原始帧。\n"
        "- `assets/generated/<state>/normalized/`：透明 `192 x 208` 规范帧。\n"
        f"- `build/{pet_id}/`：最终 `spritesheet.webp`、`pet.json`、校验和预览。\n"
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
        "| [Production Spec](02-production-spec.md) | [制作规格](02-production-spec.zh-CN.md) |\n",
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
        "| [Production Spec](02-production-spec.md) | [制作规格](02-production-spec.zh-CN.md) |\n",
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


def validate_project(args: argparse.Namespace) -> None:
    project = Path(args.path).resolve()
    manifest = load_manifest(project)
    out_dir = project / "build" / str(manifest["id"])
    validation = build_atlas(project)
    print(json.dumps({"out_dir": str(out_dir), "errors": validation["errors"]}, ensure_ascii=False, indent=2))
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
    out_dir = project / "build" / pet_id
    if (
        not (out_dir / "spritesheet.webp").exists()
        or not (out_dir / "pet.json").exists()
        or not (out_dir / "validate.json").exists()
    ):
        validation = build_atlas(project)
        errors = [str(error) for error in validation["errors"]]
    else:
        errors = load_validation_errors(out_dir)
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
    scaffold.add_argument("path")
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
