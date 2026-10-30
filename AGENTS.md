# AGENTS.md — AI Agent Guide for bash-365.com

> Cross-tool entry point for AI coding agents (GitHub Copilot, Codex, Cursor, Aider, Claude Code, …). Follows the [agents.md](https://agents.md/) convention.

## Project Snapshot

Dual-purpose repository:

1. **Jekyll site** (root) — `bash-365.com` marketing/content site, GitHub Pages deploy on push to `main`, uses `jekyll-theme-zer0` remote theme.
2. **VS Code extension** (`extension/`) — "Prompt Orchestrator", TypeScript + esbuild, self-contained sub-project.

Default dev environment: Docker Compose for the Jekyll site (`docker-compose up`); `npm` inside `extension/` for the extension.

For the full overview see [`.github/copilot-instructions.md`](./.github/copilot-instructions.md).

## Where Agent Guidance Lives

| Layer | Location | When to read |
|---|---|---|
| Cross-tool entry | `AGENTS.md` (this file) | Always first |
| Claude Code entry | `CLAUDE.md` | Claude Code reads this automatically; it adds the `.claude/` layer |
| Project Copilot instructions | `.github/copilot-instructions.md` | Always second |
| Brand — single source of truth | `.github/instructions/brand.instructions.md` | Before any brand / voice / identity work |
| Canonical frontmatter schema | `.github/FRONTMATTER.md` | When editing any `.prompt.md` or `.instructions.md` |
| File-scoped instructions | `.github/instructions/*.instructions.md` | Auto-loaded when files match `applyTo` |
| Reusable prompts | `.github/prompts/*.prompt.md` | When asked to run a multi-step task that matches a prompt |
| Claude-native primitives | `.claude/` (skills, agents, commands, memory, hooks) | In Claude Code — see `.claude/README.md` |
| Workflows | `.github/workflows/` | When changing CI (the content loop's design lives in `docs/content-loop.md`) |

### Claude Code layer (`.claude/`)

Claude Code has native primitives that specialize this cross-tool guidance. Map in `.claude/README.md`.

| Primitive | Location | Use for |
|---|---|---|
| Skills | `.claude/skills/*/SKILL.md` | Governed procedures (editorial gate, toolkit-doc authoring, wikilinks, brand) |
| Subagents | `.claude/agents/*.md` | Delegated jobs (article review, build validation, brand audit, the weekly `preacher` doctrine enforcer, the weekly `content-curator` reviewer, the daily `loop-writer` — see `docs/the-preacher.md`, `docs/content-loop.md`, `docs/automation.md`) |
| Commands | `.claude/commands/*.md` | `/`-triggers: `/lint-content`, `/new-toolkit-doc`, `/brand-check`, `/loop-run` |

### File-scoped instruction map

| Editing files in… | Read |
|---|---|
| Anything that carries the brand outward (content, `_layouts/**`, `_includes/**`, `assets/brand/**`) | `.github/instructions/brand.instructions.md` |
| Any customer-facing page (`pages/**`, `index.md`, `about.md`, `contact.md`) | `.github/instructions/content-style.instructions.md` |
| `pages/_posts/**` | `.github/instructions/posts.instructions.md` (+ content-style) |
| `pages/_services/**` | `.github/instructions/services.instructions.md` (+ content-style) |
| `_includes/**`, `_layouts/**`, `_sass/**`, `_data/**`, `_plugins/**`, `_config*.yml`, `Gemfile*` | `.github/instructions/jekyll-theme.instructions.md` |
| `extension/**` | `.github/instructions/extension.instructions.md` |
| `.github/prompts/**`, `.github/instructions/**` | `.github/instructions/prompts.instructions.md` |

## Reusable Prompts

| Task | Prompt |
|---|---|
| Full commit + push + deploy workflow | `.github/prompts/commit-publish.prompt.md` |
| Review an article for structure / SEO | `.github/prompts/article-review.prompt.md` |
| Generate documentation | `.github/prompts/documentation.prompt.md` |
| Implement / refactor code | `.github/prompts/code-implementation.prompt.md`, `code-refactoring.prompt.md` |
| Debug an issue | `.github/prompts/debugging.prompt.md` |
| Generate tests | `.github/prompts/test-generation.prompt.md` |
| System design / requirements | `.github/prompts/system-design.prompt.md`, `requirements-analysis.prompt.md` |
| Prompt engineering | `.github/prompts/prompt-engineering.prompt.md` |

## Essential Commands

```bash
# Jekyll site
docker-compose up                                          # Start dev server
docker-compose exec jekyll bundle exec jekyll build \
  --config '_config.yml,_config_dev.yml'                   # Validate build
docker-compose down

# Extension
cd extension && npm install
cd extension && npm run lint && npm run compile

# Publish
# Use /commit-publish prompt — direct-to-main triggers Pages deploy
```

## Operating Rules

1. **Minimal, surgical changes.** Match existing style. Don't refactor adjacent code.
2. **Validate before declaring done.** Jekyll changes → run the Docker build. Extension changes → `npm run lint && npm run compile`.
3. **Conventional commits**: `<type>(<scope>): <subject>`.
4. **Update `CHANGELOG.md`** for user-visible changes (add to `[Unreleased]`).
5. **No secrets.** Refuse to commit literal `ghp_*`, `sk-*`, `AKIA*`.
6. **Don't mix Jekyll and extension changes** in one commit.
7. **Don't commit** `_site/`, `node_modules/`, `vendor/`.

---

_Keep this file short — push detail into `.github/copilot-instructions.md` and `.github/prompts/`._

## Governance

Read [`docs/constitution.md`](docs/constitution.md) before changing anything: it is the highest-precedence rule set here and wins over this file when they disagree. It changes only through a numbered record in [`docs/amendments/`](docs/amendments/), ratified by the maintainer merging the PR; agents propose, never merge. Every user-facing feature has a stable id in [`features/features.yml`](features/features.yml) with `status`, location and the PRD requirement ids it serves; the PRD's "Feature catalog" block is generated from it (`python3 <bamr87/bamr87>/tools/governance_lint.py prd-sync . --write`; check with `… check .`). Never hand-edit that block or `CHANGELOG.md`.

## Claude Code notes

Moved verbatim from the former `CLAUDE.md` on 2026-10-20 (decision D4: one canonical agent file). Fold these into the sections above when you next touch them.


> The canonical entry point for **Claude Code** in this repository. Read this first, every session.
>
> This repo is a working demonstration of what BASH Consulting sells: a practice that runs on
> **governed AI** — rules in files, reusable playbooks, agents that draft, humans who approve. The
> `.claude/` directory below is the reference implementation of that model. When you work here, you
> are also maintaining the showcase. Practice what we preach.

## What this repository is

A dual-purpose repository. Treat the two sub-projects independently — **never mix them in one commit.**

1. **Jekyll site** (repo root) — `bash-365.com`, built on the `bamr87/zer0-mistakes` remote
   theme, deployed to GitHub Pages on every push to `main`. This is the primary project.
2. **VS Code extension** (`extension/`) — *Prompt Orchestrator*, a self-contained TypeScript
   sub-project that runs the shared `.github/prompts/` library from inside the editor.

The site builds **Docker-first** (host Ruby is usually too old). See [`AGENTS.md`](./AGENTS.md) for the cross-tool overview and [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) for the full project reference. This file does not repeat them — it adds the Claude-native layer.

## The context framework — where guidance lives

Guidance is layered. Read from the top; the deeper layers auto-load or are pulled in on demand.

| Layer | Location | Loaded |
|---|---|---|
| **Claude entry point** | `CLAUDE.md` (this file) | Always, automatically |
| **Cross-tool entry point** | [`AGENTS.md`](./AGENTS.md) | Read once per session |
| **Project reference** | [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | Read once per session |
| **Brand — the single source of truth** | [`.github/instructions/brand.instructions.md`](./.github/instructions/brand.instructions.md) | Before any brand/voice/identity work |
| **Content style** | [`.github/instructions/content-style.instructions.md`](./.github/instructions/content-style.instructions.md) | Editing any customer-facing page |
| **File-scoped rules** | `.github/instructions/*.instructions.md` | Auto-matched by `applyTo` glob |
| **Frontmatter schema** | [`.github/FRONTMATTER.md`](./.github/FRONTMATTER.md) | Editing any `.prompt.md` / `.instructions.md` |
| **Content taxonomy** | [`_data/taxonomy.yml`](./_data/taxonomy.yml) | Categorizing or voicing a post |
| **The content loop** | [`docs/content-loop.md`](./docs/content-loop.md) + `_data/loop/` | Before touching the loop's scripts, data, workflow, or the session-trace hook |

### The Claude-native primitives (`.claude/`)

Four primitives, one job each. See [`.claude/README.md`](./.claude/README.md) for the full map.

| Primitive | Directory | Use it when |
|---|---|---|
| **Skills** | `.claude/skills/*/SKILL.md` | You need a *governed procedure* — the same steps done the same way every time (editorial gate, authoring a toolkit doc, wikilink discipline, brand application, LinkedIn share drafting, one cycle of the content loop). |
| **Subagents** | `.claude/agents/*.md` | You want to *delegate* a bounded job to a fresh context (editorial review, build validation, brand audit, the loop writer). Invoke via the Agent tool. |
| **Commands** | `.claude/commands/*.md` | You want a discoverable `/`-entry point that runs a common workflow (`/lint-content`, `/new-toolkit-doc`, `/brand-check`, `/linkedin-draft`, `/loop-run`). |
| **Memory + hooks** | `.claude/agent-memory/`, `.claude/hooks/`, `.claude/settings.json` | Agents carry decisions across sessions; hooks enforce policy automatically (the `SessionEnd` trace feeds the content loop). |

**The content loop** is the showcase's autopilot: a daily, variable-gated routine that turns the practice's own commits, pull requests, and AI sessions into one new article every other day and one improvement on the days between, through the scripts in `scripts/loop/`, the `content-loop` skill, the `loop-writer` agent, and one human-merged pull request per run. Read [`docs/content-loop.md`](./docs/content-loop.md) before changing any of it.

**Skills vs. prompts:** `.github/prompts/*.prompt.md` are the *cross-tool* library (Copilot, the extension, Cursor). `.claude/skills/` are the *Claude-native* equivalents — richer, with optional scripts. When both exist, prefer the skill inside Claude Code; keep the two in sync when you change a shared workflow.

## Operating rules

These are the hard rules for working in this repo. The brand and content-style files add detail; these are the ones you cannot skip.

1. **Minimal, surgical changes.** Match the surrounding style. Do not refactor adjacent code, and do
   not restructure the remote theme — override via `_includes/`, `_layouts/`, `_sass/`, `_data/`. Every override is declared in `.theme-overrides.yml` — see "Theme overrides" below.
2. **Validate before declaring done.**
   - Jekyll changes → run the Docker build:
     `docker-compose exec -T jekyll bundle exec jekyll build --config '_config.yml,_config_dev.yml'`
   - Content changes → run the editorial gate (lints the whole repo, exit 1 on errors): `python3 scripts/content_lint.py`
   - Extension changes → `cd extension && npm run lint && npm run compile`
3. **Governed content.** Customer-facing copy obeys `content-style.instructions.md` and
`brand.instructions.md`: no banned phrases, acronyms expanded on first use, sentence-case headings, one H1, `description` 120–155 chars with no trailing period, one CTA. **Enact, don't announce** — never name a piece's own creative device in reader-facing text.
4. **Never invent** metrics, client names, logos, or certifications. Describe categories of work and
   what compliance frameworks require; never claim BASH is certified.
5. **Deterministic-first.** If a step can be a script, it is a script (`scripts/`). Spend the model
where judgment is needed. Generated data (`_data/playbook.yml`, tool tables) comes from scripts, not hand-editing — change the source, regenerate.
6. **Author is `Amr Abdel-Motaleb`.** Conventional commits: `<type>(<scope>): <subject>`
   (type ∈ `feat fix docs refactor chore ci`; scope ∈ `posts pages services config extension prompts docs toolkit`).
7. **Update `CHANGELOG.md`** (`[Unreleased]`) for user-visible changes.
8. **No secrets, ever.** Refuse to commit literal `ghp_*`, `sk-*`, `AKIA*`. API keys live
   server-side (`api/`, Azure app settings) — never in the repo or the browser.
9. **Commit to the working branch; do not push** unless explicitly asked. The final polish pass on
   any content is done with Opus 4.8.
10. **Don't commit** `_site/`, `node_modules/`, `vendor/`, `.playwright-mcp/`.

## Obsidian wikilinks (a repeated foot-gun)

Internal cross-links use Obsidian `[[Page Title]]` syntax, resolved client-side. Two rules save hours:

- **Pipeless only.** `[[Page Title]]` survives the kramdown GFM parser; the aliased form `[[a|b]]`
  gets mangled into a table. Reword instead of aliasing.
- **Collection docs + non-root pages only.** The wiki index covers collection docs and pages with an
`output_ext` of `.html`; it does **not** index root-level pages (`tools.md`, `ai-operations.md`). Link to those with a normal markdown link. Full detail: the `wikilinks` skill.

## Theme overrides (what we fork, and why)

The site is a thin consumer of `bamr87/zer0-mistakes`. Anything under `_includes/` or `_layouts/` that shares a path with the theme **shadows** it. [`.theme-overrides.yml`](./.theme-overrides.yml) at the repo root is the source of truth for those forks: fork a file, add its row with an honest reason. An undeclared fork reads as accidental drift to the theme's `audit-consumer`, and the point of the file is that its list stays short and true.

| Override | Why |
|---|---|
| `_layouts/landing.html` | Bespoke marketing homepage — the interactive B-mark hero (`_includes/bash-mark.html`), services grid from `_data/entity/services.yml`, industries/process/FAQ. Replaces the theme's generic `_data/landing.yml` template. |
| `_includes/analytics/posthog.html` | Consent gate, Global Privacy Control, no IP geolocation. **Retirable now** — upstreamed in v1.28.0 as `posthog.privacy.*`, set in `_config.yml`, and `remote_theme` is untagged so the theme honours them. Delete in its own PR after diffing the rendered PostHog init on both stacks. |
| `_includes/analytics/google-tag-manager-head.html` | Deliberate no-op stub. Google Tag Manager is off site-wide; PostHog is the only analytics. |
| `assets/images/wizard-on-journey.png` | Our own homepage/Open Graph image that happens to share a path with an unrelated theme asset. |

`_data/**` and `_plugins/**` are **not** overrides — Jekyll never loads either from a theme, so ours are the only copies that run. `_data/authors.yml` exists for exactly that reason: the theme's author card and "About the Author" box read `site.data.authors`, which `remote_theme` does not ship. Its `name:` values must stay byte-identical to the `author:` strings in post front matter, or bylines fall back to a bare name and a generic icon.

## Build stacks (know which config you're in)

| Stack | Config | Theme source | Built by CI? |
|---|---|---|---|
| **Local dev** | `_config.yml,_config_dev.yml` | path gem (`/zer0-mistakes` mount) | **No** |
| **GitHub Pages** | `_config.yml` alone | `remote_theme`, untagged (latest) | Yes (`build-pages`) |
| **Azure Static Web Apps** | `_config.yml,_config.azure.yml` | `Gemfile.azure` gem pin | Yes (`build-azure`) |

Local dev runs on port 4042 with livereload and is the only stack where `_plugins/` execute; GitHub Pages is **safe mode**, so anything depending on a local plugin (e.g. server-side wikilink resolution) must also work without it, or it is broken in production.

**CI never builds the local-dev stack.** `.github/workflows/build-validate.yml` builds only the Pages and Azure stacks (plus the content lint). The Docker command in operating rule 2 is a *developer* check that nothing verifies afterwards — a change that builds only under `_config_dev.yml` can still be broken in production, and a change that breaks only local dev will pass CI silently. Validate against the stack the change ships on, and treat a green PR as evidence about Pages and Azure only.
