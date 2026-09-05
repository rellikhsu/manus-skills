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

## Manus import URLs

For a whole collection, use the **`dist` branch** URLs in
[`metadata/manus-imports.tsv`](metadata/manus-imports.tsv). For example:

- [harness-engineering collection](https://github.com/rellikhsu/manus-skills/tree/dist/skills/harness-engineering)
- [Matt Pocock collection](https://github.com/rellikhsu/manus-skills/tree/dist/skills/mattpocock-skills)
- [Superpowers collection](https://github.com/rellikhsu/manus-skills/tree/dist/skills/superpowers)

Each collection has one top-level `SKILL.md` and child skill directories. To
import just one child instead, use its directory on `dist`, such as
[harness-engineering:which-loop](https://github.com/rellikhsu/manus-skills/tree/dist/skills/harness-engineering/which-loop).
`metadata/skill-imports.tsv` lists individual provenance URLs; it is not the
collection import list.

`main` holds the copied upstream skills and generated collection entries.
`scripts/transform-for-manus.py` prepares `dist` by prefixing child frontmatter
names, leaving their instructions and collection root names intact. Update
upstream child instructions in the upstream repository. Update collection entry
templates in `scripts/sync-skills.sh` (`write_bundle_skills`); changing only a
generated `SKILL.md` will be overwritten by the next sync. The harness collection
retains navigation to matching children; it does not impose an additional
mandatory `which-loop` step on every task.

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

These tests exercise the real transformer and validator in disposable directories:
child name prefixes, unchanged instruction bodies and collection roots,
idempotence, and rejection of missing or incorrect namespaces. They do not claim
to validate Manus's live skill-selection behavior.

## License

Each upstream skill remains subject to its upstream repository's license and attribution requirements. Refer to the upstream repositories and any license files copied into the skill directories before redistributing or modifying the content.
