# The content loop — the practice's work, turned into content on a cadence

> One new article every other day, drawn from what the practice actually did — commits, pull requests, AI sessions, tools built. One improvement to an existing page on the days between, driven by the same work. Scripts decide *when* and offer *what*; the model writes; a human merges.

This is the operator's guide. It is the bash-365.com counterpart of the autopilot that runs [lifehacker.dev](https://github.com/bamr87/lifehacker.dev) (`AUTOPILOT.md` there), rebuilt on this repository's own conventions: Python scripts with self-tests, the editorial gate, the brand and content-style instruction files, and the pull-request-only rule every routine here already follows. `docs/` is excluded from the Jekyll build, so this page is internal.

## TL;DR

A daily workflow (`.github/workflows/content-loop.yml`) runs a deterministic planner. The planner reads the loop's ledger and decides one of three things: a **new** article is due, an **improvement** is due, or the loop should **idle** — and says why. When there is work to do it hands the writer (a Claude Code agent following a written skill) the best unspent *stories* from the practice's recent activity and the most-overdue section, or the pages the same activity has made stale. The writer produces one piece, gates it with the repo's scripts, records the run in the ledger, and opens one pull request. You review and merge. GitHub Pages deploys `main`.

Nothing runs until you set one repository variable. Nothing merges without you.

## The promise

| | |
|---|---|
| **Cadence** | A new article every 2 days; an improvement on the days between. Both are ledger-driven, so a missed day is caught up, never doubled. |
| **Where ideas come from** | The practice's own work: this repository's git history (with the `Co-Authored-By: Claude` and `Claude-Session:` trailers that mark AI-assisted work), CHANGELOG lines, committed AI-session traces, and — read-only, best-effort — the founder's sister repositories. |
| **Rotation** | New articles rotate through the four post sections (`tech`, `corp`, `erp`, `muses`), most-overdue first, each in its own voice from `_data/taxonomy.yml`. |
| **Voice and audience** | BASH's: enterprise-grade IT for small business, written for owners, controllers, and in-house IT leads. The practice's work is the worked example; the pattern is the deliverable. |
| **Output** | One pull request per run, labeled by title `content(<section>): <new\|improve> — <subject>`, on a `loop/<run-id>` branch, with a run record in `_data/loop/runs/`. |
| **Who approves** | A human. The loop never pushes to `main`, never merges, never enables itself. |

## The flywheel

```
  the practice does work ──▶ commits · PRs · AI sessions · tools   (the signal)
                                            │
                    scripts/loop/signals.py │ mine + group + score + mark spent
                                            ▼
                    scripts/loop/plan.py  ── decide: new / improve / idle ──▶ .loop/plan.md + digest.md
                                            │
                    the loop-writer agent   │ read the work for real · translate for the reader · gate
                    (content-loop skill)    ▼
                    ONE pull request  +  _data/loop/runs/<run>.yml   (the ledger remembers)
                                            │
                                   HUMAN MERGE GATE
                                            │
                         GitHub Pages deploys main ──▶ the site ──▶ more work ──▶ …
```

The ledger closes the loop: the next planner run reads it to know when the last new piece and the last improvement happened (cadence), which section has waited longest (rotation), which pages were improved recently (cooldown), and which stories are already spent (never the same commit twice).

## The data that drives it

All of it is committed data, so the repository is the loop's CMS.

| File | Purpose | Written by |
|---|---|---|
| `_data/loop/config.yml` | Cadence (new every N days, improve every M), the open-PR cap, the section ring, the signal window, the improve rules, and the map from an area of work to the pages it makes stale | humans |
| `_data/loop/sources.yml` | Where the miner may look: the home repository via git, sister repositories via the GitHub API, each with a weight | humans |
| `_data/loop/runs/*.yml` | The ledger — one record per run: date, mode, section, path, title, the story ids it spent, the PR | `scripts/loop/ledger.py`, in the loop's own PR |
| `_data/loop/sessions.jsonl` | The committed AI-session trace: session id, when it ended, intent (the first prompt, one line, scrubbed), files touched, commits — never a transcript | `scripts/loop/trace.py --sync`, committed by a human |
| `.claude/loop/sessions.jsonl` | The local, gitignored queue the `SessionEnd` hook appends to | `.claude/hooks/session-trace.sh` |
| `.loop/` | The planner's per-run working directory (`plan.json`, `plan.md`, `signals.json`, `digest.md`) — gitignored; in CI it travels as a workflow artifact | `scripts/loop/plan.py` |

## The scripts, and where judgment stays

Everything load-bearing is a script (`scripts/loop/`, standard library only, each with `--self-test`):

