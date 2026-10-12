/**
 * ===================================================================
 * bash-365.com AI Chat Proxy — Azure Static Web Apps managed function
 * ===================================================================
 *
 * File: api/src/functions/chat.js
 * Route: POST /api/chat  (SWA prefixes managed-function routes with /api)
 *
 * Server-side companion for the zer0-mistakes theme chat widget
 * (theme files: _includes/components/ai-chat.html + assets/js/ai-chat.js).
 * Ported from the theme's Cloudflare Worker reference implementation at
 * templates/deploy/chat-proxy/worker.js — chat route. The widget's GitHub
 * issue route lives beside it in github.js.
 *
 * Contract with the widget (assets/js/ai-chat.js):
 *   Request:  POST { model, max_tokens, system, messages, tools?, stream: true }
 *   Response: Anthropic Messages API SSE stream passed through unchanged,
 *             or a plain JSON message object — the widget accepts both.
 *   Errors:   { error: { message } } with an HTTP status the widget maps
 *             to a friendly message.
 *
 * Auth (precedence, highest first — set exactly one credential as an Azure
 * Static Web App application setting; never in the repo, never echoed):
 *   1. CLAUDE_CODE_OAUTH_TOKEN — long-lived Claude Code OAuth token from
 *        `claude setup-token` (Claude Pro/Max). Sent as
 *        `Authorization: Bearer <token>` + `anthropic-beta: oauth-2025-04-20`.
 *        This is the DEFAULT: if it is set, it is used. OAuth (subscription)
 *        requests must identify as Claude Code, so the first system block is
 *        forced to the Claude Code identity (see chatHandler).
 *   2. ANTHROPIC_API_KEY — standard workspace `x-api-key`. The FALLBACK, used
 *        only when no OAuth token is set. Best for a public site with a
 *        spend-capped workspace key.
 * The worker's rotating-refresh OAuth mode is not ported — it needs a
 * key/value store (Cloudflare KV) that SWA managed functions don't provide;
 * use the long-lived setup-token instead.
 *
 * Hardening:
 *   - POST only (OPTIONS answered for preflight)
 *   - Origin allowlist (production domains + this SWA's own hostnames;
 *     shared with github.js in ../lib/gate.js)
 *   - Request body size cap
 *   - Server-side max_tokens cap and model pin
 *   - Simple fixed-window in-memory rate limit per client IP
 *
 * Optional application settings (all have safe defaults):
 *   CHAT_MODEL            — pin the model server-side (default claude-opus-4-8)
 *   MAX_TOKENS_CAP        — cap on client-requested max_tokens (default 4096)
 *   MAX_BODY_BYTES        — request body cap in bytes (default 524288)
 *   ALLOWED_ORIGINS,
 *   SWA_ORIGIN_PREFIX     — origin allowlist; see ../lib/gate.js
 *   RATE_LIMIT_MAX        — requests per window per IP (default 20)
 *   RATE_LIMIT_WINDOW_MS  — window length in ms (default 60000)
 *   CHAT_BUFFER_RESPONSE  — 'true' to buffer the upstream SSE body instead
 *                           of streaming it (fallback if the managed runtime
 *                           rejects HTTP streaming; the widget handles both)
 * ===================================================================
 */

'use strict';

const { app } = require('@azure/functions');
const {
  originAllowed,
  corsHeaders,
  jsonError,
  clientIp,
  createRateLimiter,
  readJsonBody,
} = require('../lib/gate');

// HTTP streaming requires Functions runtime >= 4.28 and @azure/functions >= 4.3,
// both standard on SWA managed functions with a node:18+ apiRuntime.
app.setup({ enableHttpStream: true });

const ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages';
const ANTHROPIC_VERSION = '2023-06-01';
const OAUTH_BETA = 'oauth-2025-04-20'; // required beta header for subscription OAuth
// Claude subscription OAuth requires the FIRST system block to identify as
// Claude Code, or the Messages API rejects the request with a misleading terse
// rate_limit_error. Prepended to the system prompt in OAuth mode only.
const CLAUDE_CODE_SYSTEM_PROMPT = "You are Claude Code, Anthropic's official CLI for Claude.";
const DEFAULT_MODEL = 'claude-opus-4-8'; // mirrors ai_chat.model in _config.yml
const DEFAULT_MAX_TOKENS = 1024;
const DEFAULT_MAX_TOKENS_CAP = 4096;
const DEFAULT_MAX_BODY_BYTES = 512 * 1024; // widget can attach ~48 KB page-source tool results
const DEFAULT_RATE_LIMIT_MAX = 20;
const DEFAULT_RATE_LIMIT_WINDOW_MS = 60_000;
const MAX_TOOLS = 16;

// --- Anthropic auth (Claude Code OAuth preferred, API key fallback) -------

