# PRD — bash-365.com

> Product requirements for [`bash-365/bash-365.com`](https://github.com/bash-365/bash-365.com).
> Derived from the README, agent docs, config and code in this repo. Anything not
> stated in those sources is marked **TBD**; success metrics are proposals.

## 1. Overview / problem

Source for bash-365.com, the site of BASH Consulting (Bourne Again Solutions Hero), a Denver-based IT consulting practice for small and medium businesses. Dual-purpose: a Jekyll marketing/content site on the zer0-mistakes theme, and a VS Code extension (Prompt Orchestrator) that runs the shared prompt library. The site also demonstrates the firm's governed AI content pipeline.

## 2. Target users

- SMB prospects evaluating IT/ERP/AI consulting services
- The firm, publishing content through the AI pipeline
- Developers using the Prompt Orchestrator extension (runs from source)

## 3. Goals and non-goals

**Goals**

- Present eight service areas (AI/automation, cloud, ERP, financial systems, data/BI, custom software, IT strategy, managed IT)
- Publish blog content (corp/erp/muses/tech) through a governed AI pipeline
- Deploy to both GitHub Pages and Azure Static Web Apps, gated by CI

**Non-goals**

- Publishing internal agent docs on the site (excluded from build)
- Marketplace publication of the extension (not published)

## 4. Core features (current)

- Jekyll site with `_layouts`/`_includes` overrides and local `_plugins/`
- Dual deploy: GitHub Pages (safe mode, theme pinned v1.26.0) and Azure SWA (`/api/chat`, PR staging, IaC in `infra/azure/`)
- `build-validate.yml` builds both stacks and runs the content linter
- Nightly site-health, weekly content drafts, AI chat proxy
- `extension/` Prompt Orchestrator (TypeScript)

## 5. Requirements

**Functional**

- Both production stacks build on every push/PR
- Repo docs (README, CLAUDE, AGENTS, CHANGELOG, PRD) are excluded from the built site

**Non-functional**

- Ruby ≥ 3.2 (Docker-first local dev)
- Custom plugins do not run on GitHub Pages

## 6. Success metrics (proposed — not defined in sources)

- Inbound consultation inquiries: TBD
- Site-health check pass rate
- Content published per month

## 7. Roadmap / open questions

- Which stack is canonical for the apex long-term (see bash-365-apex): TBD

## 8. Links

- [README.md](README.md) · [AGENTS.md](AGENTS.md) · [CLAUDE.md](CLAUDE.md) · [CHANGELOG.md](CHANGELOG.md)
