---
title: "Debugging a CI failure you cannot read"
description: "A failing GitHub Actions run in a repository the session had no API access to, diagnosed by inverting the step number in the URL and rebuilding the job locally"
date: 2026-09-07
categories: [it-journey]
tags: [github-actions, ci-cd, jekyll, html-proofer, debugging, forks, claude-code, ai-workflows, reproducibility, bash-365]
draft: true
---

## The ask

One link, one question: *what's wrong with this workflow?* The link pointed at a job in a GitHub Actions run, deep-linked to a specific step:

```
https://github.com/amr-bash/bash-365.com/actions/runs/34136278621/job/101787900076#step:8:1
```

The session had write access to `bamr87/bashconsultants` and no API access to `amr-bash/bash-365.com` at all. Every route to the log was closed: the Actions API returned 404 against the repo the session *could* see, and 403 from the egress proxy against the repo it could not. The one artifact that would normally answer the question in ten seconds — the log — was unreachable.

That turns out to be a solvable class of problem, and the method generalizes.

## What the URL still tells you

A run URL that nobody can open is not information-free. It carries four facts:

- **the owner and repo** — which workflow files are in play,
- **the run ID** — which, because GitHub's run IDs increase monotonically across the whole platform, is a usable clock,
- **the job ID** — one job, so one `jobs:` key,
- **the step index** — `#step:8:1` means step 8, line 1.

The step index is the sharp one, and it is sharper than it looks, because GitHub's step numbering is not the same as the list of steps you wrote in YAML. The runner injects its own:

1. `Set up job` is always step 1.
2. If the job declares `container:`, `Initialize containers` is step 2 and **everything you wrote shifts down by one**.
3. Your declared steps follow in order.
4. Post-steps (`Post Cache gems`, `Post Run actions/checkout`), `Stop containers` and `Complete job` are numbered from a *reserved block* at the end, not contiguously — a job with 6 declared steps can jump from step 8 straight to step 14.

So "step 8" is a coordinate you can invert. Enumerate every job in every workflow file, apply those rules, and ask which ones even *have* a step 8 that is a real named step rather than cleanup. Across two repositories and nineteen jobs, exactly two did:

| Workflow | Job | Step 8 |
|---|---|---|
| `build-validate.yml` | `build-pages` (container: `ruby:3.3`) | `Sanity-check output` |
| `site-health.yml` | `health` | `Link check built site (internal only)` |

Every other job's step 8 was `Post Checkout` or similar — a cleanup step that had succeeded. Two candidates from a blank wall.

The run ID narrowed the timing. Interpolating between two runs with known timestamps in the readable repository gave roughly 1,490 run IDs per second platform-wide, which placed the unreadable run at about 15:03 UTC — and, usefully, about 75 seconds *before* a scheduled sync job, ruling out the causal story that had looked most obvious.

## Rebuild the job, not the theory

Two candidates is not an answer. The way to get one without the log is to stop reasoning about the workflow and run it.

The target repository was public, so a shallow clone worked even though the API did not. Its `main` turned out to be stale by nearly two months — which mattered, because it meant the run could be building one of two very different trees. So both got built:

- the **merge tree** (what a pull request from the fork would compile), reconstructed with a local `git merge` of the fork's `main` into the stale `main`;
- the **stale tree** itself, checked out into a `git worktree`, with its own pinned theme and its own version of the workflow.

Then the job steps were executed verbatim — the same heredoc `Gemfile`, the same `bundle install`, the same `jekyll build`, the same sanity-check script, the same `htmlproofer` invocation with the same flags.

On the merge tree, both candidate step 8s passed. On the stale tree, with the stale repository's *own* `htmlproofer` flags:

```
HTML-Proofer found 379 failures!
```

That number was the confirmation. Not because 379 is large, but because `379` was already written down — in a comment in the *other* repository's copy of the same workflow, explaining a fix made two months earlier:

> those shapes were 368 of the 379 failures that kept this check red

A reproduction that lands on a number someone else recorded independently is no longer a hypothesis.

## The actual bug

The failure was never really in the workflow logic. It was **fork drift**.

The theme renders `/tags/#<slug>` and `/archives/#<slug>` links on every post, plus bare `#<slug>` anchors, but the site publishes no `/tags/` or `/archives/` index pages. Add relative repository-file links on the published agent-context pages, and href-less `<a>` tags from theme pagination:

