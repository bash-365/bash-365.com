/**
 * ===================================================================
 * bash-365.com chat issue reporter — Azure Static Web Apps managed function
 * ===================================================================
 *
 * File: api/src/functions/github.js
 * Routes: POST /api/github/issue
 *         POST /api/github/pull-request  (always refused — see below)
 *
 * Server-side companion for the zer0-mistakes chat widget's GitHub "proxy"
 * mode (ai_chat.github.mode: 'proxy' in _config.yml). When a visitor reports a
 * problem in the chat, the widget shows a confirmation card and then POSTs the
 * issue here; this function files it on the site repository with a server-held
 * token, so visitors need no GitHub account — the widget's 'url' mode sends
 * them to a github.com form instead, which requires signing in.
 *
 * Ported from the theme's Cloudflare Worker reference implementation
 * (templates/deploy/chat-proxy/worker.js, handleIssue) with these changes:
 *   - Labels are limited to an allowlist; anything else the model proposes
 *     is dropped, and `from-chat` is always applied for triage.
 *   - @-mentions in visitor text are defused so a report cannot ping people.
 *   - A provenance footer marks the issue as visitor-supplied and records the
 *     page it came from (the Referer, when it is one of our own origins).
 *   - A stricter per-IP rate limit than chat.
 *   - The pull-request route is NOT ported. Anonymous visitors do not get
 *     write access to branches; the route answers 403 with a message telling
 *     the model to file an issue that quotes the suggested wording instead.
 *
 * Contract with the widget (assets/js/ai-chat.js, githubProxyPost):
 *   Request:  POST { title, body, labels? }
 *   Response: 201 { url, number }
 *   Errors:   { error: { message } } — the message is shown to the model as a
 *             tool error, so it is written for the model to relay.
 *
 * Application settings:
 *   CHAT_ISSUES_TOKEN       — REQUIRED to enable reporting. Fine-grained GitHub
 *                             PAT scoped to the one repository below with
 *                             Issues: read & write and nothing else. Never in
 *                             the repo, never echoed.
 *   CHAT_ISSUES_REPOSITORY  — owner/repo to file on (default bash-365/bash-365.com)
 *   CHAT_ISSUES_LABELS      — comma-separated label allowlist
 *                             (default bug,documentation,enhancement,question)
 *   ISSUE_RATE_LIMIT_MAX    — issues per window per IP (default 3)
 *   ISSUE_RATE_LIMIT_WINDOW_MS — window length in ms (default 600000)
 *   ALLOWED_ORIGINS, SWA_ORIGIN_PREFIX — origin allowlist; see ../lib/gate.js
 * ===================================================================
 */

'use strict';

const { app } = require('@azure/functions');
const {
  originAllowed,
  corsHeaders,
  jsonResponse,
  jsonError,
  clientIp,
  createRateLimiter,
  readJsonBody,
} = require('../lib/gate');

const GITHUB_API = 'https://api.github.com';
const DEFAULT_REPOSITORY = 'bash-365/bash-365.com';
const DEFAULT_LABELS = ['bug', 'documentation', 'enhancement', 'question'];
const PROVENANCE_LABEL = 'from-chat';
const MAX_TITLE_CHARS = 256;
const MAX_BODY_CHARS = 20_000;
const MAX_BODY_BYTES = 64 * 1024;
const DEFAULT_RATE_LIMIT_MAX = 3;
const DEFAULT_RATE_LIMIT_WINDOW_MS = 10 * 60_000;
const CONTACT_FALLBACK = 'email info@bash-365.com';

const rateLimited = createRateLimiter(() => ({
  max: Number(process.env.ISSUE_RATE_LIMIT_MAX) || DEFAULT_RATE_LIMIT_MAX,
  windowMs: Number(process.env.ISSUE_RATE_LIMIT_WINDOW_MS) || DEFAULT_RATE_LIMIT_WINDOW_MS,
}));

function repository() {
  return (process.env.CHAT_ISSUES_REPOSITORY || DEFAULT_REPOSITORY).trim();
}

