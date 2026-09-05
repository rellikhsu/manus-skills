"""Exercise the real dist transformer and validator in disposable collections."""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ManusDist(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="manus-dist-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        scripts = self.root / "scripts"
        scripts.mkdir()
        for name in ("transform-for-manus.py", "validate-dist.py"):
            shutil.copyfile(ROOT / "scripts" / name, scripts / name)
        self.collection = self.root / "skills/harness-engineering"
        self.child = self.collection / "which-loop/SKILL.md"
        self.child.parent.mkdir(parents=True)
        self.bundle = self.collection / "SKILL.md"
        self.bundle.write_text(
            "---\nname: harness-engineering\ndescription: Collection fixture.\n---\n"
            "# Collection\nRead the matching child SKILL.md.\n", encoding="utf-8"
        )
        self.original = (
            "---\nname: which-loop\ndescription: Use when composing a workflow.\n---\n"
            "# Which Loop\n\n```yaml\nname: preserve-body-example\n```\n"
        )
        self.child.write_text(self.original, encoding="utf-8")

    def run_script(self, name):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / name)],
            cwd=self.root, capture_output=True, text=True, check=False,
        )

    def test_transform_prefixes_only_child_frontmatter(self):
        bundle_before = self.bundle.read_bytes()
        result = self.run_script("transform-for-manus.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = (
            '---\nname: "harness-engineering:which-loop"\n'
            'description: Use when composing a workflow.\n---\n'
            '# Which Loop\n\n```yaml\nname: preserve-body-example\n```\n'
        )
        self.assertEqual(self.child.read_text(encoding="utf-8"), expected)
        self.assertEqual(self.bundle.read_bytes(), bundle_before)
        result = self.run_script("validate-dist.py")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_repeated_transform_is_byte_identical(self):
        self.assertEqual(self.run_script("transform-for-manus.py").returncode, 0)
        first = self.child.read_bytes()
        result = self.run_script("transform-for-manus.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.child.read_bytes(), first)

    def test_validation_rejects_unconverted_child(self):
        result = self.run_script("validate-dist.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.child.read_text(encoding="utf-8"), self.original)

    def test_validation_rejects_a_different_namespace(self):
        self.child.write_text(self.original.replace(
            "name: which-loop", 'name: "different:which-loop"', 1
        ), encoding="utf-8")
        result = self.run_script("validate-dist.py")
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
