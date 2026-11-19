#!/usr/bin/env python3
"""Validate the generated ``dist`` tree before it is published for Manus import.

Checks, in order:

1. every child skill frontmatter ``name`` is ``"<namespace>:<skill>"`;
2. every bundle exists on disk with a navigation root;
3. files that must not ship to Manus are absent;
4. each bundle stays inside the 100-file Manus import limit;
5. ``metadata/manus-imports.tsv`` matches the layout, so the published import
   list can never drift from the tree it describes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bundle_layout as layout  # noqa: E402

ROOT_DIR = SCRIPT_DIR.parent
SKILLS_DIR = ROOT_DIR / "skills"

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
NAME_VALUE_RE = re.compile(r"[A-Za-z0-9_-]+:[A-Za-z0-9_-]+")

errors: list[str] = []


def child_skill_files(skills_dir: Path) -> list[Path]:
    files: list[Path] = []
    for namespace_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        files.extend(layout.iter_skill_files(namespace_dir, skills_dir))
    return files


def validate_skill_file(skill_file: Path) -> None:
    relative = skill_file.relative_to(SKILLS_DIR)
    content = skill_file.read_text(encoding="utf-8")
    frontmatter_match = FRONTMATTER_RE.match(content)
    name_match = frontmatter_match and NAME_RE.search(frontmatter_match.group(1))
    raw_name = name_match.group(1).strip().strip("'\"") if name_match else ""
    namespace = relative.parts[0]
    if not NAME_VALUE_RE.fullmatch(raw_name) or not raw_name.startswith(f"{namespace}:"):
        errors.append(f"Invalid child skill name in {skill_file}: {raw_name!r}")


def validate_no_pruned_files(skills_dir: Path) -> int:
    shipped = [
        path
        for path in sorted(p for p in skills_dir.rglob("*") if p.is_file())
        if layout.prunable(path.relative_to(skills_dir))
    ]
    for path in shipped:
        errors.append(f"File excluded from Manus imports is still present: {path}")
    return len(shipped)


def validate_bundles(skills_dir: Path, bundle_list: list[layout.Bundle]) -> int:
    kept = 0
    for bundle in bundle_list:
        bundle_dir = skills_dir / Path(*bundle.relative_path.split("/"))
        if not (bundle_dir / "SKILL.md").is_file():
            errors.append(f"Bundle root missing: {bundle_dir}/SKILL.md")
            continue
        if not bundle.skills:
            errors.append(f"Bundle has no child skills: {bundle.name}")
        files = [path for path in bundle_dir.rglob("*") if path.is_file()]
        if len(files) != bundle.file_count:
            errors.append(
                f"Bundle {bundle.name} holds {len(files)} files but the manifest "
                f"declares {bundle.file_count}"
            )
        if len(files) > layout.MAX_IMPORT_FILES:
            errors.append(
                f"Bundle {bundle.name} exceeds the Manus import limit: "
                f"{len(files)} files > {layout.MAX_IMPORT_FILES}"
            )
        elif len(files) > layout.WARN_IMPORT_FILES:
            print(
                f"WARNING: bundle {bundle.name} is close to the import limit: "
                f"{len(files)}/{layout.MAX_IMPORT_FILES} files"
            )
        kept += len(files)
    return kept


def validate_manifest(skills_dir: Path, bundle_list: list[layout.Bundle]) -> None:
    path = layout.metadata_file(skills_dir, layout.IMPORTS_NAME)
    if not path.is_file():
        errors.append(f"Import manifest missing: {path}")
        return
    if path.read_text(encoding="utf-8") != layout.render_imports(bundle_list):
        errors.append(f"Import manifest is stale, regenerate it: {path}")


def main() -> None:
    skills_dir = SKILLS_DIR
    skill_files = child_skill_files(skills_dir)
    if not skill_files:
        raise SystemExit("ERROR: No SKILL.md files found.")
    for skill_file in skill_files:
        validate_skill_file(skill_file)

    bundle_list = layout.discover(skills_dir)
    shipped = validate_no_pruned_files(skills_dir)
    total_files = validate_bundles(skills_dir, bundle_list)
    validate_manifest(skills_dir, bundle_list)

    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        raise SystemExit(1)
    print(
        f"Validated dist: {len(skill_files)} child skills in {len(bundle_list)} bundles, "
        f"{total_files} files, largest bundle "
        f"{max(bundle.file_count for bundle in bundle_list)}/{layout.MAX_IMPORT_FILES}, "
        f"{shipped} pruned files present"
    )


if __name__ == "__main__":
    main()
