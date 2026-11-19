"""Exercise the real dist transformer and validator in disposable collections.

The dist tree exists to satisfy one Manus constraint: an imported GitHub
subdirectory must not contain more than 100 files. These tests lock in the
pruning pass, the namespace splitting, the name-prefix contract, and the guard
that fails the weekly sync when a bundle grows past the limit.
"""

from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TemporaryTree:
    """A throwaway mirror root holding a copy of the scripts under test."""

    def __init__(self):
        self._temporary = tempfile.TemporaryDirectory(prefix="manus-dist-")
        self.root = Path(self._temporary.name)
        shutil.copytree(ROOT / "scripts", self.root / "scripts")
        (self.root / "metadata").mkdir()
        self.add_cleanup = self._temporary.cleanup

    @property
    def manifest_path(self):
        return self.root / "metadata" / "manus-imports.tsv"

    def write_bundle_map(self, text):
        (self.root / "metadata" / "manus-bundles.tsv").write_text(text, encoding="utf-8")

    def read_manifest(self):
        return self.manifest_path.read_text(encoding="utf-8")

    def write_namespace_root(self, namespace, description="Collection fixture."):
        root_file = self.root / "skills" / namespace / "SKILL.md"
        root_file.parent.mkdir(parents=True, exist_ok=True)
        root_file.write_text(
            f"---\nname: {namespace}\ndescription: {description}\n---\n"
            f"# {namespace}\nRead the matching child SKILL.md.\n",
            encoding="utf-8",
        )
        return root_file

    def write_skill(self, namespace, skill, extra_files=0, with_agent_manifest=True):
        directory = self.root / "skills" / namespace / skill
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: Use for the {skill} workflow.\n---\n" f"# {skill}\n",
            encoding="utf-8",
        )
        for index in range(extra_files):
            (directory / f"reference-{index}.md").write_text("reference\n", encoding="utf-8")
        if with_agent_manifest:
            manifest = directory / "agents"
            manifest.mkdir()
            (manifest / "openai.yaml").write_text("name: other-cli\n", encoding="utf-8")
        return directory

    def run(self, name):
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / name)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def snapshot(self):
        return {
            path.relative_to(self.root).as_posix(): path.read_bytes()
            for path in sorted((self.root / "skills").rglob("*"))
            if path.is_file()
        }