function labelAllowlist() {
  const configured = (process.env.CHAT_ISSUES_LABELS || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
  return configured.length ? configured : DEFAULT_LABELS;
}

// Keep only allowlisted labels, deduplicated, and always tag the source.
function issueLabels(requested) {
  const allowed = new Set(labelAllowlist());
  const picked = (Array.isArray(requested) ? requested : [])
    .filter((label) => typeof label === 'string' && allowed.has(label));
  return Array.from(new Set([PROVENANCE_LABEL, ...picked]));
}

// A zero-width space after "@" stops GitHub from treating "@someone" or
// "@org/team" as a mention, so visitor text cannot notify arbitrary accounts.
function defuseMentions(text) {
  return text.replace(/(^|[^\w`])@(?=[A-Za-z0-9])/g, '$1@​');
}

// The page the visitor was on, when the browser reports one of our origins.
function sourcePage(request) {
  const referer = request.headers.get('referer') || '';
  try {
    const url = new URL(referer);
    return originAllowed(url.origin) ? url.origin + url.pathname : '';
  } catch (err) {
    return '';
  }
}

function provenanceFooter(page) {
  const lines = [
    '',
    '---',
    '_Filed by a site visitor through the chat assistant. The report above is visitor-supplied and unverified._',
  ];
  if (page) lines.push(`_Page: ${page}_`);
  return lines.join('\n');
}

async function createIssue(payload) {
  return fetch(`${GITHUB_API}/repos/${repository()}/issues`, {
    method: 'POST',
    headers: {
      authorization: `Bearer ${process.env.CHAT_ISSUES_TOKEN}`,
      accept: 'application/vnd.github+json',
      'x-github-api-version': '2022-11-28',
      'content-type': 'application/json',
      'user-agent': 'bash-365-chat-issues',
    },
    body: JSON.stringify(payload),
  });
}

// --- Handlers ------------------------------------------------------------

// Runs the checks both routes share. Returns { cors } to continue, or
// { response } to return immediately.
function gate(request) {
  const origin = request.headers.get('origin') || '';
  const cors = corsHeaders(origin);
  if (request.method === 'OPTIONS') return { response: { status: 204, headers: cors } };
  if (request.method !== 'POST') return { response: jsonError('Method not allowed', 405, cors) };
  if (!originAllowed(origin)) return { response: jsonError('Origin not allowed', 403, cors) };
  return { cors };
}

async function issueHandler(request, context) {
  const { cors, response } = gate(request);
  if (response) return response;

  if (!process.env.CHAT_ISSUES_TOKEN) {
    return jsonError(
      `Issue reporting is not set up on this site yet. Ask the visitor to ${CONTACT_FALLBACK} with the details instead.`,
      503,
      cors
    );
  }

  if (rateLimited(clientIp(request))) {
    return jsonError(
      `This visitor has filed several reports in the last few minutes. Ask them to wait a while, or to ${CONTACT_FALLBACK}.`,
      429,
      cors
    );
  }

  const { body, error } = await readJsonBody(request, MAX_BODY_BYTES, cors);
  if (error) return error;
  const title = body && typeof body.title === 'string' ? body.title.trim() : '';
  const text = body && typeof body.body === 'string' ? body.body.trim() : '';
  if (!title || !text) {
    return jsonError('title and body are required', 400, cors);
  }

  const payload = {
    title: defuseMentions(title).slice(0, MAX_TITLE_CHARS),
    body: defuseMentions(text).slice(0, MAX_BODY_CHARS) + '\n' + provenanceFooter(sourcePage(request)),
    labels: issueLabels(body.labels),
  };

  let upstream;
  try {
    upstream = await createIssue(payload);
    // 422 here is almost always a label the token cannot create; file the
    // report without labels rather than lose it.
    if (upstream.status === 422) {
      context.warn('GitHub rejected the issue labels; retrying without labels.');
      upstream = await createIssue({ ...payload, labels: [] });
    }
  } catch (err) {
    context.error('GitHub request failed:', err.message);
    return jsonError(`Could not reach GitHub. Ask the visitor to try again later or ${CONTACT_FALLBACK}.`, 502, cors);
  }

  const data = await upstream.json().catch(() => ({}));
  if (!upstream.ok) {
    // Log GitHub's reason for the operator; keep it out of the visitor's chat.
    context.error(`GitHub issue create failed (${upstream.status}):`, data.message || 'no message');
    return jsonError(`The report could not be filed. Ask the visitor to ${CONTACT_FALLBACK} instead.`, 502, cors);
  }

  return jsonResponse({ url: data.html_url, number: data.number }, 201, cors);
}

async function pullRequestHandler(request) {
  const { cors, response } = gate(request);
  if (response) return response;
  return jsonError(
    'Pull requests are not accepted from the site chat. Use create_github_issue instead and put the suggested wording in the issue body.',
    403,
    cors
  );
}

app.http('githubIssue', {
  methods: ['POST', 'OPTIONS'],
  authLevel: 'anonymous',
  route: 'github/issue',
  handler: issueHandler,
});

app.http('githubPullRequest', {
  methods: ['POST', 'OPTIONS'],
  authLevel: 'anonymous',
  route: 'github/pull-request',
  handler: pullRequestHandler,
});
