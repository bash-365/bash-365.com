# API — Azure Static Web Apps managed functions

This folder is the `--api-location` of `.github/workflows/azure-swa.yml`. The workflow deploys a prebuilt `_site` plus this app with the SWA CLI (no Oryx). Azure serves the functions under `/api/` on the same host as the site.

Infra lives in `infra/azure/` (`bootstrap.sh`, `main.bicep`). Do not revive `proud-pond-06dc10c1e`.

Two functions ship today. Both use the shared origin gate, error shape, body cap, and rate limiter in `src/lib/gate.js`.

| Route | File | Purpose |
| --- | --- | --- |
| `POST /api/chat` | `src/functions/chat.js` | Proxies the site's AI chat widget to the Anthropic Messages API. Auth is a Claude Code OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`, preferred) or an `ANTHROPIC_API_KEY` (fallback), held in an Azure application setting — never in the repo or the browser. SWA default/staging origins are allowed via `SWA_ORIGIN_PREFIX`, not a hardcoded app name. |
| `POST /api/github/issue` | `src/functions/github.js` | Files a visitor's problem report from the chat as an issue on `bash-365/bash-365.com`, using a fine-grained token (`CHAT_ISSUES_TOKEN`, Issues read & write on that repo only). Allowlists labels, always adds `from-chat`, defuses `@`-mentions, and records the source page. Answers `503` without the token. |
| `POST /api/github/pull-request` | `src/functions/github.js` | Always `403`. Visitors do not open pull requests; the message tells the model to file an issue instead. |

Full documentation — secrets, OIDC, cutover, rollback — lives in [`docs/automation.md`](../docs/automation.md).

## Local run (optional)

Requires Node 18+ and Azure Functions Core Tools v4:

```bash
cd api
npm install
cp local.settings.json.sample local.settings.json   # then set CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY (and CHAT_ISSUES_TOKEN to test reports)
func start
```

The functions listen on `http://localhost:7071/api/chat` and `http://localhost:7071/api/github/issue`. Note the theme also ships its own Node dev proxy for local chat testing; see `templates/deploy/chat-proxy/` in the zer0-mistakes theme repo.
