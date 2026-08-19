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

write_bundle_skills() {
  cat > "$ROOT_DIR/skills/mattpocock-skills/SKILL.md" <<'EOF'
---
name: mattpocock-skills
description: Engineering and productivity workflows from Matt Pocock's public skills repository. Use when the user asks to implement, test, review, prototype, research, specify, triage, teach, hand off, or improve software work and agent workflows.
---

# Matt Pocock Skills Collection

Use this as a navigation skill for the bundled Matt Pocock workflows. Read the matching child `SKILL.md` before executing the requested workflow.

Engineering workflows are under `engineering/`; productivity workflows are under `productivity/`. Prefer the narrowest matching child skill. Do not assume this collection replaces project-specific instructions, safety requirements, or the user's explicit request.
EOF

  cat > "$ROOT_DIR/skills/aws/SKILL.md" <<'EOF'
---
name: aws-skills
description: AWS architecture, serverless, database, deployment, modernization, Amazon Location, SageMaker, and API implementation workflows from the AWS Labs agent plugins repository. Use for AWS infrastructure, Lambda, API Gateway, Step Functions, DSQL, Amplify, deployment, architecture diagrams, SageMaker, or AWS modernization tasks.
---

# AWS Agent Plugins Collection

Use this as a navigation skill for the bundled AWS workflows. Read the matching child `SKILL.md` before executing the requested AWS task.

The collection is grouped by upstream plugin under the child directories. Use the narrowest matching skill and verify current AWS documentation for version-sensitive behavior. Do not infer credentials or perform destructive AWS operations without the user's explicit authorization.
EOF

  cat > "$ROOT_DIR/skills/superpowers/SKILL.md" <<'EOF'
---
name: superpowers
description: A disciplined software-development workflow collection from obra/superpowers. Use before creative coding work, requirements analysis, implementation plans, test-driven development, debugging, code review, Git worktrees, or completion verification.
---

# Superpowers Workflow Collection

Use this as a navigation skill for the bundled Superpowers workflows. Read the matching child `SKILL.md` before executing the requested workflow.

Follow the relevant workflow in sequence. Preserve the user's explicit requirements, keep changes focused, test before claiming completion, and verify results before delivery.
EOF
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

write_manus_bundle_metadata() {
  local metadata_file="$ROOT_DIR/metadata/manus-imports.tsv"
  printf 'bundle_name\tmanus_github_import_url\tupstream_repository\n' > "$metadata_file"
  printf 'mattpocock-skills\thttps://github.com/rellikhsu/manus-skills/tree/main/skills/mattpocock-skills\thttps://github.com/mattpocock/skills\n' >> "$metadata_file"
  printf 'aws-skills\thttps://github.com/rellikhsu/manus-skills/tree/main/skills/aws\thttps://github.com/awslabs/agent-plugins\n' >> "$metadata_file"
  printf 'superpowers\thttps://github.com/rellikhsu/manus-skills/tree/main/skills/superpowers\thttps://github.com/obra/superpowers\n' >> "$metadata_file"
}

clone_source "$MATT_REPO" matt
clone_source "$AWS_REPO" aws
clone_source "$SUPERPOWERS_REPO" superpowers

copy_matt_skills
copy_aws_skills
copy_superpowers_skills
write_bundle_skills

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
write_manus_bundle_metadata

printf 'Synced skills: %s\n' "$(find "$ROOT_DIR/skills" -type f -name SKILL.md | wc -l | tr -d ' ')"
printf 'Source metadata: %s\n' "$ROOT_DIR/metadata/source-commits.json"
printf 'Import metadata: %s\n' "$ROOT_DIR/metadata/skill-imports.tsv"