class ManusDist(unittest.TestCase):
    def setUp(self):
        self.tree = TemporaryTree()
        self.addCleanup(self.tree.add_cleanup)
        self.root = self.tree.root
        self.collection = self.root / "skills/harness-engineering"
        self.child = self.collection / "which-loop/SKILL.md"
        self.child.parent.mkdir(parents=True)
        self.bundle = self.collection / "SKILL.md"
        self.bundle.write_text(
            "---\nname: harness-engineering\ndescription: Collection fixture.\n---\n"
            "# Collection\nRead the matching child SKILL.md.\n",
            encoding="utf-8",
        )
        self.original = (
            "---\nname: which-loop\ndescription: Use when composing a workflow.\n---\n"
            "# Which Loop\n\n```yaml\nname: preserve-body-example\n```\n"
        )
        self.child.write_text(self.original, encoding="utf-8")

    def run_script(self, name):
        return self.tree.run(name)

    def test_transform_prefixes_only_child_frontmatter(self):
        bundle_before = self.bundle.read_bytes()
        result = self.run_script("transform-for-manus.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        expected = (
            '---\nname: "harness-engineering:which-loop"\n'
            "description: Use when composing a workflow.\n---\n"
            "# Which Loop\n\n```yaml\nname: preserve-body-example\n```\n"
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
        self.child.write_text(
            self.original.replace("name: which-loop", 'name: "different:which-loop"', 1),
            encoding="utf-8",
        )
        result = self.run_script("validate-dist.py")
        self.assertNotEqual(result.returncode, 0)

    def test_validation_reports_the_bundle_that_is_over_the_limit(self):
        self.assertEqual(self.run_script("transform-for-manus.py").returncode, 0)
        for index in range(120):
            (self.collection / "which-loop" / f"reference-{index}.md").write_text(
                "reference\n", encoding="utf-8"
            )
        result = self.run_script("validate-dist.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("import limit", result.stderr)


class ManusImportBudget(unittest.TestCase):
    """Pruning and splitting: the two passes that make big namespaces importable."""

    def setUp(self):
        self.tree = TemporaryTree()
        self.addCleanup(self.tree.add_cleanup)
        self.root = self.tree.root

    def test_pruning_removes_foreign_agent_manifests_and_empty_dirs(self):
        self.tree.write_namespace_root("acme")
        skill = self.tree.write_skill("acme", "alpha")
        result = self.tree.run("transform-for-manus.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((skill / "agents" / "openai.yaml").exists())
        self.assertFalse((skill / "agents").exists())
        self.assertEqual(sorted(path.name for path in skill.iterdir()), ["SKILL.md"])
        self.assertIn("acme\t", self.tree.read_manifest())

    def test_split_namespace_stays_under_the_import_limit(self):
        namespace = "broad"
        self.tree.write_namespace_root(namespace)
        for skill in ("alpha-skill", "beta-skill", "gamma-skill"):
            self.tree.write_skill(namespace, skill, extra_files=30)
        self.tree.write_bundle_map(
            "namespace\tbundle\tdescription\tskills\n"
            f"{namespace}\tcore\tFirst half of the broad namespace.\talpha-skill, beta-skill\n"
            f"{namespace}\tafter\tSecond half of the broad namespace.\tgamma-skill\n"
        )
        result = self.tree.run("transform-for-manus.py")
        self.assertEqual(result.returncode, 0, result.stderr)

        # The namespace root is replaced by one navigation root per bundle.
        self.assertFalse((self.root / "skills" / namespace / "SKILL.md").exists())
        core = self.root / "skills" / namespace / "core"
        self.assertTrue((core / "alpha-skill" / "SKILL.md").is_file())
        self.assertTrue((core / "beta-skill" / "SKILL.md").is_file())
        self.assertFalse((self.root / "skills" / namespace / "alpha-skill").exists())

        root_text = (core / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: broad-core", root_text)
        self.assertIn("First half of the broad namespace.", root_text)
        self.assertIn("- `broad:gamma-skill`", (core.parent / "after" / "SKILL.md").read_text("utf-8"))

        # Splitting must never rename a skill.
        self.assertIn(
            'name: "broad:alpha-skill"',
            (core / "alpha-skill" / "SKILL.md").read_text(encoding="utf-8"),
        )
        manifest = self.tree.read_manifest()
        self.assertIn(f"{DIST}/skills/{namespace}/core", manifest)
        self.assertIn("broad-after", manifest)
        self.assertEqual(self.tree.run("validate-dist.py").returncode, 0)

        # A second run must not move or rewrite anything again.
        snapshot = self.tree.snapshot()
        self.assertEqual(self.tree.run("transform-for-manus.py").returncode, 0)
        self.assertEqual(self.tree.snapshot(), snapshot)

    def test_transform_fails_when_a_bundle_is_over_the_limit(self):
        namespace = "oversized"
        self.tree.write_namespace_root(namespace)
        self.tree.write_skill(namespace, "huge-skill", extra_files=140)
        result = self.tree.run("transform-for-manus.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("import limit", result.stderr)

    def test_validate_rejects_a_stale_manifest(self):
        self.tree.write_namespace_root("acme")
        self.tree.write_skill("acme", "alpha")
        self.assertEqual(self.tree.run("transform-for-manus.py").returncode, 0)
        self.tree.manifest_path.write_text("bundle_name\n", encoding="utf-8")
        self.assertNotEqual(self.tree.run("validate-dist.py").returncode, 0)

    def test_bundle_map_missing_a_skill_is_fatal(self):
        namespace = "unmapped"
        self.tree.write_namespace_root(namespace)
        self.tree.write_skill(namespace, "alpha-skill")
        self.tree.write_skill(namespace, "forgot-me")
        self.tree.write_bundle_map(
            "namespace\tbundle\tdescription\tskills\n"
            f"{namespace}\tcore\tDeclared half.\talpha-skill\n"
        )
        result = self.tree.run("transform-for-manus.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forgot-me", result.stderr + result.stdout)

    def test_bundle_name_colliding_with_a_skill_name_is_fatal(self):
        namespace = "clashing"
        self.tree.write_namespace_root(namespace)
        self.tree.write_skill(namespace, "core")
        self.tree.write_bundle_map(
            "namespace\tbundle\tdescription\tskills\n"
            f"{namespace}\tcore\tBundle named like its only skill.\tcore\n"
        )
        result = self.tree.run("transform-for-manus.py")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("collides", result.stderr + result.stdout)


DIST = "https://github.com/rellikhsu/manus-skills/tree/dist"

if __name__ == "__main__":
    unittest.main()
