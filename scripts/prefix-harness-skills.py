#!/usr/bin/env python3
"""Prefix harness-engineering skills with the namespace for Manus compatibility."""

import os
import re
from pathlib import Path

SKILLS_DIR = Path("/home/ubuntu/manus-skills/skills/harness-engineering")
NAMESPACE = "harness-engineering"

def process_skill(skill_dir: Path):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return

    content = skill_md.read_text()
    
    # 找到 frontmatter
    match = re.search(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        return
        
    frontmatter = match.group(1)
    body = content[match.end():]
    
    # 尋找 name 欄位
    name_match = re.search(r"^name:\s*(.*?)$", frontmatter, re.MULTILINE)
    if not name_match:
        return
        
    current_name = name_match.group(1).strip()
    
    # 去除引號
    if current_name.startswith('"') and current_name.endswith('"'):
        current_name = current_name[1:-1]
    elif current_name.startswith("'") and current_name.endswith("'"):
        current_name = current_name[1:-1]
        
    # 如果已經有 namespace 就跳過
    if current_name.startswith(f"{NAMESPACE}:"):
        return
        
    new_name = f"{NAMESPACE}:{current_name}"
    
    # 替換 frontmatter 中的 name
    new_frontmatter = re.sub(
        r"^name:\s*.*$", 
        f'name: "{new_name}"', 
        frontmatter, 
        count=1, 
        flags=re.MULTILINE
    )
    
    new_content = f"---\n{new_frontmatter}\n---\n{body}"
    skill_md.write_text(new_content)
    print(f"Updated {skill_md.relative_to(SKILLS_DIR.parent)}: {current_name} -> {new_name}")

def main():
    if not SKILLS_DIR.exists():
        print(f"Directory not found: {SKILLS_DIR}")
        return
        
    for item in SKILLS_DIR.iterdir():
        if item.is_dir():
            process_skill(item)

if __name__ == "__main__":
    main()