| Script | Job |
|---|---|
| `signals.py` | Mine the activity into scored stories and render the digest. `--no-remote` skips the sister repos; `--out DIR` writes `signals.json` + `digest.md`. |
| `plan.py` | The pure decision: mode, reason, section ring, stories offered, improve candidates. Writes `plan.json` + `plan.md` and, in CI, the job outputs. `--mode` and `--section` are operator overrides. |
| `ledger.py` | `--record` a run, `--set-pr` the URL after the push, `--list`, `--last new\|improve`. |
| `trace.py` | The session trace: `append` (the hook), `--list`, `--sync` (fold the local queue into the committed trace), `--add` (a manual entry). |
| `_lib.py` | Shared: a strict YAML-subset reader/writer, the git wrapper, the credential scrubber, the house slug rule. |

The model does only the judgment: which of the offered stories yields an honest lesson for the section, what the angle is, and the writing itself. That split is why the loop can be dry-run end to end without a token, why every decision in the run summary is explainable, and why the worst a model mistake can do is open a pull request.

## Cadence and rotation

The planner alternates: with `new_every_days: 2` and `improve_every_days: 2`, a daily schedule produces new, improve, new, improve. It is self-correcting rather than calendar-bound — each mode is due when enough days have passed since the *ledger's* last record of it, and when both are due the more overdue one runs first. A failed run does not shift the pattern permanently; the next day catches up.

Backpressure comes first: with `caps.max_open_prs` loop PRs still awaiting review, the planner idles and says so. Throughput is clamped to review speed by design — adding compute never floods the human.

The section ring (`sections.ring`) orders the four post sections by how long each has gone without a new piece, using both the ledger and the newest dated post on disk. The writer takes the first section it can serve honestly from the offered stories and records the section it actually served, so the rotation follows reality rather than intent.

## Where the ideas come from

The miner groups the home repository's commits into stories: by AI session when a commit carries a `Claude-Session:` trailer, else by pull request when the subject ends in `(#N)`, else by day. Each story carries its commits, files, insertions and deletions, the areas of the repository it touched (posts, toolkit, services, `ci`, `claude`, `scripts`, `config`, `theme`, …), the pull request, the CHANGELOG lines that mention it, the session's intent when a trace exists, and an ordered list of *suggested sections* derived from the areas and a few keyword pulls (ledger, close, and invoice pull toward `erp`; consent, vendor, and cost toward `corp`).

Scores are explainable and their weights live in `config.yml`: recency within the window, size on a log scale, a bonus for AI-assisted work (the loop is meant to trace those sessions), a discount for commits that only add articles (an article about writing an article is a weak seed) and for automated runs, and the source's weight. A story any run has already spent scores zero. When the default window holds nothing unspent, the planner widens it once to `max_window_days`; when even that is empty, it idles honestly — there is nothing to write about until the next work lands.

Sister repositories (`sources.yml`, `via: github`) are read through `gh api` when a token is available: merged pull requests and recent commits become stories tagged with their repo, so the writer can say where the work happened. Missing `gh`, a missing token, or an API refusal is a note in the digest, never a failure.

## The session trace

AI sessions are the loop's most interesting signal — a session is a story with an intent, a set of files, and the commits it produced. Two of those are already in git: the `Co-Authored-By: Claude …` trailer marks AI-assisted commits, and the `Claude-Session:` trailer groups them by session. The third, the intent, is not, so the repo's `SessionEnd` hook (`.claude/settings.json` → `.claude/hooks/session-trace.sh` → `scripts/loop/trace.py append`) records it.

The hook does no model work, swallows every error, and always exits 0. It writes one line of **derived metadata** — session id, end time, repo, branch, the first user prompt as a one-line scrubbed intent, files touched, commits carrying the session's trailer, a turn count — to the local, gitignored queue. Transcripts are never read for anything but that first prompt, and nothing that looks like a credential survives `scrub()`.

Folding the queue into the committed trace is a deliberate, human step:

```bash
python3 scripts/loop/trace.py --list    # what's queued locally, what's already committed
python3 scripts/loop/trace.py --sync    # fold into _data/loop/sessions.jsonl — review the diff, then commit
```

You see exactly what is about to become public before it does. A session with no honest business lesson can simply stay unsynced.

## A run, step by step

