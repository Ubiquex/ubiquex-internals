# ubiquex-internals

The architecture and design site. Explains why `ubx` is built the way
it is, for a developer joining the project, distinct from
[ubiquex-docs](https://github.com/Ubiquex/ubiquex-docs), which is
user-facing content for someone building infrastructure with `ubx`, not
someone reading its source.

## Where this sits

Documents [ubiquex](https://github.com/Ubiquex/ubiquex) (the real
source of truth: `docs/architecture.md`, `docs/schema.md`,
`docs/plan.md` stay in that repo, next to the code; this site links
out to them rather than copying) and
[ubx-provider-dynamic](https://github.com/Ubiquex/ubx-provider-dynamic).
A `sync-drift-watch` mechanism (below) tracks both as real source
files this site's own content must stay honest about. Nothing depends
on this repo; it is read, never generated from.

## What it contains

- `overview.mdx`, `architecture.mdx`: the system model, the trust chain
- `schema-constitution.mdx`: the proposal and IR schema, hashing rules
- `repository-map.mdx`: what every repo in the org is and why it exists
- `provider-system.mdx`: hand-written vs. dynamic providers
- `sdk-and-codegen.mdx`: the multi-language SDK monorepo, blueprints
- `docs-pipeline.mdx`: the artifact model, golden pages, the coverage check
- `workflows.mdx`: real, sequenced operational flows across repos
- `decisions.mdx`: design decisions that live in Linear history, not
  any repo, and can't be reconstructed from code
- `conventions.mdx`: session verification discipline (merged flags
  lying, publish exit statuses lying, and the other real traps found
  this project's own way)
- `concepts/`: one page per core mechanism (ledger, resolver, executor,
  IR, proposal, drift, staleness, cross-stack references, blueprints)
- `sync-state.json`, `scripts/check_drift.py`: the drift-detection
  mechanism, see "How it's maintained" below

## How to use it

```
npm install -g mint
mint dev       # local preview
mint validate  # confirm the site builds
```

## How it's maintained

A narrative distillation of `ubiquex`'s own `docs/*.md`, never a copy,
those files are canonical for exact implementation detail; this site
explains them in prose for a person reading it for the first time.
`sync-state.json` records the `ubiquex` commit SHA each tracked source
file was last reviewed against; `.github/workflows/sync-drift-watch.yml`
runs daily, clones the real `ubiquex` repo, and opens or updates one
labeled tracking issue the moment a tracked file gets new commits since
its recorded SHA. It is a backstop for an already-tracked file drifting
silently, not a substitute for adding a new page when a genuinely new
mechanism ships (`ubiquex`'s own CLAUDE.md rule 10 governs when that's
required).

## Links

- Docs: https://docs.ubiquex.io
- User-facing docs corpus: https://github.com/Ubiquex/ubiquex-docs
- Linear board: https://linear.app/ubiquex