| Shape | Failures |
|---|---|
| `/tags/#<slug>` | 226 |
| bare `#<slug>` | 134 |
| `/archives/#<slug>` | 6 |
| repo-file links (`./.claude/….md`) | 7 |
| href-less `<a>` | 3 |

The development fork had diagnosed and fixed exactly this — four extra `htmlproofer` flags and an `--ignore-files` pattern — and had been green ever since. The deployment repository never received the change, and had been failing nightly, alone, for two months. Running the fork's flags against the stale tree took it from 379 failures to zero, which is the proof that the fix is the fix and no code change is needed at all: the pending sync pull request already carries it.

## A red herring worth keeping

The first local build failed with:

```
Invalid US-ASCII character "\xE2" on line 3
```

which looks like a content bug and is not one. Ruby derives `Encoding.default_external` from the locale, and with `LANG` unset it lands on US-ASCII, at which point any non-ASCII byte in a `.scss` file is a syntax error. The official `ruby` Docker images set `ENV LANG C.UTF-8`, so CI never sees this; a bare sandbox does. Exporting `LANG=C.UTF-8` made it vanish.

The lesson is about reproductions generally: when you rebuild a CI job locally, the *environment* is part of the job. Container image defaults — locale, `HOME`, `TZ`, `PATH` — are silent inputs, and a difference in one of them produces a failure that belongs to your laptop and not to the bug you are chasing. Reproduce the container, not just the commands.

## What this says about forks

A fork used as a development repository with the "real" repository downstream is a common enough pattern, and it has a specific failure mode: **fixes flow toward the place where nobody is watching, slowest**. The fork gets the fix at the moment of the fix. The deployment repository gets it whenever someone merges the sync pull request. In between, the deployment repository runs stale automation against a tree that has moved on, and its scheduled workflows fail into a void.

Two cheap defenses:

- **Make the alert land somewhere a human is.** This repository had already learned half of it — the nightly check used to call `gh issue create` on a repository with Issues disabled, so it failed silently every night and told nobody. It now writes to the run summary instead. The other half is that the *upstream* copy still has the old issue-creating version, which is exactly the copy currently failing.
- **Treat "the fork is ahead" as a monitored condition**, not a background fact. A scheduled sync that opens a pull request is good; a sync that nobody merges is a queue, and queues need depth alarms.

## Working this way with an AI

A few things made the difference here, and none of them were the model knowing anything special about Jekyll.

**Say what you cannot do, early.** The first three tool calls all failed — 404, 403, permission denied. Naming the wall explicitly ("the log is unreachable; what else encodes the answer?") is what redirected the work from retrying access to inverting the URL. An agent that treats a denial as a dead end stops; one that treats it as a constraint re-plans.

**Prefer a reproduction to an explanation.** It is very easy to produce a confident, plausible, wrong story about a CI failure — and an AI is *especially* good at producing one, because plausible prose is what it optimizes. The discipline that saves you is refusing to answer until something has actually been executed. Here that meant two full site builds and four `htmlproofer` runs before a single claim was made. The first candidate failure — the one that looked most likely on the reasoning alone — turned out to pass.

**Look for a number to collide with.** The strongest signal in this whole session was `379` appearing in two independent places: a live reproduction and a comment written two months earlier by someone else. Whenever you can arrange for your conclusion to be checkable against a fact you did not generate, do it. It converts "this is my best reading" into "this is the answer."

**Let the repository's own artifacts do the work.** The comment in the fixed workflow file explained the root cause, the count, and the reasoning. Repositories that write down *why* — in workflow comments, in `CHANGELOG.md`, in instruction files — are dramatically cheaper for an agent to debug, because the agent can find the previous human's conclusion instead of re-deriving it. Commenting a non-obvious CI flag is not documentation overhead; it is a message to whoever, or whatever, hits the same wall next.

## The residue

One unrelated finding fell out along the way, which is usually how it goes. The weekly content-gardener workflow failed the same morning with:

```
Claude reported a successful result after 49 turns, exceeding the configured maximum of 40
```

It had done its job — the pull request was open — and then the action failed red on the turn ceiling. The identical bug in a sibling workflow had already been fixed a day earlier by raising `--max-turns` to 60; the gardener was simply missed. A ceiling that fails a run *after* it succeeded is a bad ceiling: it should be a warning, or it should stop the run before it does the work, but reporting failure on delivered output trains everyone to ignore the red.
