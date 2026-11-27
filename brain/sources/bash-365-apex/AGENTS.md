<!-- kit: sdlc v0.1.0 · AGENTS.md is the CANONICAL agent instructions file (decision D4, UPS-AGENT-07/08).
     Keep these six `##` headings (UPS-AGENT-07 checks they exist, in any order; add your own headings as needed). CLAUDE.md is a pointer to this file and carries no rules of its own. -->

# bash-365-apex

## What this repo is

A client-side redirect from the `bash-365.com` apex domain to `https://www.bash-365.com`, served by GitHub Pages for BASH Consulting. DNS for the apex is hosted where ALIAS records are unavailable, so the apex points at GitHub Pages and this repo answers with a redirect that keeps the path. A change is done when both redirects still land on the same path at `www`. Retire the repo if the apex ever moves to a DNS host with ALIAS support.

## Stack & commands

Static HTML, no build and no dependencies. Edit `index.html` or `404.html` and push to `main`; GitHub Pages serves the change.

```bash
# install: nothing
# run:     open index.html   (or any static server, e.g. python3 -m http.server)
# test:    the CI gate (.github/workflows/ci.yml) — the fleet's shared standard-ci
```

## Layout

| Path | What |
| --- | --- |
| `index.html` | Redirect for the root path |
| `404.html` | Redirect for every other path, keeping the path |
| `CNAME` | Custom domain for GitHub Pages |
| `.nojekyll` | Serves the files as-is, without a Jekyll build |

## Conventions

- **Backlog of record:** GitHub Issues with the fleet labels. Pick up issues labelled `agent:ready`; never touch `agent:hold` or `human-review`.
- **Definition of Done:** the checklist in `.github/pull_request_template.md` (the fleet default is inherited when the repo has none). Every box is ticked before merge.
- **Commits:** Conventional Commits (`feat fix docs style refactor test chore perf ci build`). The PR title is the squash subject.
- **Branches:** `feature/`, `fix/`, `docs/`, `refactor/`, `test/` or `chore/` off `main`.
- **Changelog:** `CHANGELOG.md` records notable changes.
- **Never:** push to `main` directly, commit secrets, or add a build step. This repo must stay a plain static redirect.

## Fleet context

Member of the bamr87 fleet. The standards live in the hub: <https://github.com/bamr87/bamr87/tree/main/specs> (the Universal Project Standard). Commit here first; the hub bumps its submodule pointer afterwards.

## Standard deviations

- UPS-REPO-02/03: no source, test or docs directories. The product is two HTML files; the README is the whole documentation.

## Governance

Read [`docs/constitution.md`](docs/constitution.md) before changing anything: it is the highest-precedence rule set here and wins over this file when they disagree. It changes only through a numbered record in [`docs/amendments/`](docs/amendments/), ratified by the maintainer merging the PR; agents propose, never merge. Every user-facing feature has a stable id in [`features/features.yml`](features/features.yml) with `status`, location and the PRD requirement ids it serves; the PRD's "Feature catalog" block is generated from it (`python3 <bamr87/bamr87>/tools/governance_lint.py prd-sync . --write`; check with `… check .`). Never hand-edit that block or `CHANGELOG.md`.
