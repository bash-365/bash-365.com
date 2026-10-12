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
