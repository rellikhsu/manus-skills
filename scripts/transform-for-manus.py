#!/usr/bin/env python3
"""Prepare the generated ``dist`` tree so every bundle fits Manus's import rules.

Manus imports one GitHub subdirectory per skill bundle and refuses any tree with
more than 100 files, so ``main`` (640 files) and whole namespaces such as ``aws``
(378 files) can never be imported as-is. This script turns the pristine mirror on
``main`` into an import-ready tree on ``dist`` in four deterministic passes:

1. prune files no Manus runtime reads (other CLIs' agent manifests, junk);
2. prefix every child skill frontmatter ``name`` with ``<namespace>``, leaving
   bundle roots and all instruction bodies untouched;
3. split namespaces declared in ``metadata/manus-bundles.tsv`` into thematic
   bundle directories, each with its own generated navigation root;
4. write ``metadata/manus-imports.tsv`` and fail when any bundle is over limit.

Splitting never renames a skill: children keep the ``<namespace>:`` prefix even
after moving to ``skills/aws/serverless/``, so already-imported skill names stay
stable across the weekly sync.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bundle_layout as layout  # noqa: E402

ROOT_DIR = SCRIPT_DIR.parent
SKILLS_DIR = ROOT_DIR / "skills"

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)


def prefix_child_names(namespace_dir: Path, namespace: str, skills_dir: Path) -> int:
    """Rewrite child frontmatter names to ``"<namespace>:<name>"``."""
    changed = 0
    for skill_file in layout.iter_skill_files(namespace_dir, skills_dir):
        content = skill_file.read_text(encoding="utf-8")
        match = FRONTMATTER_RE.search(content)
        if not match:
            continue
        frontmatter = match.group(1)
        name_match = NAME_RE.search(frontmatter)
        if not name_match:
            continue
        raw_name = name_match.group(1).strip().strip("\"'")
        if raw_name.startswith(f"{namespace}:"):
            continue
        new_name = f"{namespace}:{raw_name}"
        new_frontmatter = NAME_RE.sub(lambda found: f'name: "{new_name}"', frontmatter, count=1)
        skill_file.write_text(
            content[: match.start(1)] + new_frontmatter + content[match.end(1) :],
            encoding="utf-8",
        )
        changed += 1
        print(f"Prefixed: [{skill_file.relative_to(ROOT_DIR)}] -> '{new_name}'")
    return changed


def prune_files(skills_dir: Path) -> int:
    """Delete files Manus never loads, then drop directories left empty."""
    removed = 0
    for path in sorted(p for p in skills_dir.rglob("*") if p.is_file()):
        if layout.prunable(path.relative_to(skills_dir)):
            path.unlink()
            removed += 1
            print(f"Pruned: [{path.relative_to(ROOT_DIR)}]")
    for directory in sorted(
        (p for p in skills_dir.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True
    ):
        if not any(directory.iterdir()):
            directory.rmdir()
    return removed


def render_bundle_root(namespace: str, bundle: str, description: str, skills: list[str]) -> str:
    """Render the deterministic navigation root of a split bundle."""
    title = bundle.replace("-", " ").title()
    lines = [
        "---",
        f"name: {namespace}-{bundle}",
        f"description: {json.dumps(description, ensure_ascii=False)}",
        "---",
        "",
        f"# {title} ({namespace} skills)",
        "",
        f"Navigation skill for this slice of the `{namespace}` namespace.",
        "Manus imports one GitHub subdirectory per bundle and refuses trees larger than "
        f"{layout.MAX_IMPORT_FILES} files, so the namespace is published in sized slices.",
        "Read the matching child `SKILL.md` before executing the requested workflow.",
        f"Child skills keep their upstream `{namespace}:` name prefix.",
        "Prefer the narrowest matching child skill. This bundle does not replace "
        "project-specific instructions, safety requirements, or the user's explicit request.",
        "",
        "## Skills in this bundle",
        "",
    ]
    lines += [f"- `{skill}`" for skill in sorted(skills)]
    return "\n".join(lines) + "\n"


def split_namespace(namespace_dir: Path, groups: list[dict[str, object]]) -> int:
    """Move declared skills into bundle directories and write each bundle root."""
    namespace = namespace_dir.name
    moved = 0
    skill_names = {path.name for path in layout.iter_skill_dirs(namespace_dir, namespace_dir.parent)}
    for group in groups:
        bundle = str(group["bundle"])
        if bundle in skill_names:
            raise SystemExit(
                f"ERROR: bundle name collides with a skill name: {namespace}/{bundle}"
            )
    for group in groups:
        bundle = str(group["bundle"])
        members = [str(skill) for skill in group["skills"]]  # type: ignore[arg-type]
        bundle_dir = namespace_dir / bundle
        bundle_dir.mkdir(parents=True, exist_ok=True)
        for skill in members:
            source = namespace_dir / skill
            target = bundle_dir / skill
            if source.is_dir():
                if target.exists():
                    raise SystemExit(f"ERROR: cannot move {source} onto existing {target}")
                shutil.move(str(source), str(target))
                moved += 1
            elif not target.is_dir():
                raise SystemExit(f"ERROR: skill directory not found: {namespace_dir}/{skill}")
        (bundle_dir / "SKILL.md").write_text(
            render_bundle_root(
                namespace,
                bundle,
                str(group["description"]),
                sorted(f"{namespace}:{skill}" for skill in members),
            ),
            encoding="utf-8",
        )
    stale = namespace_dir / "SKILL.md"
    if stale.is_file():
        stale.unlink()
        print(f"Replaced namespace root with bundle roots: [{stale.relative_to(ROOT_DIR)}]")
    return moved


def main() -> int:
    skills_dir = SKILLS_DIR
    if not skills_dir.is_dir():
        raise SystemExit("Skills directory not found.")
    bundle_map = layout.load_bundle_map(skills_dir)

    pruned = prune_files(skills_dir)
    prefixed = 0
    for namespace_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        prefixed += prefix_child_names(namespace_dir, namespace_dir.name, skills_dir)

    moved = 0
    for namespace in sorted(bundle_map):
        namespace_dir = skills_dir / namespace
        if namespace_dir.is_dir():
            moved += split_namespace(namespace_dir, bundle_map[namespace])

    bundles = layout.discover(skills_dir)
    manifest = layout.write_imports(bundles, skills_dir)
    width = max(len(bundle.name) for bundle in bundles)
    for bundle in layout.sorted_bundles(bundles):
        print(
            f"Bundle: {bundle.name:<{width}}  skills={len(bundle.skills):>3}  "
            f"files={bundle.file_count:>4}/{layout.MAX_IMPORT_FILES}  {bundle.status}"
        )
    print(
        f"Transformed for Manus: pruned={pruned} prefixed={prefixed} moved={moved} "
        f"bundles={len(bundles)}; manifest -> {manifest}"
    )

    offenders = layout.over_limit(bundles)
    for bundle in offenders:
        print(f"ERROR: bundle exceeds the Manus import limit: {bundle}", file=sys.stderr)
    return 1 if offenders else 0


if __name__ == "__main__":
    raise SystemExit(main())
