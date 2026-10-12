/**
 * Shared request gate for the SWA managed functions in api/src/functions/.
 *
 * Every public route spends a server-held credential (the Anthropic token for
 * /api/chat, the GitHub token for /api/github/*), so each one runs the same
 * checks: an origin allowlist, CORS headers, JSON error bodies the theme's
 * chat widget understands, and a per-IP fixed-window rate limit.
 *
 * Environment (all optional):
 *   ALLOWED_ORIGINS    — comma-separated extra allowed origins
 *   SWA_ORIGIN_PREFIX  — hostname stem of this SWA, with or without https://.
 *                        Allows this app's default and PR-staging hosts
 *                        (*.azurestaticapps.net). Never hardcode a previous
 *                        app name.
 */

'use strict';

// Production origins plus this Static Web App's own default and staging
// hostnames (staging environments look like <name>-<pr>.<region>.azurestaticapps.net).
const STATIC_ALLOWED_ORIGINS = [
  'https://bash-365.com',
  'https://www.bash-365.com',
  'https://bashconsultants.com',
  'https://www.bashconsultants.com',
];
const SWA_ORIGIN_SUFFIX = '.azurestaticapps.net';

function swaOriginPrefix() {
  const raw = (process.env.SWA_ORIGIN_PREFIX || '').trim();
  if (!raw) return '';
  return raw.startsWith('https://') ? raw : `https://${raw}`;
}

// --- CORS / origin gate ------------------------------------------------

function allowedOrigins() {
  const extra = (process.env.ALLOWED_ORIGINS || '')
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
  return STATIC_ALLOWED_ORIGINS.concat(extra);
}

function originAllowed(origin) {
  // Browsers always send Origin on POST; a missing Origin means a
  // non-browser client, which has no business spending a server credential.
  if (!origin) return false;
  if (allowedOrigins().includes(origin)) return true;
  const prefix = swaOriginPrefix();
  return Boolean(prefix) && origin.startsWith(prefix) && origin.endsWith(SWA_ORIGIN_SUFFIX);
}

function corsHeaders(origin) {
  const headers = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'content-type',
    'Access-Control-Max-Age': '86400',
  };
  if (origin && originAllowed(origin)) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Vary'] = 'Origin';
  }
  return headers;
}

function jsonResponse(payload, status, cors) {
  return {
    status,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store', ...cors },
    body: JSON.stringify(payload),
  };
}

function jsonError(message, status, cors) {
  return jsonResponse({ error: { message } }, status, cors);
}

// --- Rate limit (fixed window, per instance, per IP) ---------------------

function clientIp(request) {
  const forwarded = request.headers.get('x-forwarded-for') || '';
  // Key on the LAST hop, not the first. On Azure Static Web Apps / App Service
  // the trusted front end APPENDS the real client IP to whatever the caller sent,
  // so the first comma-separated entry is attacker-controlled (a client can spoof
  // it to dodge or poison the per-IP limit). The last entry is the value the
  // trusted proxy added.
  const parts = forwarded.split(',');
  let ip = parts[parts.length - 1].trim();
  if (ip.startsWith('[')) {
    // bracketed IPv6 with port: [::1]:12345
    ip = ip.slice(1, ip.indexOf(']') > 0 ? ip.indexOf(']') : undefined);
  } else if ((ip.match(/:/g) || []).length === 1) {
    // IPv4 with port: 203.0.113.7:54321
    ip = ip.split(':')[0];
  }
  return ip || 'unknown';
}

// Returns `limited(ip) -> boolean`. Each route gets its own buckets so a burst
// of chat turns does not use up a visitor's issue allowance, or vice versa.
// `limits()` is read per call so app-setting changes apply without a redeploy.
function createRateLimiter(limits) {
  const buckets = new Map(); // ip -> { windowStart, count }

  return function rateLimited(ip) {
    const { max, windowMs } = limits();
    const now = Date.now();

    // Opportunistic sweep so the map cannot grow without bound.
    if (buckets.size > 5000) {
      for (const [key, bucket] of buckets) {
        if (now - bucket.windowStart > windowMs) buckets.delete(key);
      }
    }

    const bucket = buckets.get(ip);
    if (!bucket || now - bucket.windowStart > windowMs) {
      buckets.set(ip, { windowStart: now, count: 1 });
      return false;
    }
    bucket.count += 1;
    return bucket.count > max;
  };
}

// --- Body ----------------------------------------------------------------

// Reads and parses a JSON body under a byte cap. Returns { body } on success
// or { error } holding a ready-to-return response.
async function readJsonBody(request, maxBytes, cors) {
  const declaredLength = Number(request.headers.get('content-length'));
  if (declaredLength && declaredLength > maxBytes) {
    return { error: jsonError('Request body too large', 413, cors) };
  }
  let raw;
  try {
    raw = await request.text();
  } catch (err) {
    return { error: jsonError('Invalid request body', 400, cors) };
  }
  if (Buffer.byteLength(raw, 'utf8') > maxBytes) {
    return { error: jsonError('Request body too large', 413, cors) };
  }
  try {
    return { body: JSON.parse(raw) };
  } catch (err) {
    return { error: jsonError('Invalid request body', 400, cors) };
  }
}

module.exports = {
  originAllowed,
  corsHeaders,
  jsonResponse,
  jsonError,
  clientIp,
  createRateLimiter,
  readJsonBody,
};
