#!/usr/bin/env python3
import os
import re
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT_DIR / "skills"
def transform_skill_file(file_path: Path, namespace: str):
    content = file_path.read_text(encoding="utf-8")
    # Frontmatter regex
    fm_pattern = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
    match = fm_pattern.search(content)
    if not match:
        return
    frontmatter = match.group(1)
    name_pattern = re.compile(r"^name:\s*(.+)$", re.MULTILINE)
    name_match = name_pattern.search(frontmatter)
    if not name_match:
        return
    raw_name = name_match.group(1).strip().strip(chr(39) + chr(34))
    prefix = f"{namespace}:"
    if not raw_name.startswith(prefix):
        new_name = f"{prefix}{raw_name}"
        new_frontmatter = name_pattern.sub(f'name: "{new_name}"', frontmatter, count=1)
        new_content = content[:match.start(1)] + new_frontmatter + content[match.end(1):]
        file_path.write_text(new_content, encoding="utf-8")
        print(f"Prefixed: [{file_path.relative_to(ROOT_DIR)}] -> '{new_name}'")
def main():
    if not SKILLS_DIR.exists():
        print("Skills directory not found.")
        return
    for namespace_dir in sorted(SKILLS_DIR.iterdir()):
        if not namespace_dir.is_dir():
            continue
        namespace = namespace_dir.name
        # Only transform child skills (not namespace bundle root)
        for skill_file in sorted(namespace_dir.rglob("SKILL.md")):
            if skill_file.parent != namespace_dir:
                transform_skill_file(skill_file, namespace)
if __name__ == "__main__":
    main()
