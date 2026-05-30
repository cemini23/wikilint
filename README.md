# wikilint

[![CI](https://github.com/cemini23/wikilint/actions/workflows/ci.yml/badge.svg)](https://github.com/cemini23/wikilint/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Lint **agent-maintained markdown wikis** — orphans, bidirectional `related:` gaps, dangling links, missing `@path` mentions, frontmatter quality, stale `[NEEDS VERIFICATION]` tags.

Stdlib-only. No PyYAML dependency. Designed for CI on LLM-curated knowledge bases.

Companion tools: [vet](https://github.com/cemini23/vet) (skills/briefs) · [phase0](https://github.com/cemini23/phase0) (third-party repos)

## Install

```bash
pip install git+https://github.com/cemini23/wikilint.git
pip install -e .   # from clone
```

## Usage

```bash
wikilint wiki/
wikilint wiki/ --strict
wikilint wiki/ --json --verify-age-days 14
```

Environment: `WIKILINT_WIKI_DIR` defaults the wiki path to `./wiki`.

## Checks

| Category | Severity | What it catches |
|----------|----------|-----------------|
| `orphan` | warn | Pages with zero inbound `related:` edges |
| `dangling_link` | error | `related:` targets that do not exist |
| `bidirectional_gap` | warn | A→B without B→A (hub pages exempt via `hub: true`) |
| `missing_mention` | error | `@path/foo.md` in body with no file |
| `frontmatter` | error/warn | Missing YAML block, `type`, or `maturity` |
| `stale_verification` | warn | Old `[NEEDS VERIFICATION YYYY-MM-DD]` tags |

## GitHub Action

```yaml
- uses: actions/checkout@v4
- uses: cemini23/wikilint@v0.1.0
  with:
    wiki-dir: wiki
    strict: "true"
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | PASS |
| 1 | WARN |
| 2 | FAIL (errors) |
| 3 | ERROR (bad path) |

## Related

- Methodology newsletter: [Outlier Weekly](https://outlierweekly.substack.com)
- Agent meta-wiki: [cemini-claude-code-CCC](https://github.com/cemini23/cemini-claude-code-CCC)
- Toolkit: [vet](https://github.com/cemini23/vet) · [phase0](https://github.com/cemini23/phase0) · [agent-toolkit-demo](https://github.com/cemini23/agent-toolkit-demo) · [ara-schema](https://github.com/cemini23/ara-schema)

## License

MIT
