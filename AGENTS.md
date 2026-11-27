# AGENTS.md — AI Agent Guide for bash-365.com

> Cross-tool entry point for AI coding agents (Claude Code, GitHub Copilot, Codex, Cursor, …), following the [agents.md](https://agents.md/) convention. `CLAUDE.md` imports this file; it is the canonical agent file for this repository.

## What this repo is

The source of [bash-365.com](https://www.bash-365.com), the site of BASH Consulting (Bourne Again Solutions Hero), a Denver IT consulting practice for small and medium businesses, and the organization's context hub. It is three things; treat them independently and **never mix the site and the extension in one commit**:

1. **Jekyll site** (repo root): the marketing and content site on the `bamr87/zer0-mistakes` remote theme, deployed on every merge to `main`. The primary project.
2. **VS Code extension** (`extension/`): *Prompt Orchestrator*, a self-contained TypeScript sub-project that runs the shared `.github/prompts/` library from the editor.
3. **The org brain** (`brain/`, `scripts/brain/`, `_data/org/`): BASH's knowledge, rules and repositories as one queryable vault, so any agent can contribute to any org repository consistently. See [docs/brain.md](docs/brain.md).

The repo is a working demonstration of what BASH sells, a practice that runs on **governed AI**: rules in files, reusable playbooks, agents that draft, humans who approve. When you work here you maintain the showcase too, so practice what we preach. **Done** means the gates under Stack & commands pass for what you touched, the nearest README and this file say what changed, and a human merges the pull request.

## Start with the org brain

Before changing this repo or any other org repository, ask the brain. It reads this repository live and joins the rules, the repo's commands and the notes relevant to your task:

```bash
python3 scripts/brain/brain.py hot                                   # where to start
python3 scripts/brain/brain.py brief <repo> --task "what you will do"  # the work order
python3 scripts/brain/brain.py query <words>                         # ranked notes; cite their paths
```

The same answers come over MCP from the `bash-brain` server in `.mcp.json` (`get_brief`, `search`, `get_note`, …). The rules every org contribution follows are [brain/notes/org-operating-rules.md](brain/notes/org-operating-rules.md); the `org-brain` and `org-contribute` skills are the procedures.

## Stack & commands

Jekyll on the zer0-mistakes theme (Docker-first: host Ruby is usually older than the 3.2 the theme needs), a TypeScript extension, stdlib-only Python 3 scripts, and GitHub Actions.

```bash
# Jekyll site (http://localhost:4042)
docker-compose up
docker-compose exec -T jekyll bundle exec jekyll build --config '_config.yml,_config_dev.yml'   # validate a build
docker-compose down

# Content and doctrine gates
python3 scripts/content_lint.py          # editorial contract; lints the whole repo, exit 1 on errors
python3 scripts/doctrine_check.py        # structural doctrine checks
python3 tools/unwrap-prose.py --check    # Markdown: one paragraph per line (--write fixes)

# The org brain
python3 scripts/brain/brain.py --self-test
python3 scripts/brain/brain.py check     # registry + standard valid, no secrets; warns when stale
python3 scripts/brain/brain.py build     # regenerate brain/generated/ after changing a source

# Extension
cd extension && npm install && npm run lint && npm run compile && npm test

# Governance (from a bamr87/bamr87 checkout)
python3 <bamr87/bamr87>/tools/governance_lint.py check .
python3 <bamr87/bamr87>/tools/governance_lint.py prd-sync . --write

# Publish: /commit-publish — branch, PR, CI green, merge commit; deploy runs on the merge to main
git switch -c docs/<slug> && git push -u origin HEAD && gh pr create --fill
```

## Layout

| Path | What lives there |
|---|---|
| `pages/` | Site content: `_posts/` (corp, erp, muses, tech), `_services/`, `_toolkit/`, `_case-studies/`, `_about/` |
| `_data/` | Site data (entity, navigation, taxonomy, characters, the content loop) and `org/`, the org registry, standard and brain config |
| `_layouts/`, `_includes/`, `_plugins/`, `assets/` | Site-local overrides of the remote theme, local plugins (dev only), static assets |
| `brain/` | The org brain: `notes/` (hand-written), `sources/` (other org repos' snapshots), `generated/` and `graph.json` (generated) |
| `scripts/` | Content linter, doctrine check, the content loop (`loop/`), the brain (`brain/`), preview images, publishing helpers |
| `extension/` | Prompt Orchestrator (independent sub-project) |
| `api/`, `infra/azure/` | Azure Functions chat proxy; Bicep and bootstrap for Static Web Apps |
| `docs/` | Operations docs, the constitution, amendments and ADRs (excluded from the build) |
| `.github/`, `.claude/`, `.agents/`, `.codex/` | Instructions, prompts and workflows; the Claude layer and its Codex mirror |
| `features/`, `verify/`, `drafts/` | Feature catalog, browser verification scenarios, unpublished drafts |

## Where agent guidance lives

Read from the top; the deeper layers auto-load or are pulled in on demand.

| Layer | Location | When to read |
|---|---|---|
| This file | `AGENTS.md` | Always first |
| The constitution | `docs/constitution.md` | Before changing anything; it wins over this file |
| Org operating rules | `brain/notes/org-operating-rules.md` | Before contributing to any org repository |
| Project reference | `.github/copilot-instructions.md` | Once per session |
| Brand, the single source of truth | `.github/instructions/brand.instructions.md` | Before any brand, voice or identity work |
| Content style | `.github/instructions/content-style.instructions.md` | Editing any customer-facing page |
| File-scoped rules | `.github/instructions/*.instructions.md` | Auto-matched by `applyTo` glob |
| Front-matter schema | `.github/FRONTMATTER.md` | Editing any `.prompt.md` or `.instructions.md` |
| Content taxonomy | `_data/taxonomy.yml` | Categorizing or voicing a post |
| The content loop | `docs/content-loop.md` + `_data/loop/` | Before touching the loop's scripts, data, workflow or session-trace hook |
| Portable prompts | `.github/prompts/*.prompt.md` | A multi-step task one of them covers (`commit-publish`, `article-review`, `documentation`, …) |
| Claude-native layer | `.claude/` (map: `.claude/README.md`); mirrored for Codex in `.codex/` and `.agents/skills/` | In Claude Code or Codex |

**File-scoped instruction map:**

| Editing files in… | Read |
|---|---|
| Anything that carries the brand outward (content, `_layouts/**`, `_includes/**`, `assets/brand/**`) | `brand.instructions.md` |
| Any customer-facing page (`pages/**`, `index.md`, `about.md`, `contact.md`) | `content-style.instructions.md` |
| `pages/_posts/**` | `posts.instructions.md` (+ content-style) |
| `pages/_services/**` | `services.instructions.md` (+ content-style) |
| `_includes/**`, `_layouts/**`, `_sass/**`, `_data/**`, `_plugins/**`, `_config*.yml`, `Gemfile*` | `jekyll-theme.instructions.md` |
| `extension/**` | `extension.instructions.md` |
| `.github/prompts/**`, `.github/instructions/**` | `prompts.instructions.md` |

**Claude primitives**, one job each: **skills** (`.claude/skills/*/SKILL.md`) are governed procedures (editorial gate, toolkit docs, wikilinks, brand, LinkedIn shares, the content loop, the org brain, contributing to an org repo); **subagents** (`.claude/agents/*.md`) take delegated jobs (editorial review, build validation, brand audit, the weekly `preacher` and `content-curator`, the daily `loop-writer`); **commands** (`.claude/commands/*.md`) are the `/` triggers (`/lint-content`, `/new-toolkit-doc`, `/brand-check`, `/linkedin-draft`, `/loop-run`, `/brain`, `/brief`); **memory and hooks** carry decisions across sessions and enforce policy (the `SessionEnd` trace feeds the content loop). `.github/prompts/` is the cross-tool library; when a skill and a prompt cover the same workflow, prefer the skill in Claude Code and keep the two in sync.

## Conventions

- **Backlog of record:** GitHub Issues (`.github/sdlc.yml`, `backlog.mode: issues`); `editorial:directive` issues from the hub feed the content lanes. **Definition of Done:** `.github/pull_request_template.md`. **Decisions:** ADRs in `docs/adr/`.
- **Commits:** Conventional Commits, `<type>(<scope>): <subject>`, type ∈ `feat fix docs refactor chore ci`, scope ∈ `posts pages services config extension prompts docs toolkit brain`. Author is `Amr Abdel-Motaleb`.
- **Branches and merging: pull requests only, never push to `main`.** Branch off `main` (`feature/` `fix/` `docs/` `refactor/` `test/` `chore/`), push only when asked, open a pull request, wait for CI (`ci.yml`, `build-validate.yml`, the Azure SWA staging build), and merge with a **merge commit**: never squash or rebase, never `--admin`, never force-push. `main` has no branch protection, so this is a convention you keep, not a setting that enforces it.
- **Changelog:** add user-visible changes to `CHANGELOG.md` under `[Unreleased]`.
- **Minimal, surgical changes.** Match the surrounding style; do not refactor adjacent code or restructure the remote theme.
- **Governed content.** Customer-facing copy obeys `content-style.instructions.md` and `brand.instructions.md`: no banned phrases, acronyms expanded on first use, sentence-case headings, one H1, `description` 120–155 characters with no trailing period, one CTA. **Enact, don't announce:** never name a piece's own creative device in reader-facing text. The final polish pass on any content is done with Opus 4.8.
- **Deterministic-first.** If a step can be a script, it is a script (`scripts/`); spend the model where judgment is needed.
- **Never:** invent metrics, client names, logos or certifications (describe what frameworks require; never claim BASH is certified); commit secrets (refuse literal `ghp_*`, `sk-*`, `AKIA*`; keys live server-side in `api/` or Azure app settings); hand-edit generated files (`_data/playbook.yml`, tool tables, `brain/generated/`, the PRD feature-catalog block); commit `_site/`, `node_modules/`, `vendor/` or `.playwright-mcp/`; mix site and extension changes in one commit.

**Obsidian wikilinks (a repeated foot-gun).** Internal cross-links use `[[Page Title]]`, resolved client-side in production. Use the pipeless form only: kramdown turns `[[a|b]]` into a table; reword instead of aliasing. The wiki index covers collection docs and pages with an `.html` `output_ext`, not root-level pages (`tools.md`, `ai-operations.md`): link those with a normal Markdown link. Full detail: the `wikilinks` skill.

**Theme overrides.** The site is a thin consumer of `bamr87/zer0-mistakes`; anything under `_includes/` or `_layouts/` that shares a path with the theme shadows it. [`.theme-overrides.yml`](.theme-overrides.yml) is the source of truth for those forks: fork a file, add its row with an honest reason. Today: `_layouts/landing.html` (the bespoke homepage), `_includes/analytics/posthog.html` (consent gate; retirable now that theme v1.28.0 ships `posthog.privacy.*`, in its own PR after diffing the rendered init on both stacks), `_includes/analytics/google-tag-manager-head.html` (a deliberate no-op stub) and `assets/images/wizard-on-journey.png` (our image at a theme path). `_data/**` and `_plugins/**` are not overrides: Jekyll never loads either from a theme. `_data/authors.yml` exists because `remote_theme` does not ship it; its `name:` values must match post `author:` strings byte for byte.

**Build stacks.** Know which config you are in:

| Stack | Config | Theme source | Built by CI? |
|---|---|---|---|
| Local dev | `_config.yml,_config_dev.yml` | path gem (`/zer0-mistakes` mount), port 4042 | No |
| GitHub Pages | `_config.yml` alone | `remote_theme`, untagged | Yes (`build-pages`) |
| Azure Static Web Apps | `_config.yml,_config.azure.yml` | `Gemfile.azure` gem pin | Yes (`build-azure`) |

Local dev is the only stack where `_plugins/` run; GitHub Pages is safe mode, so anything that depends on a local plugin must also work without it. CI never builds the local-dev stack: validate against the stack the change ships on, and treat a green PR as evidence about Pages and Azure only.

## Fleet context

A member of the bamr87 fleet, checked out in the hub [bamr87/bamr87](https://github.com/bamr87/bamr87) as `projects/bash-365.com`: commit and push here first; the hub bumps its pointer afterwards. The hub owns the standards this repo is measured against ([specs/](https://github.com/bamr87/bamr87/tree/main/specs)), the kits that seeded `ci.yml`, `markdown-oneline.yml`, `conformance.yml` and `verify.yml` (change those through the hub, never here), and the content atlas that files editorial directives. Org-wide context (who BASH is, the rules, a card for every org repository and its agent-readiness) lives in the org brain, [github.com/bash-365/bash-365.com/tree/main/brain](https://github.com/bash-365/bash-365.com/tree/main/brain); the fleet-wide documentation brain is [bamr87/README](https://github.com/bamr87/README).

## Standard deviations

none (`.github/sdlc.yml` declares `deviations: []`)

## Governance

Read [`docs/constitution.md`](docs/constitution.md) before changing anything: it is the highest-precedence rule set here and wins over this file when they disagree. It changes only through a numbered record in [`docs/amendments/`](docs/amendments/), ratified by the maintainer merging the PR; agents propose, never merge. Every user-facing feature has a stable id in [`features/features.yml`](features/features.yml) with `status`, location and the PRD requirement ids it serves; the PRD's "Feature catalog" block is generated from it (`python3 <bamr87/bamr87>/tools/governance_lint.py prd-sync . --write`; check with `… check .`). Never hand-edit that block or `CHANGELOG.md`.