The writer follows `.claude/skills/content-loop/SKILL.md`; the charter is `.claude/agents/loop-writer.md`. In order: read the plan and the digest; read the chosen story's commits and diffs for real; translate it for the section's reader (outcome first, mechanism second, next step last, the practice's work as the worked example, the pull request linked as the primary source); draft the article per `posts.instructions.md` and the section voice — or, in improve mode, add the section the recent work justifies to the first candidate page and bump `lastmod`; gate it with `content_lint.py`, `doctrine_check.py`, and `unwrap-prose.py --check`; record the run with `ledger.py --record` in the same commit as the content; push `loop/<run-id>` and open the pull request; link it back with `ledger.py --set-pr`; write `loop-result.json`; stop.

The pull request body states the mode and the planner's reason, names the story and the section served, lists what changed, and carries the reviewer's checklist. For a new post the checklist includes the preview image: when the `OPENAI_API_KEY` secret exists the workflow generates it on the PR branch with the existing generator (`docs/preview-images.md`); otherwise the reviewer does, per the house rule that a post never ships without its banner.

## Guardrails (do not remove)

- **No push to `main`. No self-merge, no self-approval.** The loop works on `loop/*` branches and opens pull requests; a human merges.
- **The variable is the switch.** The schedule idles until `CONTENT_LOOP_ENABLED` is `true`; the bot token cannot set variables, so the loop cannot enable itself. A manual run works without it — a human pressed the button.
- **Backpressure.** `caps.max_open_prs` is honored on every run, forced modes included.
- **Never invent.** No metrics, clients, certifications, or outcomes that are not in the diff or the page. No secrets, internal hostnames, or unpublished drafts in an article — the repository and the article are public.
- **Deterministic first.** Mode, cadence, rotation, scoring, and spent-tracking are scripts. The model chooses among what the scripts offer; it never re-decides them.
- **Honest idling.** No unspent activity, a full review queue, or no candidate page all end as an idle run with a reason in the summary, never as filler.
- **One byline.** `Amr Abdel-Motaleb` — agents draft, the human approves and owns it.

Loosening any of these is a deliberate change: say so in `CHANGELOG.md` with a date.

## Activation

1. Add the Anthropic credential the other routines already use, under Settings → Secrets and variables → Actions: `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`, preferred) or `ANTHROPIC_API_KEY`. Without either, the loop plans but never writes.
2. Set the repository **variable** `CONTENT_LOOP_ENABLED` to `true`. That is the single ON switch.
3. Optional: `CONTENT_LOOP_GITHUB_TOKEN`, a fine-grained PAT with Contents and Pull requests read/write, so the loop's PRs trigger the normal build checks. The workflow probes it against the API first and degrades to `github.token` with a warning when it has expired, because `secrets.X || github.token` tests presence, not validity, and an expired token wins that expression.
4. Optional: `OPENAI_API_KEY` to have new posts' preview images generated on the PR branch; `CONTENT_LOOP_MODEL` (a variable) to pin the writer's model.

When the loop is on, the weekly `content-gardener` and `content-review` schedules stand down — their gates check the same variable — so topics are not doubled. Both still run on manual dispatch. The preacher is unaffected; it audits the loop's output like everything else.

## Running it by hand

```bash
python3 scripts/loop/plan.py --out .loop --no-remote     # decide today, no network; read .loop/plan.md
python3 scripts/loop/signals.py --no-remote --window 60  # just the digest, wider window
python3 scripts/loop/ledger.py --list                    # what the loop has done
```

In Claude Code, `/loop-run` runs one full cycle (`/loop-run improve`, `/loop-run new erp` to steer). In Actions, **Run workflow** with `dry_run` checked plans and publishes the digest to the run summary without writing anything; `mode` and `section` steer a live run.

## Extending

- **Change the cadence or the cap:** edit `_data/loop/config.yml`. Nothing in the scripts hard-codes a number.
- **Add a source repository:** a row in `_data/loop/sources.yml` with a weight. Public repositories need no extra token.
- **Teach the improve mode a new relationship:** add the area → pages entry under `improve.related_pages`; the planner boosts those pages whenever an unspent story hits that area.
- **Add an area or a section pull:** `AREA_RULES`, `SECTION_HINTS`, and `KEYWORD_HINTS` at the top of `scripts/loop/signals.py`, with a line in its self-test.
- **Change the writer's procedure:** the skill. Change its scope or hard rules: the agent charter. The workflow only points at them.

Every script has a `--self-test`; run them all before touching the planner or the miner:

```bash
for s in _lib ledger signals plan trace; do python3 scripts/loop/$s.py --self-test || exit 1; done
```

## Lineage and siblings

The design is lifted from lifehacker.dev's autopilot — the deterministic/judgment split, a committed ledger as memory, `*_ENABLED` variables as the only switches, one PR per run, a human as the only commit authority, and the two-store session-trace pattern of its retrospective hook — and rebuilt in this repo's idiom. It sits beside the existing routines: the **gardener** (gap-driven weekly drafts) and the **curator** (weekly expand-or-add review), both of which it supersedes on schedule while enabled, and the **preacher** (weekly doctrine enforcement), which holds the loop to the same standard as everything else. See `docs/automation.md` for the full workflow table.
