# Manus Skills Mirror

This repository is a private, generated mirror of skills from four upstream repositories plus a manually imported Perplexity Finance namespace. It is structured so that every skill directory contains its own `SKILL.md` and can be imported into Manus through a GitHub subdirectory URL.

## Upstream sources

| Namespace | Upstream repository | Mirror path |
| --- | --- | --- |
| `mattpocock-skills` | https://github.com/mattpocock/skills | `skills/mattpocock-skills/<skill-name>` |
| `aws` | https://github.com/awslabs/agent-plugins | `skills/aws/<skill-name>` |
| `superpowers` | https://github.com/obra/superpowers | `skills/superpowers/<skill-name>` |
| `harness-engineering` | https://github.com/rellikhsu/harness-engineering | `skills/harness-engineering/<skill-name>` |
| `perplexity` | User-provided Perplexity Finance export | `skills/perplexity/<skill-name>` |

The mirror is kept private for the user's Manus synchronization workflow. The private `harness-engineering` upstream is cloned using the GitHub Actions `GH_PAT` secret. Do not commit credentials, tokens, private project files, or unrelated personal data to this repository.

## The 100-file import limit

Manus imports **one GitHub subdirectory per skill bundle and refuses any tree
that holds more than 100 files**. This repository root (640 files) and the `aws`
namespace (378 files) can never be imported as a single URL, and neither could
`skills/mattpocock-skills` (110 files) before pruning. An import that is too big
fails with `此技能過大，無法匯入（限制 100 個檔案）`. Import one bundle at a time
using the URLs below; never import the repository root or `skills/`.

`scripts/transform-for-manus.py` turns the pristine mirror on `main` into an
import-ready tree on `dist` in four deterministic passes:

1. **prune** files no Manus runtime reads (`*/agents/openai.yaml` for other
   CLIs, plus junk files) and the directories left empty;
2. **prefix** every child frontmatter `name` with `<namespace>:`, leaving
   instruction bodies and collection roots untouched;
3. **split** any namespace still over the limit into thematic bundles declared in
   [`metadata/manus-bundles.tsv`](metadata/manus-bundles.tsv), each with its own
   generated navigation `SKILL.md`;
4. **publish** [`metadata/manus-imports.tsv`](metadata/manus-imports.tsv) and
   fail the run when a bundle exceeds the limit.

Splitting never renames a skill: children of `skills/aws/serverless/` still
resolve as `aws:api-gateway`, and relative links between sibling skills keep
working because a link only resolves inside the bundle that holds both skills.
[`scripts/bundle_layout.py`](scripts/bundle_layout.py) owns the layout, the limit,
and the manifest, so `main` and `dist` always describe the same bundles.

## Manus import URLs

| Bundle | Skills | Files | Import URL |
| --- | --- | --- | --- |
| `aws-ai-ml` | 11 | 76/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/aws/ai-ml> |
| `aws-database` | 1 | 74/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/aws/database> |
| `aws-hyperpod` | 8 | 39/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/aws/hyperpod> |
| `aws-modernization` | 4 | 72/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/aws/modernization> |
| `aws-serverless` | 7 | 79/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/aws/serverless> |
| `aws-tooling` | 3 | 43/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/aws/tooling> |
| `harness-engineering` | 11 | 12/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/harness-engineering> |
| `mattpocock-skills` | 39 | 72/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/mattpocock-skills> |
| `perplexity` | 21 | 46/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/perplexity> |
| `superpowers` | 15 | 81/100 | <https://github.com/rellikhsu/manus-skills/tree/dist/skills/superpowers> |

Each bundle has one top-level `SKILL.md` and child skill directories. To import
just one child instead, use its own directory on `dist`, such as
[harness-engineering:which-loop](https://github.com/rellikhsu/manus-skills/tree/dist/skills/harness-engineering/which-loop).
`metadata/skill-imports.tsv` lists individual provenance URLs; it is not the
collection import list.

`main` holds the copied upstream skills and generated collection entries. Update
upstream child instructions in the upstream repository. Update collection entry
templates in `scripts/sync-skills.sh` (`write_bundle_skills`) and bundle grouping
in `metadata/manus-bundles.tsv`; changing only a generated `SKILL.md` will be
overwritten by the next sync. The harness collection retains navigation to
matching children; it does not impose an additional mandatory `which-loop` step
on every task.

When upstream adds a skill to a split namespace, add it to the right row of
`metadata/manus-bundles.tsv`; the sync fails with the offending skill name if it
is missing, and fails again if a bundle crosses the limit.

## Updates

The GitHub Actions workflow is scheduled for **Monday 08:00 Asia/Taipei
(00:00 UTC)** and also supports manual execution. An upstream push does not
immediately trigger it. It fetches the latest default branch of each upstream
repository, not a release tag or plugin version. It replaces only the generated
upstream namespaces, preserves the manually imported `perplexity` namespace,
records exact source commits in `metadata/source-commits.json`, and then validates
and publishes the transformed `dist` branch. Treat `dist` as generated output:
the workflow rebuilds and force-pushes it.

For an immediate update after the intended upstream and converter changes have
both been pushed, run the existing workflow from GitHub Actions or:

```bash
gh workflow run sync-upstream-skills.yml --repo rellikhsu/manus-skills --ref main
```

Wait for that run to succeed, then read `metadata/source-commits.json` **on `dist`**
and confirm the intended upstream SHA before importing. A sync refreshes
`updated_at`, so a new mirror commit alone is not proof that every skill changed;
compare source SHAs and the relevant collection files.

The Manus scheduled task is separate from this repository workflow. It should inspect the mirror commit and import or update the corresponding Manus personal skills. A successful GitHub Actions run alone does not mean that the Manus personal Skills library has been updated.

Use Manus's supported collection update/import operation. If replacing the old
collection is required, replace only that collection and preserve unrelated
personal skills. Local filesystem copies are not proof of a library update.

## Local validation

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

These tests exercise the real transformer and validator in disposable
directories: child name prefixes, unchanged instruction bodies and collection
roots, idempotence, rejection of missing or incorrect namespaces, pruning,
namespace splitting, and the guard that fails when a bundle crosses the 100-file
import limit. They do not claim to validate Manus's live skill-selection
behavior.

Inspect or verify the import budget without transforming anything:

```bash
python3 scripts/bundle_layout.py            # per-bundle skill and file counts
python3 scripts/bundle_layout.py --check    # non-zero when a bundle is over 100
python3 scripts/transform-for-manus.py      # apply the dist layout in place
python3 scripts/validate-dist.py            # verify the transformed tree
```

## License

Each upstream skill remains subject to its upstream repository's license and attribution requirements. Refer to the upstream repositories and any license files copied into the skill directories before redistributing or modifying the content.
