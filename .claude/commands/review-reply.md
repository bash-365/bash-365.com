---
description: Read a Google review of BASH and stage a reply in the BASH voice in zer0-CMS for a person to approve
argument-hint: "<review id | \"unanswered\">"
allowed-tools: Read, Glob, Grep, mcp__zer0-reputation
---

Draft a reply to a Google review of BASH Consulting following the **`google-review-reply`** skill, and stage it in zer0-CMS for approval. Target: `$ARGUMENTS`.

**Do this:**

1. Read the **`google-review-reply`** skill and apply the **`brand`** and **`content-editorial`** rules it points to. Confirm the `zer0-reputation` MCP server is connected (the skill's "Connecting"); if it is not, stop and say what is missing.
2. If the argument is a review id, read that review with `reputation.get_review`. If it is `unanswered`, ask the person which review — the studio's Reputation → Reviews with "Not replied to" lists them — rather than guessing.
3. Record the analysis with `reputation.record_analysis`.
4. Draft the reply to the skill's rules and propose it with `reputation.propose_reply`.
5. Report back: the review in one line, the analysis, the proposed text, any guard finding, and where the person approves it (Reputation → Reviews → the review).

Post nothing to Google from this command. A person approves the exact text in the studio, and only the platform's worker posts it. The final voice pass is done with Opus 4.8.