// Precedence: OAuth token wins when both are set. Returns 'oauth' | 'api_key' | null.
function anthropicAuthMode() {
  if (process.env.CLAUDE_CODE_OAUTH_TOKEN) return 'oauth';
  if (process.env.ANTHROPIC_API_KEY) return 'api_key';
  return null;
}

// Auth + content headers for the upstream call. OAuth uses a Bearer token plus
// the oauth beta header; the API key uses x-api-key. Never logged or echoed.
function anthropicAuthHeaders(mode) {
  if (mode === 'oauth') {
    return {
      authorization: `Bearer ${process.env.CLAUDE_CODE_OAUTH_TOKEN}`,
      'anthropic-version': ANTHROPIC_VERSION,
      'anthropic-beta': OAUTH_BETA,
      'content-type': 'application/json',
    };
  }
  return {
    'x-api-key': process.env.ANTHROPIC_API_KEY,
    'anthropic-version': ANTHROPIC_VERSION,
    'content-type': 'application/json',
  };
}

const rateLimited = createRateLimiter(() => ({
  max: Number(process.env.RATE_LIMIT_MAX) || DEFAULT_RATE_LIMIT_MAX,
  windowMs: Number(process.env.RATE_LIMIT_WINDOW_MS) || DEFAULT_RATE_LIMIT_WINDOW_MS,
}));

// --- Handler -------------------------------------------------------------

async function chatHandler(request, context) {
  const origin = request.headers.get('origin') || '';
  const cors = corsHeaders(origin);

  if (request.method === 'OPTIONS') {
    return { status: 204, headers: cors };
  }
  if (request.method !== 'POST') {
    return jsonError('Method not allowed', 405, cors);
  }
  if (!originAllowed(origin)) {
    return jsonError('Origin not allowed', 403, cors);
  }

  const authMode = anthropicAuthMode();
  if (!authMode) {
    // Neither credential is set. proxy_ready should stay false in _config.yml
    // until CLAUDE_CODE_OAUTH_TOKEN (preferred) or ANTHROPIC_API_KEY is set.
    return jsonError('Chat is not configured on this deployment', 503, cors);
  }

  if (rateLimited(clientIp(request))) {
    return jsonError('Too many requests — please wait a minute and try again', 429, cors);
  }

  const maxBodyBytes = Number(process.env.MAX_BODY_BYTES) || DEFAULT_MAX_BODY_BYTES;
  const { body, error } = await readJsonBody(request, maxBodyBytes, cors);
  if (error) return error;
  if (!body || !Array.isArray(body.messages) || body.messages.length === 0) {
    return jsonError('Invalid request body', 400, cors);
  }

  const cap = Number(process.env.MAX_TOKENS_CAP) || DEFAULT_MAX_TOKENS_CAP;

  // In OAuth mode the first system block must be the Claude Code identity, or
  // Anthropic rejects the request. Keep the site assistant's own instructions
  // as a following block. API-key mode (standard billing) doesn't need this.
  const userSystem = typeof body.system === 'string' ? body.system : undefined;
  let system = userSystem;
  if (authMode === 'oauth') {
    system = [{ type: 'text', text: CLAUDE_CODE_SYSTEM_PROMPT }];
    if (userSystem) system.push({ type: 'text', text: userSystem });
  }

  const payload = {
    // Model is pinned server-side (CHAT_MODEL app setting, else DEFAULT_MODEL) —
    // the client's body.model is ignored so a tampered request cannot select a
    // more expensive model and run up spend.
    model: process.env.CHAT_MODEL || DEFAULT_MODEL,
    max_tokens: Math.min(Number(body.max_tokens) || DEFAULT_MAX_TOKENS, cap),
    system,
    messages: body.messages,
    tools: Array.isArray(body.tools) ? body.tools.slice(0, MAX_TOOLS) : undefined,
    stream: true,
  };

  let upstream;
  try {
    upstream = await fetch(ANTHROPIC_URL, {
      method: 'POST',
      headers: anthropicAuthHeaders(authMode),
      body: JSON.stringify(payload),
    });
  } catch (err) {
    context.error('Upstream request to Anthropic failed:', err.message);
    return jsonError('Upstream request failed', 502, cors);
  }

  const responseHeaders = {
    'content-type': upstream.headers.get('content-type') || 'application/json',
    'cache-control': 'no-store',
    ...cors,
  };

  // Stream the SSE body straight through (error bodies pass through as JSON).
  // CHAT_BUFFER_RESPONSE=true buffers instead — the widget parses a complete
  // SSE payload the same way, just without incremental rendering.
  if (process.env.CHAT_BUFFER_RESPONSE === 'true' || !upstream.body) {
    return { status: upstream.status, headers: responseHeaders, body: await upstream.text() };
  }
  return { status: upstream.status, headers: responseHeaders, body: upstream.body };
}

app.http('chat', {
  methods: ['POST', 'OPTIONS'],
  authLevel: 'anonymous',
  route: 'chat',
  handler: chatHandler,
});
