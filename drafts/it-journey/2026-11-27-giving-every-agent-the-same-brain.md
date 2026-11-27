---
title: "Giving every agent the same brain"
description: "Turning a consulting site's repository into the organization's context source: a vault read in place, a registry, an agent-readiness standard, a per-repo brief and a read-only MCP server, in stdlib Python."
date: 2026-11-27
categories: [it-journey]
tags: [claude-code, mcp, second-brain, knowledge-management, obsidian, python, governance, ai-workflows, agents, bash-365]
draft: true
---

## The ask

Make bash-365.com the comprehensive context source for the whole organization and its AI agents: build in a second brain and a set of tools like the fleet hub's, so agents can contribute to and evolve every repository in the org consistently and accurately.

Two words carry the weight: *consistently* and *accurately*. An agent that starts a session in one repository knows that repository's `AGENTS.md` and whatever else happens to be in its context window. Hand the same task to two agents and they can answer to different rules, because nothing guarantees they read the same ones. The fix is not a better agent. It is a better input: one place every agent reads first, that knows who the organization is, what must always hold, which repositories exist, how to work in each, and what each one is still missing.

## Survey before design

Three things already existed, and the design had to respect all of them.

The fleet hub owns the standards (the Universal Project Standard, with stable ids like `UPS-AGENT-07`), the kits that seed every repository, and the fleet registry. Copying any of that into the site would create a second source of truth to drift.

A sibling repository already runs a fleet-wide second brain: every repository's docs collected into an Obsidian vault, a generated hot cache, and a read-only MCP server that fences third-party text. It is about 6,700 lines, built around its own registry and a MkDocs site. It knows the fleet's documentation, but nothing about the company as a company: its services, doctrine, brand rules, decisions.

The site repository itself turned out to hold most of the company's knowledge already: service pages, a toolkit of guides, case studies, posts, a constitution, ADRs, brand and editorial instructions, and a full Claude agent layer. It also had a house rule that shaped everything after it: every script is standard library only, so it runs the same on a bare CI runner and a laptop.

Then the org itself. A code search showed three repositories in the GitHub organization. Cloning the two I had not seen produced the first real finding before a line of code existed: the fleet registry listed the VS Code extension as archived and unmaintained, but the checkout was a 1.0.0 Marketplace release with docs, CI and merges the week before. The registry was wrong, and only reading the actual repository could show it.

## The shape

The central decision: **the vault is the repository, read in place.** Nothing is copied. A small config file (`_data/org/brain.yml`) lists globs and the kind each file gets (governance, rule, skill, service, toolkit, post…). The other org repositories enter only as redacted snapshots of their agent-facing docs, with a manifest recording the commit and which standard files exist.

Five modules under `scripts/brain/`, all stdlib:

- `vault.py` is the single definition of what a note is and what a link points at. The site links four ways (title wikilinks, relative paths, site permalinks like `/services/erp/`, and the site's own absolute URLs), and one resolver handles all of them, plus Liquid `{% link %}` tags. It resolves every one of the corpus's 229 wikilinks.
- `org.py` holds the registry, the agent-readiness checks, the snapshot sync, and the **brief**.
- `generate.py` writes the browsable layer: a hot cache, a map of content, one note per shared tag, a card per repository, the audit, vault health and a JSON graph. Every output carries a fingerprint of its inputs and never a timestamp, so a rebuild on an unchanged tree changes nothing.
- `brain.py` is the CLI; `mcp_server.py` serves the same answers over MCP.

The brief is the piece that turns knowledge into consistency. `brain.py brief <repo> --task "…"` joins the org operating rules, that repository's own commands and conventions (read from its agent file and fenced as third-party text), its gaps against the standard with the hub command that fixes each, the notes in the vault relevant to the task, and a Definition of Done. Two agents given the same task now start from the same page.

## Reuse over reinvention

The repository already had a YAML-subset reader (written for the content loop) and a front-matter parser (written for the editorial linter). The brain uses both instead of shipping a third and fourth parser. The credential scrubber the content loop applies to everything it commits is the same one that redacts snapshots. The agent-readiness standard is not a new standard: it is a list of the hub's existing checks that an agent needs before its first commit, each citing its `UPS-` id, plus exactly one rule only the org can set: every org repository's agent file points at the brain.

## Holding the flagship to its own standard

The first audit flagged the repository the brain lives in. Its `AGENTS.md` was 2,284 words against a 2,000-word budget, lacked the six headings the fleet standard requires, and still carried a block of notes "moved verbatim … fold these into the sections above when you next touch them." Folding them in removed a duplicated rules list (and one contradiction about pushing), and the file now passes every check at 1,830 words. A brain that audits other repositories and exempts its own home would not be worth trusting.

## Guardrails worth copying

- **Read-only server.** The MCP server has no write tool. Filing a note is a command a person or agent runs deliberately and commits in a pull request.
- **Fence what you did not write.** Snapshot text comes back inside `<untrusted-doc repo=… path=…>`, with any fence tag inside the text escaped so it cannot close the fence early.
- **Staleness warns; it does not block.** The content pipeline opens pull requests every other day. Failing them because the generated layer is a page behind would punish the wrong thing, so CI warns and a weekly, switch-gated workflow proposes the refresh.
- **Determinism makes the gate cheap.** Because outputs depend only on committed inputs, the check is a rebuild in memory and a byte comparison.

## Working with AI: tips from this session

- **Clone before you trust a registry.** The most useful fact in the session (an "archived" repository that had just shipped 1.0.0) came from reading the repository, not its metadata. Give your agent read access to the real thing.
- **Ask for the input layer, not a smarter agent.** Consistency across agents comes from a shared, queryable context and a work order, not from longer prompts.
- **Make the agent's standard cite the human standard.** Every check carries the id of the rule it implements, so a reviewer can see it is a subset, not a fork.
- **Point the audit at home first.** The first finding was against the repository doing the auditing; fixing it in the same change made the standard credible.
- **Reuse the repository's own parsers.** An agent will happily write a new YAML parser. Telling it to find the existing one keeps every tool agreeing on what a file says.
- **Leave the knowledge behind.** The brain has a `save` command for exactly the moment a session learns something the next one needs. Use it in the same pull request.

## What is next

Close the gaps the audit found: an `AGENTS.md` for the extension repository and a one-line brain pointer in the apex redirect's agent file, each in its own pull request in its own repository. Correct the fleet registry's entry for the extension in the hub. Then let the weekly refresh run, and watch whether agents that start from the brief need fewer review rounds than agents that do not.
