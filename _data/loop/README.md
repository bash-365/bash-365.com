# `_data/loop/` — the content loop's data

The content loop is a governed, scheduled AI routine that turns the practice's own recent work into one new article every other day and one improvement to an existing page on the days between. The repository is the loop's CMS: everything it needs to decide is a file here, everything it produces goes through a pull request a human merges. The operator's guide is [`docs/content-loop.md`](../../docs/content-loop.md).

| File | Purpose | Written by |
|---|---|---|
| `config.yml` | Cadence, backpressure cap, section rotation ring, signal window, improve rules, area → related-page map, the editorial-directive label, cap and kinds | humans |
| `sources.yml` | The repositories the miner may read (home via git, sisters via the GitHub API) with weights | humans |
| `runs/*.yml` | The ledger: one record per run — mode, section, path, the story ids it spent, the PR, the directive issue it served (when the plan carried one) | `scripts/loop/ledger.py`, in the loop's own PR |
| `sessions.jsonl` | Committed AI-session traces: session id, intent, files touched, commits — scrubbed metadata, never transcripts | `scripts/loop/trace.py --sync` (a human commits it) |

Jekyll loads `config.yml`, `sources.yml`, and `runs/*.yml` as `site.data.loop`, so a page can render the loop's state; `sessions.jsonl` and the READMEs are ignored by the data loader.
