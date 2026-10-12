---
title: "A content loop that writes from the commit log"
description: "Porting lifehacker.dev's autopilot to a consulting site: deterministic Python decides when and offers what, the model writes, a human merges — and the AI sessions themselves become the story source."
date: 2026-09-05
categories: [it-journey]
tags: [github-actions, claude-code, jekyll, python, automation, content-pipeline, git, governance, ai-workflows, bash-365]
draft: true
---

## The ask

One sentence, three constraints: build a content harness for bash-365.com like the autopilot that runs lifehacker.dev, publish one new article every other day with rotating topics and improvements to existing pages in between, and drive the ideas from real work — commits, pull requests, features, tools, and the AI sessions that produced them — in the consultancy's own voice for its own audience.

The interesting word is *drive*. Most content automation starts from a topic list and asks a model to fill it. This one starts from the repository's history and asks a model to explain it to someone who signs checks.

## Survey before design

The session began with reading, not writing. lifehacker.dev's loop is documented in three files — the operator's guide, the architecture, and the CI/CD map — and the shape that emerged is worth stating plainly: everything load-bearing is a script (the fingerprints, the RICE math, the budget split, the lease), models do only judgment inside role agents, every run ends in one pull request, and a human is the only commit authority. Two smaller patterns came along: a `*_ENABLED` repository variable as the single ON switch for every loop, and a two-store session-retrospective hook — a local, gitignored queue that a `SessionEnd` hook appends to, and a committed ledger written only when a human publishes.

Then the target. bash-365.com already had the pieces a loop needs to lean on: an editorial linter with self-tests, a content inventory script that flags thin and stale pages, a doctrine checker, three weekly Claude routines (a gardener, a curator, a preacher) all written as `claude-code-action` workflows that skip gracefully without a credential, and instruction files that define the voice down to banned phrases and the one-CTA rule.

The finding that changed the design came from `git log`. The repository's commits already carried two trailers: `Co-Authored-By: Claude …` on AI-assisted work, and `Claude-Session: https://claude.ai/code/session_…` on the sessions run through Claude Code on the web. The "tracing of AI sessions" the ask wanted was mostly already in git — grouping commits by that trailer reconstructs a session's work with no hook, no transcript, and no model call. The hook only had to add the one thing git does not carry: what the session set out to do.

## The shape

Five stdlib-only Python scripts under `scripts/loop/`, each with a `--self-test`, because that is how every other script in that repo is built:

- `signals.py` mines the history into *stories* — commits grouped by session trailer, else by `(#N)` pull-request reference, else by day — with files, insertions and deletions, the areas of the repo touched, CHANGELOG lines that mention the PR, and the session's intent when a trace exists. Sister repositories are read through `gh api` when a token exists and skipped with a note when it does not.
- `plan.py` is the pure decision: new, improve, or idle, with a reason. The cadence is ledger-driven rather than calendar-driven — a mode is due when enough days have passed since the ledger's last record of it, and when both are due the more overdue one runs first — so a failed run is caught up the next day rather than doubled or dropped. A backpressure cap on open loop PRs comes before everything else.
- `ledger.py` keeps one YAML file per run. lifehacker.dev solved concurrent appends to its backlog with a custom git merge driver; one file per run needs no driver, because two pull requests that each add a different file never conflict.
- `trace.py` is the session hook's body: intent, files, commits, a turn count, all scrubbed, into a local queue; `--sync` folds the queue into the committed trace so a person sees the diff before it is public.
- `_lib.py` holds a strict YAML-subset reader and writer, because the repo's convention is no PyYAML and the loop's data files are simple enough to deserve a parser that refuses anything fancy.

The workflow runs the planner daily, publishes the plan and the activity digest to the run summary, and only then spends a model: the writer agent reads the plan as an artifact, follows a written skill, and opens one pull request. It is off until a repository variable says otherwise, and while it is on, the two weekly content routines stand down so a topic is never drafted twice.

## The problem that fell slowly

Scoring. The first live run of the miner against the real history put a three-day-old whitespace fix — one commit, one file, prose unwrapped to one paragraph per line — at the top of the digest, above an eighteen-day-old session that retired a theme override, declared every fork in a manifest, and backfilled the author profiles across ten files. Recency was doing all the work.

The fixtures had not caught it because the fixtures were built to check grouping, not ranking. The fix was three small changes made as data rather than cleverness: a flatter recency curve, a heavier size term, and a commit-type factor that discounts `style` and `chore` below `feat` and `fix`. After that the substantive session led, the whitespace fix sat third, and the weights moved into `config.yml` so the next adjustment is a diff to a data file, not a code change.

Two smaller bugs are worth admitting because the self-tests caught them within a minute of writing them: the YAML parser's tab-indentation guard measured indentation in spaces only, so a tab-indented line slipped through; and a changelog line cleaner that stripped list markers with `lstrip("-* ")` also ate the bold asterisks off the first word. Neither would have surfaced in a demo. Both surfaced in a fixture.

## What it does on day one

With the branch committed and the trailers in place, the miner already sees this session as a story: three commits grouped under one session id, the intent line from the trace, the areas it touched. The first scheduled run, if the variable is flipped, would decide *new*, put the `tech` section first because it has waited longest, and offer the writer the work of building the loop itself — which is the right first story for a site whose pitch is that it runs on the same governed AI it sells.

## Working-with-AI tip

Read the sibling system and the target's conventions before designing, and let what you find overrule the plan you walked in with. The plan on entry was a `SessionEnd` hook that captured everything. The `git log` survey showed the commits already carried session identifiers, so the hook shrank to the one field git lacks, the miner became deterministic and offline, and the whole "AI-session tracing" requirement became a `grep` over trailers — auditable by anyone, with no transcript ever leaving a laptop.

Two habits made the rest go faster. Make every deterministic piece self-testing *and* run it against real history early — the fixtures proved the grouping, the live digest exposed the ranking flaw, and neither alone would have been enough. And put every weight and threshold in a data file the moment you find yourself tuning it, so the tuning conversation with the model is about numbers in YAML rather than rewrites in Python.

## Where it stands

A draft pull request, off by default, with the operator's guide, the scripts, the skill and the agent charter, the workflow, and the first session trace committed. Turning it on is one repository variable. Turning it off is the same variable.
