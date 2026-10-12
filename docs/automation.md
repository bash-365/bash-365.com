# Automation: scheduled workflows and the AI chat proxy

This page documents the repo's automation: the GitHub Actions workflows and the Azure Functions app in `api/` that powers the site's AI chat widget. It is an internal operations doc — `docs/` is excluded from the Jekyll build.

The workflows: **build & validate** (the PR gate), **Azure Static Web Apps** (OIDC deploy of the Jekyll Azure stack + `/api/chat`), **site health** (nightly), **content loop** (daily, activity-driven: a new article every other day and an improvement on the days between — see [`content-loop.md`](./content-loop.md)), **content gardener** (weekly new-post draft), **content review** (weekly expand-or-add), **PR to upstream** (fork sync), and **the preacher** (weekly doctrine enforcement — see [`the-preacher.md`](./the-preacher.md)).

## What runs where

The repo deploys to two hosts from the same source:

| Host | Deployed by | Serves |
| --- | --- | --- |
| Azure Static Web Apps (SWA) — app `swa-bash365-prod` (planned primary) | `.github/workflows/azure-swa.yml` after `./infra/azure/bootstrap.sh` | Static site plus managed Azure Functions under `/api/`, PR staging URLs. Custom domains: `bash-365.com` and `www.bash-365.com` after `./infra/azure/cutover.sh`. |
| GitHub Pages | GitHub's built-in Pages build (github-pages gem + `remote_theme`) | Static site only. DNS rollback target. `/api/chat` does not exist here. Keep Pages enabled; do not delete the repo `CNAME` file. |

The AI chat widget only has a working backend on SWA. `_config.azure.yml` sets `ai_chat.proxy_ready: true`; `_config.yml` keeps it `false`, so a DNS rollback to Pages does not render a dead widget.

Do **not** revive `proud-pond-06dc10c1e` or `.github/workflows/azure-static-web-apps-proud-pond-06dc10c1e.yml`. The LinkedIn automation runs entirely in GitHub Actions and needs no server-side host.

## The chat proxy (`api/`)

`api/src/functions/chat.js` is an Azure Functions app (Node.js v4 programming model) that `.github/workflows/azure-swa.yml` deploys with `swa deploy --api-location ./api` (prebuilt `_site`, no Oryx). It implements the zer0-mistakes theme's chat proxy contract, ported from the theme's Cloudflare Worker reference implementation (`templates/deploy/chat-proxy/worker.js` in the theme repo). The chat route lives in `chat.js`; the issue route the widget uses to file visitor reports lives in `github.js` (see "Issue reports from the chat" below). Both share the origin allowlist, error shape, body cap, and per-IP rate limiter in `api/src/lib/gate.js`.

What it does, in order:

