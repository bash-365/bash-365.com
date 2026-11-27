# ADR 0002 — The org brain lives in the site repository, read in place

- **Status**: proposed
- **Date**: 2026-11-27
- **Deciders**: proposed by Claude Code at the maintainer's request; accepted when the maintainer merges the pull request
- **Related**: [docs/brain.md](../brain.md), feature B365-010, PRD FR5

## Context

The maintainer asked for bash-365.com to become the comprehensive context source for the organization and its AI agents, with a second brain and tooling like the hub's, so agents contribute to every org repository consistently and accurately. The fleet already has two neighbours that do part of this: the hub (bamr87/bamr87) owns the standards, kits and fleet registry, and bamr87/README collects every fleet repository's documentation into a vault with a read-only MCP server. Neither knows BASH as a company (its services, doctrine, brand and editorial rules, decisions), and neither gives an agent a single work order for an org repository. Most of BASH's knowledge already lives in this repository, as site content and governance files.

## Decision

Build the org brain in this repository, under `brain/` (vault outputs, notes, snapshots), `_data/org/` (registry, standard, config) and `scripts/brain/` (engine, CLI, MCP server, tests).

- The vault is this repository **read in place**: no page is copied. Other org repositories enter only as redacted snapshots of their agent-facing docs in `brain/sources/`, refreshed by `brain.py sync`.
- The engine is **standard library only** and reuses the repo's existing YAML-subset and front-matter parsers.
- The generated layer (`brain/generated/`, `brain/graph.json`) is **committed** and deterministic, so readers that run nothing (GitHub, another repository's agent, a cloud session) still get it; the CLI and the MCP server read the working tree live, so they are never stale.
- Staleness **warns** in CI rather than failing, so content pull requests and the content loop are never blocked on a rebuild; a weekly, switch-gated workflow proposes the refresh.
- The agent-readiness standard is a **cited subset** of the hub's Universal Project Standard (each check names its UPS id), plus one org-only rule: every org repository's agent file points at the org brain. The hub's conformance gate stays the authority for the whole standard.
- The MCP server is **read-only**; filing a note is a command, committed in a pull request.

## Consequences

**Positive**

- One query surface for BASH's knowledge and rules, with a brief that turns them into a work order for any org repository.
- Nothing new to install; the engine runs wherever the content loop runs.
- The flagship repository is held to the same standard it asks of the others (it passes all checks after this change).

**Negative**

- The committed generated layer churns with content; refresh pull requests are the price of a layer that works without running anything.
- Snapshots of other repositories can lag their source by up to a week unless someone runs `sync`.
- A second registry (`_data/org/repos.yml`) beside the hub's: the org file records only what the org needs and names drift with the hub instead of correcting it here.

## Alternatives considered

- **Use bamr87/README's context engine as is** — it is built around the fleet registry's collect and navigation rules and a MkDocs site, knows nothing of BASH's content model, and would put the org's rules in another repository's vault.
- **Vendor the README engine into this repository** — about 6,700 lines tied to its registry and navigation contracts; most of it (collection, MkDocs navigation, AI enrichment) has no job here.
- **Generate the brain only in CI, never commit it** — keeps diffs clean, but leaves agents that only read files (and other repositories' agents) with nothing to read.
- **A brain repository of its own** — a fourth org repository to keep in sync with the one that holds most of the knowledge it describes.

## Supersedes / Superseded by

- Supersedes: none
- Superseded by: none
