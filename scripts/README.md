# Scripts

Utility scripts for developing and maintaining bashconsultants.com. Everything listed here exists in this directory; if a script isn't listed, it was retired.

## Content quality

### `content_lint.py`

Mechanically enforces the editorial contract from `.github/instructions/content-style.instructions.md` and `posts.instructions.md` across reader-facing Markdown (posts, services, root pages): required post frontmatter, description length, banned marketing phrases, draft flags, filename/date agreement, flow-style category/tag lists, and exclamation marks in titles or descriptions.

```bash
python3 scripts/content_lint.py             # lint the repo, exit 1 on errors
python3 scripts/content_lint.py --warn-only # report but always exit 0
python3 scripts/content_lint.py --self-test # run inline fixtures
```

### `doctrine_check.py`

The deterministic half of "practice what we preach" — structural doctrine checks (DRY, single-source-of-truth) that complement `content_lint.py`'s editorial focus. An extensible registry of `@check` functions; the [preacher](../docs/the-preacher.md) grows it by mechanizing recurring AI-review burdens. The seed check, `DRY-CONTACT`, flags hardcoded contact values in content that should read from `_data/entity/info.yml`.

```bash
python3 scripts/doctrine_check.py             # run all checks, exit 1 on any violation
python3 scripts/doctrine_check.py --warn-only # report but always exit 0
python3 scripts/doctrine_check.py --list      # list the registered checks
python3 scripts/doctrine_check.py --self-test # run inline fixtures
```

### `content_inventory.py`

The deterministic seed for the weekly content review — lists every reader-facing content page with its word count, last-modified date, and age, and flags the thin and the stale. The [content curator](../.claude/agents/content-curator.md) starts from this instead of re-reading the whole corpus every week (structural pages — index stubs, landing loops — are skipped).

```bash
python3 scripts/content_inventory.py          # full table, most-neglected first
python3 scripts/content_inventory.py --focus  # the thin/stale shortlist for a weekly run
python3 scripts/content_inventory.py --json   # machine-readable (for the curator)
```

### `generate_playbook_data.py`

Generates `_data/playbook.yml` from `.github/prompts/*.prompt.md` and `.github/instructions/*.instructions.md` so Jekyll pages can loop over the prompt library. Standard library only, deterministic output.

```bash
python3 scripts/generate_playbook_data.py          # write _data/playbook.yml
python3 scripts/generate_playbook_data.py --check  # exit 1 if the file is stale
```

## Brand assets

### `generate_mark_shape.py`

