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

The mirrored content comes from public upstream repositories and is kept private for the user's Manus synchronization workflow. Do not commit credentials, tokens, private project files, or unrelated personal data to this repository.

## Manus import URL

Manus currently imports a single skill when the supplied GitHub path resolves to a directory containing `SKILL.md`. The generated `metadata/skill-imports.tsv` file contains the upstream skill URL for each item. The mirror URL for a skill follows this format:

```text
https://github.com/rellikhsu/manus-skills/tree/main/skills/<namespace>/<skill-name>
```

For example:

```text
https://github.com/rellikhsu/manus-skills/tree/main/skills/mattpocock-skills/tdd
https://github.com/rellikhsu/manus-skills/tree/main/skills/aws/dsql
https://github.com/rellikhsu/manus-skills/tree/main/skills/superpowers/brainstorming
https://github.com/rellikhsu/manus-skills/tree/main/skills/harness-engineering/which-loop
https://github.com/rellikhsu/manus-skills/tree/dist/skills/perplexity/company-comps
```

## Updates

The scheduled GitHub Actions workflow runs weekly and fetches the latest default branch of each upstream repository. It replaces only the generated upstream namespaces, preserves the manually imported `perplexity` namespace, records the exact upstream source commits in `metadata/source-commits.json`, and creates a commit only when content changes.

The Manus scheduled task is separate from this repository workflow. It should inspect the mirror commit and import or update the corresponding Manus personal skills. A successful GitHub Actions run alone does not mean that the Manus personal Skills library has been updated.

## License

Each upstream skill remains subject to its upstream repository's license and attribution requirements. Refer to the upstream repositories and any license files copied into the skill directories before redistributing or modifying the content.
