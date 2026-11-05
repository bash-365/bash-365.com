---
mode: agent
description: "Review changes, validate the Jekyll build, update CHANGELOG, then commit on a branch, open a PR, wait for CI and merge with a merge commit"
date: 2026-05-18T12:00:00.000Z
lastmod: 2026-11-05T12:00:00.000Z
---

# Commit & Publish — BASH Consultants

When invoked with `/commit-publish`, walk through the publish workflow: review → validate → document → branch and commit → pull request → CI green → merge commit. The site deploys when a merge lands on `main`; nothing is pushed to `main` directly.

## Steps

### 1. Review Changes

```bash
git status --short
git diff --stat
```

Classify each changed file: `post | page | service | config | extension | ci | docs`.
Refuse to proceed if any file contains literal secret prefixes (`ghp_…`, `sk-…`, `AKIA…`). Surface unexpected items: generated `_site/`, large binaries, `Gemfile.lock` deletions.

### 2. Validate

For Jekyll changes (`_*.yml`, `_includes/**`, `_layouts/**`, `pages/**`, `*.md`):

```bash
docker-compose up -d jekyll
docker-compose exec -T jekyll bundle exec jekyll build \
  --config '_config.yml,_config_dev.yml'
```

For `extension/` changes:

```bash
cd extension && npm run lint && npm run compile
```

Stop on failure.

### 3. Update Documentation

Update `README.md` in any touched directory. Update root `README.md` only for user-visible changes. Add entry to `CHANGELOG.md` under `## [Unreleased]`:

```markdown
### Added | Changed | Fixed | Removed
- **<area>**: <one-line summary>
```

### 4. Branch and commit

```bash
git switch -c <type>/<slug>    # feature/ fix/ docs/ refactor/ test/ chore/
git add -A
git commit -m "<type>(<scope>): <imperative subject>

<body explaining why>"
```

Types: `feat fix docs refactor chore ci`. Scopes: `posts pages services config extension prompts docs`.

### 5. Pull request, CI, merge

```bash
git push -u origin HEAD
gh pr create --fill --base main
gh pr checks --watch            # ci.yml, build-validate.yml, Azure SWA staging must be green
gh pr merge --merge             # merge commit only — never --squash, --rebase or --admin
```

If CI is red, push another commit to the branch; never force-push. `main` has no branch protection here, so the merge-commit rule is yours to keep. The deploy runs when the merge lands on `main`.

### 6. Verify

```bash
sleep 60
curl -sI https://bash-365.com/ | head -1   # expect HTTP/2 200
```

## Output to User

```markdown
## Release Summary — <YYYY-MM-DD>

### Changes
- <bullet>

### Validation
| Check | Result |
|---|---|
| Jekyll build | ✅ |
| Extension lint+compile | ✅ / N/A |
| Secret scan | ✅ |

### Commit
- PR: <url>
- CI: ✅
- Merged (merge commit): <sha>
- Deployment: pending Pages build (~1-2 min)
```

## Hard Rules

- Never commit `_site/`, `node_modules/`, or `vendor/`.
- Never push tags before the commit.
- Never push to `main` directly, and never force-push any branch.
- Roll forward, never rewrite history.
