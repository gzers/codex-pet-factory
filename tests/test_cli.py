from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def has_pillow() -> bool:
    return (
        subprocess.run(
            [sys.executable, "-c", "import PIL"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SRC)
        return subprocess.run(
            [sys.executable, "-m", "codex_pet_factory", *args],
            cwd=REPO,
            env=env,
            check=False,
            text=True,
            capture_output=True,
        )

    def test_help_does_not_require_pillow(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("scaffold", result.stdout)
        self.assertIn("build", result.stdout)

    def test_scaffold_creates_project_under_pets_and_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "pets" / "test-pet"
            result = self.run_cli("scaffold", str(project), "--name", "测试宠物", "--id", "test-pet")
            self.assertEqual(result.returncode, 0, result.stderr)

            payload = json.loads(result.stdout)
            self.assertEqual(payload["id"], "test-pet")
            self.assertEqual(payload["displayName"], "测试宠物")
            self.assertEqual(Path(payload["project"]).resolve(), project.resolve())
            self.assertTrue((project / "pet-project.json").exists())
            self.assertTrue((project / "README.md").exists())
            self.assertTrue((project / "README.zh-CN.md").exists())
            self.assertTrue((project / "docs/README.md").exists())
            self.assertTrue((project / "docs/README.zh-CN.md").exists())
            self.assertTrue((project / "docs/01-action-design.md").exists())
            self.assertTrue((project / "docs/01-action-design.zh-CN.md").exists())
            self.assertTrue((project / "docs/03-interaction-checklist.md").exists())
            self.assertTrue((project / "docs/03-interaction-checklist.zh-CN.md").exists())
            self.assertIn("[文档](docs/README.zh-CN.md)", (project / "README.md").read_text(encoding="utf-8"))
            self.assertIn("[Docs](docs/README.md)", (project / "README.zh-CN.md").read_text(encoding="utf-8"))

    @unittest.skipUnless(has_pillow(), "Pillow is not installed in this Python environment.")
    def test_install_rejects_invalid_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "pets" / "bad-pet"
            pets_dir = root / "pets"
            scaffold = self.run_cli("scaffold", str(project), "--name", "坏宠物", "--id", "bad-pet")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

            result = self.run_cli("install", str(project), "--pets-dir", str(pets_dir))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Cannot install project with validation errors", result.stderr)
            self.assertFalse((pets_dir / "bad-pet").exists())

    @unittest.skipUnless(has_pillow(), "Pillow is not installed in this Python environment.")
    def test_build_with_placeholder_frames(self) -> None:
        from PIL import Image, ImageDraw
        from codex_pet_factory.spec import CELL_HEIGHT, CELL_WIDTH, DEFAULT_STATES

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "pets" / "complete-pet"
            scaffold = self.run_cli("scaffold", str(project), "--name", "完整测试", "--id", "complete-pet")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

            for spec in DEFAULT_STATES:
                for out in (
                    project / "build" / "input" / spec.state / "normalized",
                    project / "build" / "work" / spec.state / "normalized",
                ):
                    out.mkdir(parents=True, exist_ok=True)
                    for index in range(spec.frames):
                        image = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(image)
                        draw.ellipse((42, 44, 150, 152), fill=(255, 120, 90, 255))
                        image.save(out / f"frame-{index:02d}.png")

            result = self.run_cli("build", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["errors"], [])
            self.assertBuildOutputs(project, "complete-pet")

    @unittest.skipUnless(has_pillow(), "Pillow is not installed in this Python environment.")
    def test_validate_with_placeholder_frames(self) -> None:
        from PIL import Image, ImageDraw
        from codex_pet_factory.spec import CELL_HEIGHT, CELL_WIDTH, DEFAULT_STATES

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "pets" / "validate-pet"
            scaffold = self.run_cli("scaffold", str(project), "--name", "验证测试", "--id", "validate-pet")
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)

            for spec in DEFAULT_STATES:
                for out in (
                    project / "build" / "input" / spec.state / "normalized",
                    project / "build" / "work" / spec.state / "normalized",
                ):
                    out.mkdir(parents=True, exist_ok=True)
                    for index in range(spec.frames):
                        image = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(image)
                        draw.ellipse((42, 44, 150, 152), fill=(255, 120, 90, 255))
                        image.save(out / f"frame-{index:02d}.png")

            result = self.run_cli("validate", str(project))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["errors"], [])
            self.assertBuildOutputs(project, "validate-pet")

    def assertBuildOutputs(self, project: Path, pet_id: str) -> None:
        final_dir = project / "build" / "final"
        qa_dir = project / "build" / "qa"
        input_dir = project / "build" / "input"
        work_dir = project / "build" / "work"

        self.assertEqual(final_dir.parent, qa_dir.parent)
        self.assertTrue((final_dir / "pet.json").exists(), pet_id)
        self.assertTrue((final_dir / "spritesheet.webp").exists(), pet_id)
        self.assertTrue((qa_dir / "contact-sheet.png").exists(), pet_id)
        self.assertTrue((qa_dir / "preview.html").exists(), pet_id)
        self.assertTrue((qa_dir / "validate.json").exists(), pet_id)
        self.assertTrue(input_dir.exists(), pet_id)
        self.assertTrue(work_dir.exists(), pet_id)


if __name__ == "__main__":
    unittest.main()
