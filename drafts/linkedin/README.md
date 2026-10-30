# `drafts/linkedin/` — the approval queue

A staging area, not an outbox. Each `*.md` at the top level of this folder is one proposed LinkedIn post for the BASH company page, waiting on a person.

The gate: a draft is written here at `status: pending` — by `/linkedin-draft`, by `scripts/linkedin.sh draft`, or by hand — and lands in a pull request. A person edits it and **merges** it; the merge is the approval. `.github/workflows/linkedin-publish.yml` then runs zer0-CMS's distribution lane live: it posts the draft, records it in `.github/linkedin-log.json`, and sets the draft to `status: published` with its `linkedin_urn`.

What keeps a stray file from publishing:

- only `pending` and `approved` drafts publish (`zer0.json` → `distribution.linkedin.acceptStatuses`), and `pending` only as a merged draft in the workflow on `main` — anywhere else a draft must be `approved`; a `published` one never publishes again;
- an attempt LinkedIn did not confirm is marked `unconfirmed` in the ledger, and no run sends that draft again until a person checks LinkedIn (`scripts/linkedin.sh record DRAFT URN`);
- only top-level files are read, so `examples/` never publishes, and a file with no front matter (this README) is not a draft;
- a page already in the ledger is not posted twice;
- an error from the brand guard (a banned phrase, commentary over LinkedIn's limit) blocks the post.

Preview the exact request, the guard's findings and every gate, with no network call:

```bash
scripts/linkedin.sh preview
```

`scripts/linkedin.sh` runs zer0-CMS's `manage.py linkedin` from a checkout beside this repository; its header says how to point it elsewhere. Drafting rules: `.claude/skills/linkedin-share/SKILL.md`. The lane, its gates and its settings: zer0-CMS `docs/DISTRIBUTION.md`.
