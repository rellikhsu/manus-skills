#!/usr/bin/env python3
"""Compute the Manus-importable bundle layout for the generated ``dist`` tree.

Manus imports a GitHub subdirectory as one skill bundle and rejects any tree
holding more than 100 files. This module is the single source of truth for the
layout that satisfies that limit:

* files no Manus runtime reads are pruned (see ``PRUNE_TRAILING_PARTS``);
* a namespace still over the limit after pruning is split into thematic bundles
  declared in ``metadata/manus-bundles.tsv``;
* child skill names always keep the ``<namespace>:<skill>`` prefix, so splitting
  a namespace never renames a skill.

``discover`` reads either layout, so it reports the same result for the
pristine ``main`` tree and for an already transformed ``dist`` tree. That is
what keeps the transform idempotent and ``metadata/manus-imports.tsv``
identical on both branches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

REPO_URL = "https://github.com/rellikhsu/manus-skills"
DIST_BRANCH_URL = f"{REPO_URL}/tree/dist"

MAX_IMPORT_FILES = 100  # Manus GitHub import hard limit.
WARN_IMPORT_FILES = 85  # Headroom before upstream growth breaks an import.

BUNDLE_MAP_NAME = "manus-bundles.tsv"
IMPORTS_NAME = "manus-imports.tsv"
SOURCES_NAME = "skill-sources.tsv"

# Paths Manus never loads, matched on trailing paths so the test is independent
# of how deep the skill sits: other CLIs' per-child agent manifests and junk.
PRUNE_TRAILING_PARTS = (("agents", "openai.yaml"),)
PRUNE_BASENAMES = {".DS_Store", "Thumbs.db"}

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)


def metadata_file(skills_dir: Path, name: str) -> Path:
    """Resolve a metadata file beside the skills tree being processed."""
    return skills_dir.parent / "metadata" / name


def prunable(relative_path: Path) -> bool:
    """Return True when a relative path must not ship to Manus.

    Matching on trailing path components keeps the answer the same whether the
    caller measures from the skill directory, the namespace, or ``skills/``.
    """
    parts = relative_path.parts
    return any(tuple(parts[-len(trailing) :]) == trailing for trailing in PRUNE_TRAILING_PARTS) or (
        relative_path.name in PRUNE_BASENAMES
    )


def read_frontmatter_value(skill_file: Path, key: str) -> str:
    """Read one top-level frontmatter key, joining folded block scalars."""
    if not skill_file.is_file():
        return ""
    match = FRONTMATTER_RE.match(skill_file.read_text(encoding="utf-8"))
    if not match:
        return ""
    lines = match.group(1).splitlines()
    pattern = re.compile(rf"^{key}:[ \t]*(.*)$")
    for index, line in enumerate(lines):
        found = pattern.match(line)
        if not found:
            continue
        value = found.group(1).strip()
        if value not in {">", "|", ">-", "|-", ">%", "|>"}:
            return value.strip("\"'")
        block = []
        for follow in lines[index + 1 :]:
            if follow and not follow[0].isspace():
                break
            block.append(follow.strip())
        return " ".join(part for part in block if part)
    return ""


def is_skill_dir(directory: Path) -> bool:
    return (directory / "SKILL.md").is_file()


def is_bundle_root(directory: Path, skills_dir: Path) -> bool:
    """A skill directory is a bundle root when its parent carries no ``SKILL.md``."""
    if not is_skill_dir(directory):
        return False
    return directory.parent == skills_dir or not is_skill_dir(directory.parent)


def iter_skill_dirs(namespace_dir: Path, skills_dir: Path) -> list[Path]:
    """Every skill directory under a namespace that is not itself a bundle root.

    Skill directories sit one level below the namespace on ``main`` and two on a
    split ``dist`` tree, so the root test is what distinguishes them.
    """
    return sorted(
        directory
        for skill_file in namespace_dir.rglob("SKILL.md")
        if (directory := skill_file.parent) != namespace_dir
        and not is_bundle_root(directory, skills_dir)
    )


def iter_skill_files(namespace_dir: Path, skills_dir: Path) -> list[Path]:
    """``iter_skill_dirs`` as ``SKILL.md`` paths."""
    return [directory / "SKILL.md" for directory in iter_skill_dirs(namespace_dir, skills_dir)]


def kept_files(skill_dir: Path) -> list[Path]:
    """Files in a skill directory that survive pruning."""
    return sorted(
        path
        for path in skill_dir.rglob("*")
        if path.is_file() and not prunable(path.relative_to(skill_dir))
    )


def load_bundle_map(skills_dir: Path) -> dict[str, list[dict[str, object]]]:
    """Read the bundle map into ``namespace -> group records``."""
    path = metadata_file(skills_dir, BUNDLE_MAP_NAME)
    if not path.is_file():
        return {}
    groups: dict[str, list[dict[str, object]]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("namespace\t"):
            continue
        cells = line.split("\t")
        if len(cells) < 4:
            raise SystemExit(f"ERROR: Malformed bundle map row: {line}")
        groups.setdefault(cells[0], []).append(
            {
                "bundle": cells[1],
                "description": cells[2],
                "skills": [skill.strip() for skill in cells[3].split(",") if skill.strip()],
            }
        )
    return groups


def load_upstream_repos(skills_dir: Path) -> dict[str, str]:
    """Namespace -> upstream repository, from ``metadata/skill-sources.tsv``."""
    path = metadata_file(skills_dir, SOURCES_NAME)
    repos: dict[str, str] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            cells = line.split("\t")
            if len(cells) >= 3 and cells[0] != "namespace":
                repos[cells[0]] = cells[2]
    return repos


@dataclass
class Bundle:
    namespace: str
    name: str
    relative_path: str  # path under skills/, POSIX separators
    description: str
    skills: list[str] = field(default_factory=list)
    file_count: int = 0
    upstream: str = ""

    @property
    def import_url(self) -> str:
        return f"{DIST_BRANCH_URL}/skills/{self.relative_path}"

    @property
    def status(self) -> str:
        if self.file_count > MAX_IMPORT_FILES:
            return f"OVER-LIMIT by {self.file_count - MAX_IMPORT_FILES}"
        if self.file_count > WARN_IMPORT_FILES:
            return f"near-limit ({MAX_IMPORT_FILES - self.file_count} files headroom)"
        return "ok"

    def __str__(self) -> str:
        return (
            f"{self.name} ({self.relative_path}): {self.file_count} files, "
            f"{len(self.skills)} skills"
        )


def is_split(namespace_dir: Path, groups: list[dict[str, object]]) -> bool:
    """True when the namespace directory already uses the bundle layout."""
    bundles = {str(group["bundle"]) for group in groups}
    return any(
        path.is_dir() and path.name in bundles and is_skill_dir(path)
        for path in namespace_dir.iterdir()
    )


def _build_bundle(
    namespace_dir: Path,
    namespace: str,
    skills_dir: Path,
    group: str,
    description: str,
    upstream: str,
    members: set[str] | None,
) -> Bundle:
    """Measure one bundle from the skill directories it will contain."""
    skill_dirs = iter_skill_dirs(namespace_dir, skills_dir)
    if members is not None:
        skill_dirs = [path for path in skill_dirs if path.name in members]
    if group:
        if any(path.name == group for path in skill_dirs):
            raise SystemExit(
                f"ERROR: bundle name collides with a skill name: {namespace}/{group}"
            )
        relative_path = f"{namespace}/{group}"
        name = f"{namespace}-{group}"
    else:
        relative_path = namespace
        name = namespace
    # +1 counts the generated bundle root SKILL.md.
    file_count = sum(len(kept_files(path)) for path in skill_dirs) + 1
    return Bundle(
        namespace=namespace,
        name=name,
        relative_path=relative_path,
        description=description,
        skills=sorted(f"{namespace}:{path.name}" for path in skill_dirs),
        file_count=file_count,
        upstream=upstream,
    )


def discover(skills_dir: Path = SKILLS_DIR) -> list[Bundle]:
    """Describe every importable bundle, independent of the current layout."""
    bundle_map = load_bundle_map(skills_dir)
    upstream_repos = load_upstream_repos(skills_dir)
    bundles: list[Bundle] = []

    for namespace_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        namespace = namespace_dir.name
        groups = bundle_map.get(namespace)
        upstream = upstream_repos.get(namespace, "")
        if not groups:
            bundles.append(
                _build_bundle(
                    namespace_dir,
                    namespace,
                    skills_dir,
                    "",
                    read_frontmatter_value(namespace_dir / "SKILL.md", "description"),
                    upstream,
                    None,
                )
            )
            continue
        assigned: dict[str, str] = {}
        for group in groups:
            for skill in group["skills"]:
                if skill in assigned:
                    raise SystemExit(
                        f"ERROR: skill {skill} declared in two bundles for {namespace}"
                    )
                assigned[skill] = str(group["bundle"])
        if is_split(namespace_dir, groups):
            # Already split: a leftover directory would silently drop its skills
            # from every bundle, so refuse rather than shipping an incomplete tree.
            for group in groups:
                bundle_dir = namespace_dir / str(group["bundle"])
                expected = {str(skill) for skill in group["skills"]}
                actual = {
                    path.name for path in bundle_dir.iterdir() if path.is_dir() and is_skill_dir(path)
                }
                if actual != expected:
                    raise SystemExit(
                        f"ERROR: bundle {namespace}/{group['bundle']} holds {sorted(actual)} "
                        f"but the map declares {sorted(expected)}"
                    )
            leftovers = sorted(
                path.name
                for path in namespace_dir.iterdir()
                if path.is_dir() and path.name not in {str(g["bundle"]) for g in groups}
            )
            if leftovers:
                raise SystemExit(
                    f"ERROR: {namespace} holds directories that no bundle declares: "
                    + ", ".join(leftovers)
                )
        else:
            found = {path.name for path in iter_skill_dirs(namespace_dir, skills_dir)}
            missing = sorted(found - set(assigned))
            if missing:
                raise SystemExit(
                    f"ERROR: skills missing from the bundle map for {namespace}: "
                    + ", ".join(missing)
                )
            stale = sorted(set(assigned) - found)
            if stale:
                raise SystemExit(
                    f"ERROR: bundle map names skills absent from {namespace}: " + ", ".join(stale)
                )
        for group in groups:
            bundles.append(
                _build_bundle(
                    namespace_dir,
                    namespace,
                    skills_dir,
                    str(group["bundle"]),
                    str(group["description"]),
                    upstream,
                    set(group["skills"]),
                )
            )
    return bundles


def sorted_bundles(bundles: list[Bundle]) -> list[Bundle]:
    return sorted(bundles, key=lambda item: (item.namespace, item.name))


def render_imports(bundles: list[Bundle]) -> str:
    """Deterministic TSV listing every bundle Manus should be pointed at."""
    header = "\t".join(
        [
            "bundle_name",
            "manus_github_import_url",
            "upstream_repository",
            "skill_count",
            "file_count",
            "import_status",
        ]
    )
    rows = [
        "\t".join(
            [
                bundle.name,
                bundle.import_url,
                bundle.upstream,
                str(len(bundle.skills)),
                str(bundle.file_count),
                bundle.status,
            ]
        )
        for bundle in sorted_bundles(bundles)
    ]
    return "\n".join([header, *rows]) + "\n"


def write_imports(bundles: list[Bundle], skills_dir: Path = SKILLS_DIR) -> Path:
    target = metadata_file(skills_dir, IMPORTS_NAME)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_imports(bundles), encoding="utf-8")
    return target


def over_limit(bundles: list[Bundle]) -> list[Bundle]:
    return [bundle for bundle in bundles if bundle.file_count > MAX_IMPORT_FILES]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skills-dir", type=Path, default=SKILLS_DIR)
    parser.add_argument("--write", action="store_true", help="write metadata/manus-imports.tsv")
    parser.add_argument("--json", action="store_true", help="emit the layout as JSON")
    parser.add_argument("--check", action="store_true", help="fail when a bundle is over limit")
    args = parser.parse_args(argv)

    bundles = discover(args.skills_dir)
    if args.json:
        print(
            json.dumps(
                [
                    {
                        "bundle": bundle.name,
                        "path": bundle.relative_path,
                        "skills": len(bundle.skills),
                        "files": bundle.file_count,
                        "status": bundle.status,
                    }
                    for bundle in sorted_bundles(bundles)
                ],
                indent=2,
            )
        )
    if args.write:
        target = write_imports(bundles, args.skills_dir)
        print(f"Wrote {target}: {len(bundles)} bundles")
    if not args.json and not args.write:
        width = max(len(bundle.name) for bundle in bundles)
        for bundle in sorted_bundles(bundles):
            print(
                f"{bundle.name:<{width}}  skills={len(bundle.skills):>3}  "
                f"files={bundle.file_count:>4}/{MAX_IMPORT_FILES}  {bundle.status}"
            )
    offenders = over_limit(bundles)
    if args.check and offenders:
        for bundle in offenders:
            print(f"ERROR: bundle exceeds the Manus import limit: {bundle}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
