---
name: reference-ai-vendor-claims
description: Source checks on AI/terminal-agent claims cited in bash-365.com tech posts — what the linked vendor pages actually say
metadata:
  type: reference
---

Claims in the `tech/` AI posts that were checked against their linked sources on 2026-09-07. Re-verify before reusing, but these are the traps that recurred.

**MIT Project NANDA (`nanda.media.mit.edu`, redirects to `media.mit.edu/groups/nanda/overview/`)** — the landing page itself carries **no** statistic about generative-AI pilot failure rates; it describes a research initiative on networked AI agents. The statistic lives in a report NANDA published, *The GenAI Divide: State of AI in Business 2025* (July 2025), which found the large majority of enterprise generative-AI pilots produced no measurable return. Cite the report by name when the claim needs a source, keep the wording to "the large majority" rather than a bare percentage unless the link goes to the report itself, and do not strip the citation just because the landing page no longer shows the number (the 2026-09-07 pass restored it in `tech/2025-08-12-ai-integration-reality.md` after an over-cautious cut).

**Codex CLI (`developers.openai.com/codex/cli`, redirects to `learn.chatgpt.com/docs/codex/cli`)** — the docs describe running "the tools already installed on your machine" with `/permissions` controls, and say you can "inspect the active sandbox and writable roots before you continue." They do **not** claim isolated execution that can install packages without touching the host. Write the permission-scope framing, not the isolation framing.

**Microsoft Intelligent Terminal (`devblogs.microsoft.com/commandline/announcing-intelligent-terminal-version-0-1/`, dated June 2, 2026)** — an open-source *experimental fork* of Windows Terminal, installed alongside the standard app. GitHub Copilot CLI is the default agent; it works with any agent speaking the open **Agent Client Protocol**. It was **not** announced at Build 2026, and the post does not name Claude, Codex, or Gemini.

**Links that resolve clean** (200 as of 2026-09-07): `docs.anthropic.com/en/docs/claude-code/overview`, `docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview`, `github.com/google-gemini/gemini-cli`, `arxiv.org/abs/2403.16971` (AIOS), `modelcontextprotocol.io/`, `nist.gov/itl/ai-risk-management-framework`. `code.visualstudio.com` and `hhs.gov` return 503/403 to automated fetches — bot-blocking, not dead links; don't remove them on that evidence alone.

**How to apply:** on any AI/agent post, open every vendor link before trusting the sentence attached to it. NIST AI RMF is the reliable primary source when a post needs one for AI governance/explainability.

See [[reference-post-standards]] and [[reference-content-style]].
