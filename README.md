# bash-365.com

The source for **[bash-365.com](https://bash-365.com)** — the site of BASH Consulting (Bourne Again Solutions Hero), a Denver-based IT consulting practice for small and medium businesses. This repository holds three things:

1. **Jekyll site** (repo root) — the marketing and content site, built on the [`bamr87/zer0-mistakes`](https://github.com/bamr87/zer0-mistakes) remote theme and deployed on every push to `main`.
2. **VS Code extension** (`extension/`) — *Prompt Orchestrator*, a self-contained TypeScript extension that runs the shared prompt library in `.github/prompts/` from inside the editor.
3. **The org brain** (`brain/`, `scripts/brain/`) — the organization's context source: BASH's knowledge, rules and repositories in one vault that people and AI agents query before they contribute to any org repository.

The site is also a working demonstration of how the firm operates: it is written, reviewed, illustrated, validated, and shipped through a governed AI pipeline. See [`/tools/`](https://bash-365.com/tools/) and [`/ai-operations/`](https://bash-365.com/ai-operations/).

## Services

The site presents eight service areas — AI and intelligent automation, cloud architecture, ERP consulting, financial systems, data and business intelligence, custom software development, IT strategy, and managed IT — under [`/services/`](https://bash-365.com/services/). Service pages live in `pages/_services/`.

## Quick start (Jekyll site)

The site builds Docker-first; the host Ruby on most machines is too old for the theme (requires Ruby ≥ 3.2).

```bash
# Local dev server → http://localhost:4042 (livereload on 35730)
docker-compose up

# One-off build validation (matches the local dev stack)
docker-compose exec jekyll bundle exec jekyll build \
  --config '_config.yml,_config_dev.yml'

docker-compose down
```

**Git worktrees:** the theme is mounted from a sibling checkout. Point the mount at the real checkout with `ZER0_MISTAKES_PATH` (defaults to `../zer0-mistakes`):

```bash
ZER0_MISTAKES_PATH=/path/to/zer0-mistakes docker-compose up
```

A `.devcontainer/` is provided for Codespaces and container-based editors.

## Quick start (extension)

```bash
cd extension
npm install
npm run lint && npm run compile && npm test
```

The extension runs from source (it is not published to the Marketplace). See [`extension/README.md`](extension/README.md) and [`extension/QUICKSTART.md`](extension/QUICKSTART.md).

## The org brain

The vault is this repository read in place (services, toolkit, case studies, posts, the constitution, the brand and editorial rules, the agent layer), plus hand-written notes and snapshots of the other org repositories. Ask it from a terminal or over MCP (`bash-brain` in `.mcp.json`):

```bash
python3 scripts/brain/brain.py hot                                    # where to start
python3 scripts/brain/brain.py query erp migration                    # ranked notes
python3 scripts/brain/brain.py brief bash-365-apex --task "add a security.txt"   # the work order for an org repo
python3 scripts/brain/brain.py audit                                  # every org repo against the agent-readiness standard
```

The generated layer in `brain/generated/` (hot cache, map of content, concepts, a card per repository, the audit) is browsable on GitHub or in Obsidian. The operator's guide is [`docs/brain.md`](docs/brain.md).

## Build and deploy

Every push to `main` triggers two deploys, gated by CI:

| Stack | Config | Theme | Notes |
| --- | --- | --- | --- |
| GitHub Pages | `_config.yml` | `remote_theme: bamr87/zer0-mistakes@v1.26.0` (safe mode) | Static only; DNS rollback. Custom `_plugins/` do not run |
| Azure Static Web Apps | `_config.yml` + `_config.azure.yml` (`Gemfile.azure`) | `jekyll-theme-zer0` gem | `/api/chat`, PR staging. IaC in `infra/azure/`; deploy is `.github/workflows/azure-swa.yml` |

`.github/workflows/build-validate.yml` builds **both** production stacks and runs the content linter on every push and pull request. Automation (nightly site-health, weekly content drafts, the AI chat proxy) is documented in [`docs/automation.md`](docs/automation.md).

## The zer0 stack

This site is a consumer of the zer0 stack: the [`zer0-mistakes`](https://github.com/bamr87/zer0-mistakes) theme (`remote_theme` in `_config.yml`, with every deliberate fork declared in [`.theme-overrides.yml`](.theme-overrides.yml)), the [`zer0-image-generator`](https://github.com/bamr87/zer0-image-generator) gem for preview banners (root `Gemfile`, configured by the one `preview_images:` block in `_config.yml`), and [zer0-CMS](https://github.com/bamr87/zer0-CMS), which reads [`zer0.json`](zer0.json) for the content folders and the required front matter. `.github/workflows/zer0-doctor.yml` runs zer0-CMS's contract check every week, on a pull request that touches `zer0.json`, `fleet.manifest.yml`, `.theme-overrides.yml` or `_config.yml`, or on demand from the Actions tab, and fails on an error; from a zer0-CMS checkout, run it locally with `cd content && .venv/bin/python -m sites.doctor /path/to/bash-365.com`. LinkedIn publishing runs through zer0-CMS's distribution lane; locally, `scripts/linkedin.sh status`.

## Repository layout

```
_config.yml            Production config (GitHub Pages, remote theme)
_config_dev.yml        Local dev overrides (gem theme, port 4042)
_config.azure.yml      Azure Static Web Apps overrides
_data/                 Site data — entity info, navigation, taxonomy, playbook
_layouts/, _includes/  Site-local overrides of the remote theme
_plugins/              Local Jekyll plugins (Pages runs in safe mode — see below)
pages/_posts/          Blog posts, by section: corp / erp / muses / tech
pages/_services/       Service detail pages + hub
pages/_case-studies/   Anonymized engagement snapshots
api/                   Azure Functions app (AI chat proxy)
infra/azure/           Bicep + az bootstrap/cutover for Static Web Apps
scripts/               Preview-image generator, content linter, playbook data, the brain engine
brain/                 The org brain: notes, snapshots of the other org repos, generated layer
_data/org/             The org registry, the agent-readiness standard, the brain config
extension/             VS Code extension (independent sub-project)
.github/               AI-agent instructions, prompt library, workflows
docs/                  Internal operations docs (excluded from the build)
```

## Contributing conventions

- **Read the guidance first.** [`AGENTS.md`](AGENTS.md) is the entry point for AI agents; [`.github/instructions/`](.github/instructions/) holds the authoritative editorial and code rules per file path.
- **Validate before declaring done.** Jekyll changes → run the Docker build. Extension changes → `npm run lint && npm run compile && npm test`.
- **Conventional commits:** `<type>(<scope>): <subject>`. Don't mix Jekyll-site and `extension/` changes in one commit.
- **Update [`CHANGELOG.md`](CHANGELOG.md)** for user-visible changes.
- **Never commit** `_site/`, `node_modules/`, `vendor/`, or secrets.

## Contact

**BASH Consulting** — Denver, Colorado Email: [info@bash-365.com](mailto:info@bash-365.com) · Phone: [720-352-4641](tel:+17203524641) · Web: [bash-365.com](https://bash-365.com)

## License

MIT — see [LICENSE](LICENSE).