Generates `_includes/brand/mark-shape.svg` — the outline the interactive homepage mark (`_includes/bash-mark.html` over `assets/js/constellation.js`) samples its stars from — straight out of the canonical `assets/brand/favicon.svg`, by Inkscape label (`outer-B`, `inner-c`, and the `B-Logo` layer's translate). The geometry is never hand-copied, so it cannot drift from the mark. Standard library only, deterministic output.

```bash
python3 scripts/generate_mark_shape.py          # write _includes/brand/mark-shape.svg
python3 scripts/generate_mark_shape.py --check  # exit 1 if the include is stale
```

### `generate_service_illustrations.py`

Generates the eight homepage service-card illustrations in `assets/images/services/*.svg` (referenced from `_data/entity/services.yml`). Shared palette, filters, and reduced-motion rules live in one template; the AI, cloud, data, and managed-IT cards are animated. Content stays inside the crop-safe band (x 90–550, y 40–200 of a 640×240 canvas) because the cards use `object-fit: cover` at a fixed 140px height. Standard library only, deterministic output.

```bash
python3 scripts/generate_service_illustrations.py          # write the SVGs
python3 scripts/generate_service_illustrations.py --check  # exit 1 if any SVG is stale
```

### `sample_mesh_points.py`

Samples a Wavefront OBJ mesh surface uniformly by area into a point-cloud JSON that the constellation engine's `points` source loads with `url:` — the way a 3D model from Blender or a CAD tool becomes a scene in `_data/constellations/`. Reads `v` and `f` records (polygons fan-triangulated), ignores normals, textures, and materials, normalizes to a unit half-size, and uses a fixed seed so the same mesh gives the same file. Standard library only. Reference: `/tools/partners/constellation-engine/`.

```bash
python3 scripts/sample_mesh_points.py model.obj -o assets/data/constellations/model.json
python3 scripts/sample_mesh_points.py model.obj --count 2400 --seed 7 > model.json
```

## The content loop (`loop/`)

The deterministic half of the [content loop](../docs/content-loop.md) — the daily routine that turns the practice's own recent work into a new article every other day and an improvement to an existing page on the days between. Standard library only; every script has a `--self-test`. The model does only the writing.

### `loop/signals.py`

Mines the activity into scored *stories*: this repository's git history (commits grouped by the `Claude-Session:` trailer, by `(#N)` pull-request reference, or by day; AI-assisted work marked by its `Co-Authored-By: Claude` trailer; areas, files, insertions and deletions), the CHANGELOG lines that mention each pull request, the committed AI-session trace, and — best-effort, read-only via `gh api` — the sister repositories in `_data/loop/sources.yml`. Stories already recorded in the ledger are marked spent and score zero.

```bash
python3 scripts/loop/signals.py --no-remote              # the digest, home repo only
python3 scripts/loop/signals.py --window 60 --json       # machine-readable, wider window
python3 scripts/loop/signals.py --out .loop              # signals.json + digest.md
```

### `loop/plan.py`

The pure decision: given the ledger, `_data/loop/config.yml`, the count of open loop PRs, and the stories, choose **new**, **improve**, or **idle** with a reason; order the section ring most-overdue first; offer the best unspent stories and the improve candidates (from `content_inventory.py`, boosted when recent work touched a page's subject). Writes `plan.json` + `plan.md` and, in CI, the job outputs.

```bash
python3 scripts/loop/plan.py --out .loop --no-remote     # decide today; read .loop/plan.md
python3 scripts/loop/plan.py --mode improve --section erp --json   # operator overrides
```

### `loop/ledger.py`

The loop's memory — one YAML record per run under `_data/loop/runs/`, committed in the same pull request as the content it describes (one file per run, so parallel loop PRs never conflict).

```bash
python3 scripts/loop/ledger.py --list
python3 scripts/loop/ledger.py --record --mode new --section tech --path <file> --title "…" --signals session:abc,pr:38 --summary "…"
python3 scripts/loop/ledger.py --set-pr <run-id> <pull-request-url>
```

### `loop/trace.py`

The session trace: the `SessionEnd` hook (`.claude/hooks/session-trace.sh`) calls `trace.py append` to record one line of scrubbed metadata per Claude Code session — id, intent (the first prompt, one line), files touched, commits carrying the session's trailer — into the local, gitignored queue `.claude/loop/sessions.jsonl`. Never a transcript. `--sync` folds the queue into the committed `_data/loop/sessions.jsonl`, which a human reviews and commits.

```bash
python3 scripts/loop/trace.py --list
python3 scripts/loop/trace.py --sync
python3 scripts/loop/trace.py --add --session-id <id> --intent "…"   # a manual entry
```

### `loop/_lib.py`

Shared helpers: a strict YAML-subset reader/writer for `_data/loop/*.yml` (no block scalars, anchors, or flow maps — by design), the git wrapper, the credential scrubber every committed string passes through, the house slug rule, and date helpers.

## Preview images

### `features/generate-preview-images` (canonical)

AI preview image generator for posts and configured collections. Reads defaults from the `preview_images` section of `_config.yml` (provider `openai`, model `gpt-image-2`, size `1536x1024`, quality `high`), detects content missing a `preview:` image, generates images via the OpenAI Images API (xAI Imagine via `--provider xai`, Stability AI, and a `local` placeholder provider are also supported), and writes them to `assets/images/previews/`.

Requires `OPENAI_API_KEY` — or, for `--provider xai`, an xAI OAuth token (read directly from the `grok login` or Kilo stores, or set as `XAI_OAUTH_TOKEN`) with `XAI_API_KEY` as the last resort; or `STABILITY_API_KEY` — see `.env.example` and `docs/preview-images.md`. Credentials are passed to `curl` via mode-600 config files, never on the command line.

```bash
./scripts/features/generate-preview-images --list-missing        # no API calls
./scripts/features/generate-preview-images --dry-run --verbose   # show prompts
./scripts/features/generate-preview-images --collection posts    # generate
```

### `features/xai-login`

Mints the subscription OAuth token behind `--provider xai` (ported from bamr87/law-ai spec 050): an RFC 8628 device-code grant by default, a loopback PKCE grant with `--loopback`, plus `--status`, `--check`, `--refresh`, and `--logout`. Writes `.xai/credentials.json` (gitignored, mode 0600); the refresh token rotates on every use. Never prints token values.

### `features/lib/preview_styles.py`

Resolves per-collection and per-section style overrides for one content file (`python3 scripts/features/lib/preview_styles.py <file>`), printing `key<TAB>value` lines the generator applies to that file only. Order is global → `collection_styles[<collection>]` → `section_styles[<section>]`, most specific winning key by key; the override keys match zer0-image-generator's, so blocks stay portable. A lookup that cannot answer exits 0 with no output rather than failing a run. Tests: `python3 -m unittest scripts/features/lib/test_preview_styles.py`.

### `features/lib/xai_auth.py`

The credential chain the generator calls (`python3 scripts/features/lib/xai_auth.py resolve`): explicit `XAI_OAUTH_TOKEN`, then the repo store above (refreshed under a cross-process lock), then the Grok CLI and Kilo stores, then `XAI_API_KEY`. Standard library only. Tests: `python3 -m unittest scripts/features/lib/test_xai_auth.py` (no network).

### `generate-preview-images.sh`

Backward-compatibility wrapper that forwards all arguments to `features/generate-preview-images`. The VS Code tasks in `.vscode/tasks.json` call this wrapper.

Related: the `zer0-image-generator` gem (root `Gemfile`) is the zer0 stack's engine for the same job — `bundle exec jekyll preview-images --list-missing` reads the same `preview_images` block in `_config.yml`. It replaced the vendored `_plugins/preview_image_generator.rb`, whose Liquid filters and tags nothing rendered. This script stays while `.github/workflows/content-loop.yml` and `.vscode/tasks.json` call it.

## Setup helpers

### `setup-admin-settings.sh`

Creates the admin/settings content pages for a site using the zer0-mistakes theme (the layouts, includes, and assets ship with the theme itself). Supports `--dry-run` and `--force`.

### `setup-git.sh`

Interactive helper for global Git configuration (user.name, user.email, editor, optional GitHub CLI wiring and SSH key upload). Dry-run by default; pass `--apply` to make changes.

```bash
bash scripts/setup-git.sh --name "Your Name" --email you@example.com          # dry-run
bash scripts/setup-git.sh --apply --name "Your Name" --email you@example.com  # apply
```

## Legacy

### `routine-maintenance.sh`

Clipboard-era helper that assembles prompts from `.github/prompts/` for manual pasting into VS Code Chat. Superseded by the Prompt Orchestrator extension in `extension/`, which runs the same workflows natively. The file is kept because the extension's code and docs reference it as the canonical command-to-prompt alias map:

| Alias | Prompt file |
|---|---|
| `refactor` | `code-refactoring.prompt.md` |
| `test` | `test-generation.prompt.md` |
| `docs` | `documentation.prompt.md` |
| `debug` | `debugging.prompt.md` |
| `analyze` | `requirements-analysis.prompt.md` |
| `design` | `system-design.prompt.md` |
| `implement` | `code-implementation.prompt.md` |
| `review` | `article-review.prompt.md` |

Prefer the extension for new work.