1. Answers `OPTIONS` preflight; rejects anything that isn't `POST`.
2. Rejects requests whose `Origin` header isn't on the allowlist
(production domains, this SWA's own hostnames including per-PR staging hostnames, plus anything in the `ALLOWED_ORIGINS` setting).
3. Returns `503` when neither `CLAUDE_CODE_OAUTH_TOKEN` nor
   `ANTHROPIC_API_KEY` is configured, so an accidentally enabled widget fails cleanly.
4. Applies a fixed-window in-memory rate limit per client IP
   (default 20 requests per minute per function instance).
5. Caps the request body size (default 512 KB) and validates the JSON shape
   (`messages` must be a non-empty array).
6. Forwards `{model, max_tokens, system, messages, tools, stream: true}` to
the Anthropic Messages API with the server-held credential, capping `max_tokens` (default cap 4096) and pinning the model server-side (`CHAT_MODEL`, else the default) — the client's `model` field is ignored so a tampered request can't select a costlier model.
7. Streams the Server-Sent Events response back unchanged. The widget also
accepts a buffered or plain-JSON response, so `CHAT_BUFFER_RESPONSE=true` is available as a fallback.

**Auth: Claude Code OAuth preferred, API key fallback.** The proxy picks its credential by precedence:

1. `CLAUDE_CODE_OAUTH_TOKEN` — a long-lived Claude Code OAuth token from
`claude setup-token` (Claude Pro/Max). Used by default when set. Sent as `Authorization: Bearer <token>` with the `anthropic-beta: oauth-2025-04-20` header. Because subscription OAuth must identify as Claude Code, the proxy forces the first `system` block to the Claude Code identity and keeps the site assistant's own prompt as the following block.
2. `ANTHROPIC_API_KEY` — a standard workspace `x-api-key`. The fallback, used
   only when no OAuth token is set.

Set exactly one (OAuth wins if both are present). The rotating-refresh OAuth mode from the theme's Cloudflare worker is not ported — it needs a key/value store SWA functions don't provide, so use the long-lived setup-token instead.

The credential is read from the environment at request time and is never sent to the browser, logged, or echoed in error messages. The rate limit keys on the last `X-Forwarded-For` hop (the value Azure's trusted front end appends), not the client-supplied first entry, so a caller can't spoof its way around the cap.

**Response-time ceiling.** SWA managed functions enforce a hard 45-second HTTP response limit. Bicep/workflow set `MAX_TOKENS_CAP=2048` (code default is 4096). Pin a faster model via `CHAT_MODEL` if generations still approach the ceiling.

Not ported from the worker: the rotating-refresh OAuth mode (needs Cloudflare KV) and the pull-request route. `/api/github/pull-request` exists only to refuse with a `403` that tells the model to file an issue instead; anonymous visitors do not get branches.

### Issue reports from the chat (`api/src/functions/github.js`)

When a visitor reports a typo, broken link, or wrong information, the widget shows a confirmation card and then `POST`s `{ title, body, labels }` to `/api/github/issue` (`ai_chat.github.mode: 'proxy'` in `_config.yml`). The function files the issue on `bash-365/bash-365.com` with a server-held token and returns `{ url, number }`. The widget used to run in `'url'` mode, which opened a pre-filled github.com form on `site.repository`. That broke: `site.repository` still named `bamr87/bashconsultants`, which has issues disabled. Proxy mode also means a visitor needs no GitHub account to report a problem, where a github.com form requires one.

What the function adds on top of the shared gate:

- Labels are cut to an allowlist (`CHAT_ISSUES_LABELS`), and `from-chat` is always applied, so reports are easy to triage. If GitHub rejects the labels (`422`), the report is filed again without them rather than lost.
- `@`-mentions in the title and body get a zero-width space, so a report cannot notify arbitrary accounts.
- A footer marks the issue as visitor-supplied and unverified, and records the page it came from (the `Referer`, when it is one of the site's own origins).
- A stricter rate limit than chat: 3 issues per IP per 10 minutes by default.
- Every error message is written for the model to relay, and each one points the visitor to email. Without `CHAT_ISSUES_TOKEN` the route answers `503` and the chat suggests email.

The site's `ai_chat.system_prompt` tells the model to report through `create_github_issue`, to quote the page's real source via `get_page_source` (which reads the public repo from `raw.githubusercontent.com`) when that helps, and not to call `create_pull_request`. The theme enables that tool in proxy mode, and the function refuses it server-side as a backstop.

**The token.** Create a fine-grained personal access token under the `bash-365` organization with access to **only** `bash-365/bash-365.com` and the single repository permission **Issues: Read and write**. Store it as the `CHAT_ISSUES_TOKEN` Actions secret; the production deploy copies it into the app settings. Set an expiry and a calendar reminder to rotate it. A leaked token can do no more than open and label issues in one repo.

### Application settings (Azure portal → Static Web App → Environment variables)

| Setting | Required | Default | Purpose |
| --- | --- | --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN` | One of these two to activate chat | — | Claude Code OAuth token (`claude setup-token`). **Preferred** — used when set. |
| `ANTHROPIC_API_KEY` | One of these two to activate chat | — | Workspace API key with a spend cap. Fallback, used only when no OAuth token. |
| `CHAT_MODEL` | No | `claude-opus-4-8` | Model, pinned server-side; the client's `model` field is always ignored. Bicep sets this. |
| `MAX_TOKENS_CAP` | No | `2048` on SWA (code default 4096) | Upper bound on client-requested `max_tokens`. Bicep/workflow set 2048 for SWA's 45s ceiling. |
| `SWA_ORIGIN_PREFIX` | Yes on SWA | first label of `defaultHostname` | Allows this app's default and PR-staging `*.azurestaticapps.net` origins. Never hardcode a previous app name. |
| `MAX_BODY_BYTES` | No | `524288` | Request body cap in bytes. |
| `ALLOWED_ORIGINS` | No | production + SWA hostnames | Comma-separated extra origins (e.g. `http://localhost:4000` while testing). |
| `RATE_LIMIT_MAX` / `RATE_LIMIT_WINDOW_MS` | No | `20` / `60000` | Requests per window per IP, and window length. |
| `CHAT_BUFFER_RESPONSE` | No | unset | Set `true` to buffer the upstream response instead of streaming it. |
| `CHAT_ISSUES_TOKEN` | To enable issue reports | — | Fine-grained PAT, Issues read & write on the one repo. Without it `/api/github/issue` answers `503`. |
| `CHAT_ISSUES_REPOSITORY` | No | `bash-365/bash-365.com` | `owner/repo` the reports are filed on. |
| `CHAT_ISSUES_LABELS` | No | `bug,documentation,enhancement,question` | Labels the model may pick; `from-chat` is always added. |
| `ISSUE_RATE_LIMIT_MAX` / `ISSUE_RATE_LIMIT_WINDOW_MS` | No | `3` / `600000` | Issues per window per IP, and window length. |

### Activating the chat widget

1. **GitHub Actions secret** — `CLAUDE_CODE_OAUTH_TOKEN` (preferred; `claude setup-token`) **or** `ANTHROPIC_API_KEY`. The production deploy job fails closed if neither is set. After OIDC login it runs `az staticwebapp appsettings set` so the value never lives in Bicep or the repo.
2. **Site config** — `_config.azure.yml` already sets `ai_chat.proxy_ready: true`. Leave `_config.yml` at `false` so GitHub Pages rollback does not show the widget.
3. **Issue reports (optional)** — add the `CHAT_ISSUES_TOKEN` Actions secret (see above). Without it the chat still works; reports fall back to "email us".

DNS rollback: point `bash-365.com` back at GitHub Pages. Do not flip `proxy_ready` in `_config.yml`.

Note on the API runtime: SWA picks the managed-functions Node.js version from `platform.apiRuntime` in `staticwebapp.config.json` (in the app source folder). The function uses the Node v4 programming model, which requires Node 18 or newer — the config file should set `"platform": { "apiRuntime": "node:20" }`.

## Workflow: Build & validate

File: `.github/workflows/build-validate.yml`

Runs on every push to `main` and on pull requests (with `paths-ignore: extension/**`). It is the quality gate in front of deploy. `.github/workflows/azure-swa.yml` also rebuilds the Azure stack before `swa deploy`. Three jobs:

- **build-pages** — builds the production GitHub Pages stack (`github-pages`
gem + `remote_theme: bamr87/zer0-mistakes@v1.26.0`, `_config.yml` only, `--safe`) in a `ruby:3.3` container, proving the Pages build stays green.
- **build-azure** — builds the Azure stack (`BUNDLE_GEMFILE=Gemfile.azure`,
`jekyll-theme-zer0 ~> 1.26.0`, `--config _config.yml,_config.azure.yml`), proving the SWA deploy will succeed.
- **content-lint** — runs `python3 scripts/content_lint.py` to enforce the
editorial contract (frontmatter completeness, description length, banned-phrase scan, `draft: true` blocker, filename/date match).

Gems are cached between runs; no deploy steps. If any job fails, the PR is blocked (once these checks are made required in branch protection).

## Workflow: Azure Static Web Apps

File: `.github/workflows/azure-swa.yml`

Provisions nothing. Infra is Bicep + `az` in `infra/azure/`. The workflow authenticates with GitHub OIDC (`azure/login@v2`), builds Jekyll in `ruby:3.3` with `Gemfile.azure` + `_config.yml,_config.azure.yml`, then deploys the prebuilt `_site` and `api/` with the SWA CLI. It fetches the SWA API key at deploy time (`az staticwebapp secrets list`) — no stored `AZURE_STATIC_WEB_APPS_API_TOKEN`, no Oryx.

| GitHub secret | Purpose |
| --- | --- |
| `AZURE_CLIENT_ID` | Entra app from `./infra/azure/bootstrap.sh`. Deploy is skipped when unset. |
| `AZURE_TENANT_ID` | Same. |
| `AZURE_SUBSCRIPTION_ID` | Same. |
| `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` | Chat credential. Production deploy fails if both are missing. |
| `CHAT_ISSUES_TOKEN` | Optional. Lets the chat file visitor reports as issues. The deploy logs a notice when it is unset. |

Optional repository variables: `AZURE_RESOURCE_GROUP` (default `rg-bash365-prod`), `AZURE_STATIC_WEB_APP_NAME` (default `swa-bash365-prod`).

PRs deploy to a staging environment named `pr<number>` (Free SKU has three slots; closing the PR deletes it). Staging may 503 on `/api/chat`; that is acceptable.

### One-time bootstrap and DNS cutover

Production deploys from **`bash-365/bash-365.com`** (moved from `bamr87/bashconsultants` on 2026-10-12). The Entra app `sp-bash365-swa-github` trusts this repo through two federated credentials, `bash-365-main` and `bash-365-pull-request`. This repo uses GitHub's **immutable OIDC subjects**, so the subjects are `repo:bash-365@337864329/bash-365.com@504711227:ref:refs/heads/main` and `…:pull_request`, not `repo:bash-365/bash-365.com:…`. A credential with the plain form fails login with `AADSTS700213`. `gh api repos/bash-365/bash-365.com/actions/oidc/customization/sub` prints the exact prefix.

1. `az login` then `./infra/azure/bootstrap.sh` — resource group, Entra app + federated credentials (subject prefix read from the GitHub API above; existing credentials are matched by subject, so a re-run is safe), Contributor on the RG, Bicep SWA **without** a GitHub `repositoryUrl`.
2. Paste the printed IDs into GitHub secrets; add the chat credential.
3. Merge/push so `azure-swa.yml` deploys to the default hostname. Smoke `GET /`, `/404.html`, `/search/`, `/contact/`, and `POST /api/chat` with that origin — expect not 503.
4. `./infra/azure/cutover.sh` attaches `www.bash-365.com` then `bash-365.com`. Apply **exactly** the TXT/CNAME/ALIAS records Azure prints. Do not guess IPs. Do not attach `bashconsultants.com`.
5. Rollback = revert DNS to GitHub Pages. Leave Pages enabled.

Phase 2 (not in this change): Terraform/OpenTofu Azure parity in `infra/terraform/`. Do not apply Bicep and Terraform to the same RG.

## Workflow: Site health (nightly)

File: `.github/workflows/site-health.yml` Schedule: `17 9 * * *` UTC (roughly 2–3 AM Denver), plus manual dispatch.

Steps, all with the built-in `GITHUB_TOKEN` — no extra secrets needed:

1. **Smoke build** — builds the site with the github-pages gem and
`remote_theme`, the same stack production GitHub Pages uses. A CI-only Gemfile is generated in the run because the repo's `Gemfile` carries a local-path theme gem meant for Docker development.
2. **Content lint** — runs `scripts/content_lint.py --warn-only` when the
   script exists; otherwise prints a notice and moves on.
3. **Link check** — runs `htmlproofer` against the built `_site`, internal
links only (`--disable-external`). Ignores `/api/` URLs (those only resolve on the SWA host), the theme-emitted `/tags/…`, `/archives/…`, and bare `#<tag>` anchor links (the site publishes no tag/archive index pages yet), and the published `CLAUDE`/`AGENTS` agent-context pages (their relative repo-file links are not site URLs).
4. **On failure** — writes an error annotation and a step summary describing
the failure. Issues are disabled on this repository, so no issue is filed; check the Actions tab (or the failure notification email) for red nightly runs.

## Workflow: Content gardener (weekly)

File: `.github/workflows/content-gardener.yml` Schedule: `23 14 * * 1` UTC (Mondays, morning in Denver), plus manual dispatch with an optional topic override.

Uses `anthropics/claude-code-action@v1` to draft **one** new blog post per week and open a pull request — it never pushes to `main`. The prompt requires it to:

- read `.github/instructions/content-style.instructions.md`,
`.github/instructions/posts.instructions.md`, and `.github/prompts/article-write.prompt.md` first;
- pick an uncovered topic from `_data/taxonomy.yml` (falling back to the
service catalog in `_data/entity/services.yml`) and the existing post list under `pages/_posts/`;
- write a single file into `drafts/` with `draft: true` and standards-compliant
  frontmatter;
- open a PR titled `content(posts): weekly draft — <topic>` whose body
includes the reviewer's promotion checklist (move to `pages/_posts/<subfolder>/`, flip `draft:` to `false`, confirm or regenerate the preview image).

### Activating the gardener

Two switches, both human-set. First the **kill switch**: the schedule idles until the repository **variable** `CONTENT_GARDENER_ENABLED` is `true` (`gh variable set CONTENT_GARDENER_ENABLED --body true`). The bot token cannot set variables, so the gardener can never enable itself, and flipping the variable back stops it without editing the workflow. A manual `workflow_dispatch` run bypasses the variable — a human pressed the button. Then the **credential**: add a `CLAUDE_CODE_OAUTH_TOKEN` repository secret (preferred — `claude setup-token`) **or** an `ANTHROPIC_API_KEY` repository secret (repo → Settings → Secrets and variables → Actions). When both are set, only the OAuth token is passed to `claude-code-action` — the workflow blanks the API-key input by expression, because the action does not reliably prefer OAuth on its own — so the API key is never billed while the subscription token exists. Without either credential, the workflow logs a notice and skips — scheduled runs never fail red just because the credential is absent. These are separate from the Azure application settings above; they can be different credentials with different spend caps.

When the content loop is enabled (`CONTENT_LOOP_ENABLED=true`), the gardener's schedule stands down and only manual runs proceed — see [`content-loop.md`](./content-loop.md).

Optional: add a `GARDENER_GITHUB_TOKEN` secret — a fine-grained personal access token with Contents and Pull requests read/write on this repo. Pull requests opened with the default `GITHUB_TOKEN` can't trigger other workflows, so the SWA staging build only runs on gardener PRs when this token is set (or after any human push to the PR branch). Review still works fine without it; you just review the markdown instead of a staged preview.

## Workflow: LinkedIn publishing

Publishes to the BASH LinkedIn **company page** (`urn:li:organization:64517157`) the same way the gardener drafts posts: **agents draft, a human approves, the lane posts.** It handles link shares of blog posts and standalone text updates. Native long-form LinkedIn Articles are not API-publishable — "article" here means a link-share card.

**The engine is zer0-CMS, not this repository.** The site plugs into zer0-CMS's distribution lane: one stdlib Ruby pipeline behind the `zer0-cms linkedin` CLI, a reusable workflow, an MCP server and the fleet CMS's `/admin/distribution` screen. Its design of record — every gate, and the complete list of LinkedIn calls it can make — is zer0-CMS [`docs/DISTRIBUTION.md`](https://github.com/bamr87/zer0-CMS/blob/main/docs/DISTRIBUTION.md). This site supplies only settings, in `zer0.json` → `distribution.linkedin`: the page's URN, the `drafts/linkedin/` queue, the `.github/linkedin-log.json` ledger, `acceptStatuses: ["pending", "approved"]` (a merge is the approval: the workflow on `main` runs with `ZER0_LINKEDIN_MERGED=1`, and anywhere else a draft must be `approved`), `sources: ["posts"]`, and the `office.jpg` fallback card. The lane maps a post to the Posts API payload with its commentary escaped for LinkedIn, uploads the post's `preview` image as the card thumbnail, posts, and records the returned URN under the post's canonical URL so a page is never posted twice. `zer0-cms linkedin preview` renders the exact request, the brand guard and every gate with no network call. With zer0-CMS checked out beside this repository: `ruby ../zer0-CMS/rails/bin/zer0-cms linkedin status --site .`.

**The governed flow.** `/linkedin-draft <post|text>` (the `.claude/commands/linkedin-draft.md` command + the `linkedin-share` skill) scaffolds a draft with `zer0-cms linkedin draft`, writes on-brand commentary into `drafts/linkedin/<date>-<slug>.md` at `status: pending`, and opens a PR. A human edits and **merges** it — the merge is the approval.

Files:

- `.github/workflows/linkedin-publish.yml` — a caller of zer0-CMS's `zer0-linkedin.yml`. On push to `main` under `drafts/linkedin/**` (a merged draft) it publishes the queue live; `workflow_dispatch` rehearses the queue or one draft and publishes only when `live` is ticked. It commits the ledger and the draft's `published` status back with `[skip ci]`. There is no free-text or post-by-reference input: every share is a draft a person merged.
- `.github/workflows/linkedin-token-health.yml` — weekly; the same workflow's `status` command introspects the token (when the app credentials are secrets) or proves it with a cheap read, and fails the run when the token is rejected or within 7 days of expiry (Issues are disabled on this repository, so the failed run and its summary are the alert).
- `.mcp.json` — the `zer0-linkedin` MCP server (`zer0-cms linkedin mcp`): status, sources, queue, preview and draft for Claude Code. Its publish tool stays off unless the operator starts it with `ZER0_LINKEDIN_MCP_PUBLISH=1` and `ZER0_LINKEDIN_PUBLISH=1`.
- `.github/linkedin-log.json` — the ledger, including the 2026-07-30 QuickBooks share.

### Activating LinkedIn publishing

The LinkedIn app needs Community Management API access — for the page, `w_organization_social`, `r_organization_social`, and `rw_organization_admin` for the page-role check and statistics. The application answers are [`linkedin-api-application.md`](./linkedin-api-application.md). zer0-CMS's `zer0-linkedin.yml` must be on its `main` first, since both workflows call it there. Then:

1. Get a token as a page admin — `ruby ../zer0-CMS/rails/bin/zer0-cms linkedin connect --site . --print-token` (needs `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET` in the environment and `http://127.0.0.1:8765/callback` registered on the app), or LinkedIn's [token generator](https://www.linkedin.com/developers/tools/oauth/token-generator) — and add repo **secrets** (Settings → Secrets and variables → Actions): `LINKEDIN_ACCESS_TOKEN`, optionally `LINKEDIN_CLIENT_ID` + `LINKEDIN_CLIENT_SECRET` (so token health reads the real expiry), and `LINKEDIN_REFRESH_TOKEN` only if LinkedIn enabled refresh for the app.
2. Settings live in `zer0.json`; there are no repository variables to set, and no file can arm a live publish — the workflow sets `ZER0_LINKEDIN_PUBLISH=1` for the publish step alone.
3. Without `LINKEDIN_ACCESS_TOKEN`, both workflows skip with a notice — scheduled runs never fail red just because the credential is absent.

**Token lifecycle.** Access tokens last 60 days. With a refresh token and the app credentials, the lane refreshes once on a 401; otherwise renew with `connect` or the token generator when the token-health workflow warns. The `Linkedin-Version` header expires when LinkedIn's twelve-month support window closes — set `apiVersion` in `zer0.json` (the lane defaults to `202608`); `zer0 doctor` warns two months ahead.

## Workflow: Content review (weekly)

File: `.github/workflows/content-review.yml` Schedule: `37 14 * * 4` UTC (Thursdays, morning in Denver), plus manual dispatch with optional `mode` (expand / new / auto) and `focus` inputs.

The content counterpart to the preacher. It adopts the content-curator charter (`.claude/agents/content-curator.md`) and moves the site's content forward by ONE unit each week: it reviews the corpus — starting from the deterministic `scripts/content_inventory.py --focus` shortlist of thin/stale pages — and opens a PR that either **expands** an existing article with more relevant, current information or **writes** a new article filling a real gap. It follows the same editorial authorities as the gardener, gates on `content_lint.py`, and never pushes to `main`.

This complements the **content gardener** (which only drafts brand-new posts): the gardener grows breadth, the curator reviews everything and chooses between depth and breadth. Activate it the same way: its kill switch is the `CONTENT_REVIEW_ENABLED` repository variable (`gh variable set CONTENT_REVIEW_ENABLED --body true`; manual dispatch bypasses it), plus a `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` secret (OAuth first — the key is passed only when the token is absent); optional `CONTENT_REVIEW_GITHUB_TOKEN`. While the content loop is enabled its schedule stands down (manual runs still work) — the loop's improve mode covers the same ground on a faster cadence.

## Workflow: Content loop (daily)

File: `.github/workflows/content-loop.yml` Schedule: `11 14 * * *` UTC (daily, morning in Denver), plus manual dispatch with `mode` (auto / new / improve), `section`, and `dry_run` inputs.

The activity-driven counterpart to the gardener and the curator, modeled on the lifehacker.dev autopilot. A deterministic planner (`scripts/loop/plan.py`) reads the loop's ledger (`_data/loop/runs/`) and decides one of three things each day: a **new** article is due (every other day), an **improvement** is due (the days between), or the loop should **idle** (nothing due, too many loop PRs awaiting review, or no unspent work to write about — always with the reason in the run summary). Ideas come from the practice's own work: `scripts/loop/signals.py` mines this repository's git history (grouping commits by the `Claude-Session:` trailer, by pull request, or by day; marking AI-assisted work by its `Co-Authored-By: Claude` trailer), the CHANGELOG, the committed AI-session trace (`_data/loop/sessions.jsonl`, fed by the `SessionEnd` hook), and, best-effort, the sister repositories in `_data/loop/sources.yml`. The writer (`.claude/agents/loop-writer.md`, following `.claude/skills/content-loop/SKILL.md`) turns one story into one on-voice piece in the most-overdue section, or expands the page that work made stale, gates it with the repo's scripts, records the run, and opens ONE pull request on a `loop/<run-id>` branch. It never pushes to `main`. Full design: [`content-loop.md`](./content-loop.md).

### Activating the loop

The schedule idles until the repository **variable** `CONTENT_LOOP_ENABLED` is `true` — the bot cannot set variables, so the loop cannot enable itself. It writes with the same credential as the other routines (`CLAUDE_CODE_OAUTH_TOKEN` preferred, `ANTHROPIC_API_KEY` fallback); without one it still plans, which makes a manual `dry_run` a free way to see what it would do. Optional: `CONTENT_LOOP_GITHUB_TOKEN` (a fine-grained PAT, probed for validity before use so an expired token degrades with a warning rather than failing the run), `OPENAI_API_KEY` (generates a new post's preview image on the PR branch), and the `CONTENT_LOOP_MODEL` variable (pins the writer's model). While the loop is enabled, the weekly **content gardener** and **content review** schedules stand down — their gates check the same variable — so the same topic is not drafted twice; both still run on manual dispatch.

## Workflow: PR to upstream (weekly)

File: `.github/workflows/pr-to-upstream.yml` Trigger: Mondays 15:00 UTC, plus manual dispatch. (Once the PR is open it tracks `main` and updates itself on every push, so a per-push trigger only re-confirmed a PR GitHub already keeps fresh — the weekly probe just re-opens it after a merge/close.)

Opens (and keeps) a pull request from this fork up to the repository it was forked from, `amr-bash/bash-365.com`. Idempotent — it won't duplicate an already-open PR and skips when upstream is already in sync — and safe: it skips cleanly when the `UPSTREAM_PR_TOKEN` secret is absent (the default `GITHUB_TOKEN` can't open cross-repo PRs). Add a fine-grained PAT with Pull requests + Contents on the upstream repo as `UPSTREAM_PR_TOKEN` to activate.

## Workflow: The preacher (weekly)

File: `.github/workflows/preacher.yml` Schedule: `42 14 * * 6` UTC (Saturdays, morning in Denver), plus manual dispatch with an optional `focus` lens.

The reflexive "practice what we preach" enforcer. It runs the deterministic gates (`scripts/doctrine_check.py`, `scripts/content_lint.py`) first, then does an AI judgment pass against the canon, and either opens ONE findings PR listing doctrine violations (Mode A — Issues are disabled on this repository, so the channel is a PR) or — when the repo is clean — mechanizes one recurring AI-review burden into a new check in `doctrine_check.py` and opens a PR (Mode B). It never pushes to `main`. Full canon and design: [`the-preacher.md`](./the-preacher.md). Activate it the same way as the gardener: its kill switch is the `PREACHER_ENABLED` repository variable (`gh variable set PREACHER_ENABLED --body true`; manual dispatch bypasses it), plus a `CLAUDE_CODE_OAUTH_TOKEN` or `ANTHROPIC_API_KEY` secret (OAuth first — the key is passed only when the token is absent); optional `PREACHER_GITHUB_TOKEN`.

## Cost and safety notes

- Both Anthropic credentials should be workspace-scoped keys with spend caps
  set in the Anthropic console.
- Every scheduled AI lane is OFF until a human sets its repository variable —
`CONTENT_LOOP_ENABLED`, `CONTENT_GARDENER_ENABLED`, `CONTENT_REVIEW_ENABLED`, `PREACHER_ENABLED` — and is stopped the same way, without editing a workflow (`gh variable set <NAME> --body false`). Manual `workflow_dispatch` runs bypass the variable. `fleet.manifest.yml` at the repo root inventories the lanes, their switches, and the tokens they use.
- The agents' shared guardrails — untrusted-input quarantine, the honesty rule,
  merge discipline — live in `.claude/skills/_shared/quarantine.md`.
- The chat function enforces model, token, origin, body-size, and rate
  limits server-side; a modified client can't raise them.
- The issue function holds the only GitHub credential the site uses, scoped to
issues on one repo. The origin check stops other websites, not scripts (a script can forge `Origin`), so the per-IP limit and the `from-chat` label are what keep spam manageable. If spam arrives, remove the token and the chat falls back to email.
- The gardener writes only to `drafts/` on a new branch, and the preacher only
opens PRs — neither ever pushes to `main`; a human merges or closes every PR. The site-health workflow has read-only repo access.
- Scheduled workflows run only from the default branch, so changes to them
  take effect after merge to `main`.
