<!-- kit: governance v0.1.0 -->
# 0002 — Missions

- **Status:** proposed
- **Date:** 2026-11-18
- **Proposed by:** Grok Bot (agent), at the maintainer's request
- **Ratified by:**
- **Affects:** constitution §1; PRD.md §1.1; B365-009 (proposed)
- **Supersedes:** none
- **Related:** [docs/constitution.md](../constitution.md), [PRD.md](../../PRD.md) §1.1, [features/features.yml](../../features/features.yml)

## Context

Constitution §1 was a single descriptive paragraph, not one direction statement with exactly three numbered missions. The fleet rule (bamr87/bamr87) is that every repo's constitution §1 uses that form, adopted through a numbered amendment the maintainer ratifies by merging. Mission 1 is the maintainer's own wording, adapted to this repo: provide data, tools, resources and transparency for all stakeholders, practitioners in the domain, and the general public. The ambition is the direction, not a claim that the work is already finished.

The earlier §1 text was:

> Source for bash-365.com, the site of BASH Consulting (Bourne Again Solutions Hero), a Denver-based IT consulting practice for small and medium businesses. Dual-purpose: a Jekyll marketing/content site on the zer0-mistakes theme, and a VS Code extension (Prompt Orchestrator) that runs the shared prompt library. The site also demonstrates the firm's governed AI content pipeline.

## Amendment

Retitle constitution §1 **Missions**. Replace the body of §1 with the following. The invariants in §2 and every other normative rule outside §1 are unchanged.

BASH Consulting's direction is to become the ultimate open home for all things small-business IT — data, tools, resources and transparency, gathered in one place that any business owner, practitioner or curious reader can inspect and reuse.

1. **Provide data, tools, resources and transparency for all stakeholders, small and medium business owners and operators, IT, ERP and finance professionals, and the general public.** Clients, prospects, practitioners and the general public are first-class audiences. Guides, posts, checklists and the reasoning behind each recommendation are published openly, so anyone can learn from the same material a client receives.
2. **Be the born-again solutions hero for small and medium businesses: practical, plain-spoken help across the eight service areas — AI and automation, cloud, ERP, financial systems, data and BI, custom software, IT strategy and managed IT.** In the spirit of the Bourne-again shell, every engagement starts from what the business already runs and makes it work better, not from a sales pitch. bash-365.com presents those services honestly, out of Denver, with scope and trade-offs stated up front.
3. **Show the work in the open: run the firm's own content and tooling as a governed, inspectable system.** The governed AI content pipeline, the editorial directives and news desk, the Prompt Orchestrator VS Code extension, and the CI-gated dual deploy to GitHub Pages and Azure Static Web Apps are themselves the demonstration — working examples of the practices BASH recommends to clients.

These missions set the course; they do not claim the work is finished. They serve the existing constitution and PRD: the eight service areas, the governed AI content pipeline, the Prompt Orchestrator extension, and the dual deploy gated by CI. The earlier mission paragraph is absorbed into these three. Every feature must trace to them.

_Source: [../PRD.md](../PRD.md) §1.1._

## Consequences

Agents and reviewers judge fit against these three missions before inventing scope, treating them as the direction of the repo rather than a description of what already ships. When this amendment is opened as a PR, the same text is added as PRD.md §1.1 so the constitution's `_Source:` line stays accurate, a catalog entry (B365-009, "Constitution §1 missions", planned) is added to `features/features.yml` linked to the PRD requirement it serves, and the PRD feature-catalog block is regenerated. The README and AGENTS.md one-liners are aligned with the missions and link to constitution §1. Nothing else in the PRD, catalog or invariants changes.
