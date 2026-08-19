#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

MATT_REPO="https://github.com/mattpocock/skills.git"
AWS_REPO="https://github.com/awslabs/agent-plugins.git"
SUPERPOWERS_REPO="https://github.com/obra/superpowers.git"

mkdir -p "$ROOT_DIR/skills" "$ROOT_DIR/metadata"

clone_source() {
  local url="$1"
  local name="$2"
  git clone --depth 1 --quiet "$url" "$WORK_DIR/$name"
}

reset_namespace() {
  local namespace="$1"
  rm -rf "$ROOT_DIR/skills/$namespace"
  mkdir -p "$ROOT_DIR/skills/$namespace"
}

copy_skill_dir() {
  local source_dir="$1"
  local namespace="$2"
  local skill_name
  skill_name="$(basename "$source_dir")"
  local target_dir="$ROOT_DIR/skills/$namespace/$skill_name"
  mkdir -p "$target_dir"
  cp -a "$source_dir/." "$target_dir/"
}

copy_matt_skills() {
  local source_root="$WORK_DIR/matt/skills"
  reset_namespace "mattpocock-skills"
  while IFS= read -r skill_dir; do
    copy_skill_dir "$skill_dir" "mattpocock-skills"
  done < <(find "$source_root" -mindepth 3 -maxdepth 3 -type f -name SKILL.md -printf '%h\n' | sort)
}

copy_aws_skills() {
  local source_root="$WORK_DIR/aws/plugins"
  reset_namespace "aws"
  while IFS= read -r skill_file; do
    copy_skill_dir "$(dirname "$skill_file")" "aws"
  done < <(find "$source_root" -type f -name SKILL.md -print | sort)
}

copy_superpowers_skills() {
  local source_root="$WORK_DIR/superpowers/skills"
  reset_namespace "superpowers"
  while IFS= read -r skill_file; do
    copy_skill_dir "$(dirname "$skill_file")" "superpowers"
  done < <(find "$source_root" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print | sort)
}

write_import_metadata() {
  local metadata_file="$ROOT_DIR/metadata/skill-imports.tsv"
  printf 'namespace\tskill_name\tgithub_skill_url\tupstream_repository\n' > "$metadata_file"

  while IFS= read -r skill_dir; do
    local relative_path="${skill_dir#"$WORK_DIR/matt/"}"
    local skill_name="$(basename "$skill_dir")"
    printf 'mattpocock-skills\t%s\thttps://github.com/mattpocock/skills/tree/main/%s\thttps://github.com/mattpocock/skills\n' \
      "$skill_name" "$relative_path" >> "$metadata_file"
  done < <(find "$WORK_DIR/matt/skills" -mindepth 3 -maxdepth 3 -type f -name SKILL.md -printf '%h\n' | sort)

  while IFS= read -r skill_file; do
    local relative_path="${skill_file#"$WORK_DIR/aws/"}"
    local skill_name="$(basename "$(dirname "$skill_file")")"
    local skill_path="${relative_path%/SKILL.md}"
    printf 'aws\t%s\thttps://github.com/awslabs/agent-plugins/tree/main/%s\thttps://github.com/awslabs/agent-plugins\n' \
      "$skill_name" "$skill_path" >> "$metadata_file"
  done < <(find "$WORK_DIR/aws/plugins" -type f -name SKILL.md -print | sort)

  while IFS= read -r skill_file; do
    local relative_path="${skill_file#"$WORK_DIR/superpowers/"}"
    local skill_name="$(basename "$(dirname "$skill_file")")"
    local skill_path="${relative_path%/SKILL.md}"
    printf 'superpowers\t%s\thttps://github.com/obra/superpowers/tree/main/%s\thttps://github.com/obra/superpowers\n' \
      "$skill_name" "$skill_path" >> "$metadata_file"
  done < <(find "$WORK_DIR/superpowers/skills" -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print | sort)
}

clone_source "$MATT_REPO" matt
clone_source "$AWS_REPO" aws
clone_source "$SUPERPOWERS_REPO" superpowers

copy_matt_skills
copy_aws_skills
copy_superpowers_skills

updated_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$ROOT_DIR/metadata/source-commits.json" <<EOF
{
  "updated_at": "$updated_at",
  "sources": {
    "mattpocock/skills": {
      "repository": "$MATT_REPO",
      "commit": "$(git -C "$WORK_DIR/matt" rev-parse HEAD)"
    },
    "awslabs/agent-plugins": {
      "repository": "$AWS_REPO",
      "commit": "$(git -C "$WORK_DIR/aws" rev-parse HEAD)"
    },
    "obra/superpowers": {
      "repository": "$SUPERPOWERS_REPO",
      "commit": "$(git -C "$WORK_DIR/superpowers" rev-parse HEAD)"
    }
  }
}
EOF

write_import_metadata

printf 'Synced skills: %s\n' "$(find "$ROOT_DIR/skills" -type f -name SKILL.md | wc -l | tr -d ' ')"
printf 'Source metadata: %s\n' "$ROOT_DIR/metadata/source-commits.json"
printf 'Import metadata: %s\n' "$ROOT_DIR/metadata/skill-imports.tsv"
