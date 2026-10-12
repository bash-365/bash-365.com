---
title: "Forging an epic quest whose every command was run"
description: "A seven-chapter it-journey campaign on reviving legacy systems with AI, built by first building the legacy system: a COBOL relic with deliberate strata, a reconciliation that catches the AI's port, and a content pipeline whose gates did the reviewing."
date: 2026-09-14
categories: [it-journey]
tags: [claude-code, ai-workflows, cobol, legacy-systems, jekyll, quests, verification, content-pipeline, it-journey, bash-365]
draft: true
---

## The ask

One sentence again, and a more ambitious one: *write an epic quest that focuses on learning how to use futuristic AI tools to uncover and discover how the ancient systems of the past work, and how to revive and update them.*

The destination was the it-journey repository, whose quests are gamified, fantasy-framed lessons with a strict shape: registry-governed frontmatter, a validator that scores every quest, a dependency graph that must stay whole, a glossary that is the single source of naming truth, and a rule that every command a learner is told to run must be accurate — "if you cannot verify it, it does not ship." That last rule decided how the whole session went. The quest could not be written first and checked later. The lab had to exist before the prose.

## Build the relic before you write about it

An epic quest about legacy systems needs a legacy system, and it needs one with the specific traps the campaign exists to teach. So the first hour went into forging one: `ARAGE01`, a 150-line COBOL accounts-receivable aging program in fixed-format columns, a copybook with a `REDEFINES` and an implied decimal, an 80-byte fixed-width data file, and three deliberate strata written into the header comments — a 1997 origin "converted from RPG II", a 1999 Y2K window with pivot 50, and a 2006 rule that status `7` is excluded from aging "per J.R./Accounting".

GnuCOBOL installed from apt on the sandbox's Ubuntu 24.04 in a couple of minutes, and the relic compiled and ran on the first attempt. Every later artifact in the campaign is downstream of that binary being real: golden masters captured from it, characterization tests that run it in a scratch directory, a Python port reconciled against it, an HTTP gate that shells out to it.

The design choice that made the boss chapter work was building the ghosts in on purpose. A first port of the relic that assumes every two-digit year is 20xx misdates one invoice by a century; a port that never reads the status byte ages a disputed invoice; a port that sums floats is silently fragile. All three are what a fluent first translation actually does, and the reconciliation script catches exactly the first two on eight records — three totals refuse to tie — while the third is shown with a one-line `Decimal` demonstration. The mismatch table in Chapter V is a real run, not a story about one.

## What the repository's own gates caught

The campaign went through the repo's tooling in the order its instructions prescribe, and each gate earned its keep:

- **The prose unwrapper skipped the new files.** `make prose-oneline-apply` defaults to git-tracked markdown, and eight brand-new files are untracked. The CI gate would have failed on any wrapped paragraph. Running the tool with explicit paths fixed it; the lesson is that "default: tracked files" is a quiet exclusion of exactly the files you just wrote.
- **A dependency pointed at a filename, not a permalink.** The hub recommended `/quests/0011/prompt-crystal-mastery-vscode-copilot/`, which is the file's name; its permalink is `/quests/0011/prompt-crystal-vscode-copilot/`. The network validator reported the broken edge, and the fix was reading the target's frontmatter instead of trusting the filename.
- **Two Mermaid hexagons were Liquid.** The capstone's architecture map used the hexagon node shape, written `{{ ... }}`, which Jekyll's Liquid pass would consume before Mermaid ever saw it. A grep for double braces across the new files found them; stadium shapes rendered the same idea without the trap. The repo's `make liquid-check` sweep then came back clean.
- **The quest validator scored every chapter**, 100% for the first and 95.9% for the rest, with one recommended-section warning on chapters that are not platform-dependent — the same warning the existing epic chapters carry. The hub, living in the codex directory, is unscored by design and was written to the full structure anyway.
- **The CI-parity build** ran in 111 seconds with the published remote theme, and all eight pages rendered where the permalinks said they would, with the codex index and the level hubs listing them.

## The glossary is a law, and it was obeyed

The instructions say a quest may not mint synonyms for anything the glossary already names, and that new coinages land in the glossary first, in the same change. The campaign leaned on existing terms — relics, the Labyrinth, familiars, the Oracle, the Chronicle, the Gauntlet of Trials, summoning circles, Benign Necromancy — and coined eight: archaeology, relic-raising, strata, the Elders, the Rosetta Ledger, the Strangler Fig, characterization trials, and the Plausible Ghost. Each went into the glossary's tables with the same three-part shape the existing entries use, in the same commit as the quests that use them. Reading the whole glossary before writing a word of narrative was the difference between a campaign that speaks the realm's language and one that invents a dialect.

## Working this way with an AI

- **Verify by construction.** When a rule says every command must be accurate, the cheapest way to comply is to build the thing first and paste from real runs. The chapters carry a provenance block naming the OS, compiler, and interpreter versions and the date, and they say plainly which two artifacts were not executed in the lab (the Dockerfile and the CI workflow, whose commands were run on the host instead).
- **Make the AI a proposer, never a judge.** The campaign's prompts ask the familiar to cite paragraphs, to list what it cannot know, to enumerate branches for tests, and to review a gateway for hazards — and every chapter then reproduces one claim with a run. The session followed the same rule about itself: the reviewer's job was to propose, the tooling's job was to decide.
- **Design the failure you want to teach.** A lesson about a fluent, wrong port is only honest if the port is real and the wrongness is caught by a mechanism, not by narration. Building the ghosts into the relic's strata made the boss fight a run instead of a fable.
- **Read the repo's law before its examples.** The permalink table in one file was stale relative to the executable validator, and the agents file said so: trust executable sources over prose. The precedent set by the existing epic hubs, confirmed by the validator, settled it.
- **Expect your new files to be invisible to defaults.** Untracked files, unindexed titles, ungenerated data: three of the session's five fixes were the tooling not yet knowing the files existed. Run generators and sweeps with explicit paths after authoring.

## The residue

- The bash-365.com repository keeps these session write-ups under `drafts/it-journey/`, but it-journey no longer hosts blog posts; its agents file says general blog content moved to lifehacker.dev. The folder name is now a signpost to the wrong repository, and the drafts probably belong in lifehacker.dev's tree.
- The relic's silent acceptance of a garbage as-of date — it prints a report "as of 2700/41/23" and exits clean — was found by a probe while writing Chapter VI and became the chapter's hazard lesson. It is also an unwritten assumption worth its own decision record: the parameter file was always written by a trusted job, so nobody validated it.
- The pivot at 50 has a cliff in 2050. The capstone records it as a deferred decision with a review date rather than a fix, which is the honest treatment of a rule that is correct today and wrong on a known future day.
