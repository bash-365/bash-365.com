---
title: "Raising ELIZA: what happens when you forbid an AI agent from looking up the answer"
description: "Weizenbaum's 1966 MAD-SLIP ELIZA, revived by a Claude Code harness with no web access, gated at every step, and proven against the published transcript — plus the invisible bug where the agents ran without the method at all."
date: 2026-09-15
categories: [it-journey]
tags: [claude-code, ai-workflows, mcp, legacy-systems, eliza, agent-harness, software-archaeology, testing, governance, bash-365]
draft: true
---

## The ask

*Walk through the quest using an example from GitHub: a very old, common, retired application that is not well documented, convoluted and obscure, and bring it back to functional life using only the quest methods. Bootstrap an AI harness to the quest, run it in a sandbox, push the outcome to a new repository, document everything.*

The relic chosen was ELIZA — not one of the hundreds of reimplementations, but the program Joseph Weizenbaum actually wrote, in MAD-SLIP, for CTSS on an IBM 7094. It sat in a folder in his papers at MIT for about half a century. It is public domain now, from `jeffshrager/elizagen.org`, and the folder scan carries the CC0 mark with the collection number written on it by hand: MC-0383, box 8.

The result: seven chapters, 7/7 gates passed, 190 agent turns, $6.77, and a reconciliation that ties out against Weizenbaum's published conversation turn by turn, 15 of 15, zero mismatches.

The interesting part is not that it worked. It is the bug that almost let it look like it worked when it hadn't.

## Why this relic is harder than a COBOL one

The campaign these chapters come from was written against a COBOL accounts-receivable program: a copybook, packed decimal, a Y2K pivot, and an executable you can still compile and run. Chapter one says "compile it and run it."

**You cannot run ELIZA.** No MAD-SLIP compiler survives. There is nothing to execute, nothing to diff against, no way to ask the system what it does. The only observable behaviour left in the world is the fifteen-turn conversation Weizenbaum printed in the January 1966 *CACM*.

That single transcript is the entire oracle. Everything else is reading a dead language off a punched-card deck — and you can see the deck in the file, sequence numbers still sitting in columns 73–80.

This is not an artificial difficulty. It is where a lot of real legacy work is heading: the binary still runs, but the toolchain that built it is gone, and the people who knew why are gone with it.

## The design decision that mattered

**The harness is deterministic. The model is spent only where judgment is needed.**

The harness owns the chapter order, the tool allow-list, the sandbox boundary, the gates and the ledger. The agent gets one job per chapter, and a script decides whether it succeeded. The gate's verdict, not the agent's own report, is what gets written down — because a model asked "did you do it?" will usually say yes.

The part worth stealing: **the harness never states the method.** It points the agent at an MCP server that serves the quest, and the agent fetches the chapter it is executing. Change the quest content and the run changes. No prompt in the harness needs editing. That is the difference between a harness and a pile of prompts — the method becomes versioned content, and the harness is just plumbing.

Two models, pinned, nothing else: Sonnet 5 for the chapters that reason about a dead language, Haiku 4.5 for the two that are disciplined writing against evidence already on disk. That is a real cost decision, and the cheaper model carried the decision records and the runbook without trouble.

## Cutting the network is what makes it mean anything

```
--disallowedTools WebSearch,WebFetch
```

There are hundreds of ELIZA implementations on the public web. An agent that finds one has not revived a relic; it has copied an answer and dressed it up. Denying network access is the single line that turns this from a demo into evidence.

The same logic applies well beyond ELIZA. If you want to know whether an agent can actually read your undocumented system, you have to stop it from reading about systems like yours.

## The bug that was invisible

This is the finding worth the whole exercise.

The quest content and the MCP server lived on two branches of the same repository. After a container restart, the checkout came up carrying the server but not the campaign. The server started fine. It answered fine. It answered `no campaign matches 'relic-raisers'`.

**The chapter still ran.** The agent fell back on the goal string in the harness, produced plausible, well-structured work, and the gate — which only inspects files — found what it was looking for and passed. The run would have completed looking entirely successful, with the central premise of the whole campaign quietly missing.

Every gate asked *does the output look right?* None asked *did the agent have the input?*

> An agent given less context than you think does not fail. It improvises, plausibly.

That sentence is the transferable lesson. Humans fail loudly when you take their brief away — they ask. A model fills the gap and keeps going, and the gap does not appear anywhere in the output.

Two fixes, and both are cheap:

1. **A preflight.** Call the context source before spending a cent and refuse to start if it does not resolve. Verified in both directions — it passes on a good checkout and fails on a bad one, reproduced deliberately with a `git worktree` of the server-only branch. A check you have only seen pass is not a check.
2. **An audit log.** `QUEST_MCP_LOG` makes the MCP server append one line per served call. The harness fails any chapter with zero calls. "The agent consulted the method" is now a recorded fact with tool names attached, not an assumption.

The campaign was then re-run from chapter one — not because the early chapters looked wrong, but because they could not be *proven* to have had the method. The partial run is archived rather than deleted.

## Three more bugs, all of the same family

