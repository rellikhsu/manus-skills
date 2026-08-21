#!/usr/bin/env python3
import re
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", re.DOTALL)
NAME_RE = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
NAME_VALUE_RE = re.compile(r"[A-Za-z0-9_-]+:[A-Za-z0-9_-]+")


def validate_skill_file(skill_file: Path) -> None:
    relative = skill_file.relative_to(SKILLS_DIR)
    if len(relative.parts) < 3:
        return

    content = skill_file.read_text(encoding="utf-8")
    frontmatter_match = FRONTMATTER_RE.match(content)
    name_match = frontmatter_match and NAME_RE.search(frontmatter_match.group(1))
    raw_name = name_match.group(1).strip().strip("'\"") if name_match else ""
    namespace = relative.parts[0]

    if not NAME_VALUE_RE.fullmatch(raw_name) or not raw_name.startswith(f"{namespace}:"):
        raise SystemExit(f"ERROR: Invalid child skill name in {skill_file}: {raw_name!r}")


def main() -> None:
    skill_files = sorted(SKILLS_DIR.rglob("SKILL.md"))
    if not skill_files:
        raise SystemExit("ERROR: No SKILL.md files found.")
    for skill_file in skill_files:
        validate_skill_file(skill_file)
    print(f"Validated transformed child skills: {len(skill_files)} files")


if __name__ == "__main__":
    main()