**A gate that would have passed the defect it existed to catch.** Chapter four's gate exists to prove the tests are *red* before the port is written, because tests that pass against a port that does not exist are testing nothing. It returned `True` unconditionally. Found by reading my own gates back and asking, for each one, *what output would make this gate wrong?*

**A gate asserting an interface nobody specified.** Chapter two's gate ran the agent's parser with no arguments; the agent had written it to take the script path as an argument, which the goal never forbade. Exit code 2, gate FAIL — on work that was completely correct (68 rule forms, 213 reassembly rules, exactly one `NONE` rule). The ledger now keeps **both** verdicts with a note explaining the re-run. A ledger you silently correct is not a ledger.

**A resume path that erased the campaign.** The run summary was assembled from the current invocation, so resuming with `--from 3` dropped chapters 1–2 while their files sat on disk, intact and ignored. Found the way these always are: the container restarted mid-run. Anything that runs for an hour will be interrupted; the durable record has to be the thing on disk.

There is a pattern here. Every one of these bugs is in the *checking* layer, not the work. The agent's output was consistently better than my machinery for judging it.

## Proving it is not a Plausible Ghost

The campaign names the failure mode it fears most: a port that produces correct-looking output by hardcoding the expected answers. It looks alive and it is not.

A ledger that ties out proves nothing by itself — a lookup table would also tie out. So, three checks after the fact:

1. **No hardcoded replies.** The only occurrence of any golden reply in the port is a docstring example.
2. **Novel inputs**, none of which appear in the transcript: `I dreamed about my computer last night.` → `DO COMPUTERS WORRY YOU`. `My sister is a doctor.` → `TELL ME MORE ABOUT YOUR FAMILY` (the `FAMILY` DLIST tag). `Do you remember what I said?` → `DID YOU THINK I WOULD FORGET WHAT YOU SAID` — correct pronoun inversion. Gibberish → the `NONE` rule.
3. **Mutate the data and watch the behaviour follow.** Change one reassembly rule in a copy of the 1966 script and the port's reply changes to match. The personality is data, exactly as Weizenbaum built it.

And a nice piece of self-inflicted irony: **the first version of check 3 reported `HARDCODED`.** The check was wrong, not the port. It called `respond()` twice per engine, and ELIZA *cycles reassembly rules* — so the second call legitimately returns a different answer. My verification script tripped over the relic's single most famous behaviour:

```
IN WHAT WAY → WHAT RESEMBLANCE DO YOU SEE →
WHAT DOES THAT SIMILARITY SUGGEST TO YOU → WHAT OTHER CONNECTIONS DO YOU SEE
```

Verification code is code. It gets the same bugs, and nothing verifies *it*.

## What reading a program nobody can run actually finds

- **The personality is data.** ELIZA is an interpreter; DOCTOR is a script it runs. That is the insight the whole dig turns on, and it came out of chapter two's parser rather than out of prior knowledge.
- **`NEWKEY` is not implemented as a retry** in the transcribed source — it prints the literal string. Recorded in an ADR as a known reduction from the 1966 paper rather than smoothed over.
- **The MEMORY slot hash cannot be reproduced.** SLIP's `HASH` is unavailable and undocumented. The ADR records the substitute as *correct for the golden transcript and not a proven-equivalent replacement.* That is the honest verdict rather than the flattering one, and it is the kind of sentence that saves somebody six weeks later.
- **The two transcriptions disagree** on three identifiers. Resolving it needs a fact about MAD's identifier limit nobody on the dig could establish, so it is filed as an open question instead of guessed.

Chapter one also reported, unprompted, that it could not read the MAD manual — no PDF tooling in the sandbox — and listed what that source would have answered as *unknowns*. It would have been easy and undetectable to guess. Installing `poppler-utils` closed the gap for the re-run.

## Tips worth carrying to your own agent work

**Deny the shortcut explicitly.** If the answer is findable online, an agent will find it, and you will learn nothing about your system. `--disallowedTools` is a research instrument.

**Put the method in content, not in prompts.** Served over MCP, the method becomes reviewable, diffable and reusable. Prompts embedded in a driver script are none of those.

**Assert your context channel is live, and record that it was used.** This is the one most people are missing. Everyone tests that the agent produced something; almost nobody tests that the agent received something.

**Make one gate require failure.** A test suite that has never been seen red is not a test suite. The same is true of every gate you write — run it against input that should fail it.

**Never silently correct a ledger.** When a gate is wrong, keep both verdicts and say why. The audit trail is the product.

**Ask of every gate: what output would make this wrong?** Three of the four bugs here came out of that single question.

**Absolute paths in every agent instruction.** A bare filename lands in whatever directory the agent happens to be in, and the report of success will be perfectly accurate about a file nobody wanted.

## The shape of it

The deliverable is a repository: the relic untouched under CC0, the harness, the agent's work, and a ledger recording model, turns, cost, gate verdict and every method call for all seven chapters. `bash verify.sh` runs the trials, then the reconciliation, then the evidence check on the decision records, and exits non-zero on the first failure.

The method is older than the tooling. Pin the behaviour before you touch it, translate, reconcile line by line, put a gate in front, and write down why for whoever comes next. The AI does not replace any of that. What it changes is the cost of the reading — the part that used to make legacy work unaffordable — provided you build the thing that would catch it if it were wrong.
