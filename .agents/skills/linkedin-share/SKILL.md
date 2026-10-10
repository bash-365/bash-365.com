---
name: linkedin-share
description: Draft on-brand LinkedIn company-page commentary for a blog post or a standalone update, and stage it for human approval. Use when composing anything that will publish to the BASH company page through zer0-CMS's distribution lane (zer0-cms linkedin).
---

# LinkedIn share drafting

The governed way to write copy for the BASH Consulting company page (`urn:li:organization:64517157`). The publisher — zer0-CMS's distribution lane, run here as `zer0-cms linkedin` and by `.github/workflows/linkedin-publish.yml` — is mechanical; **the judgment is here.** Agents draft, a human approves by merging the draft, and only then does it post: the same rules-in-files, humans-approve model the site sells. Follow this in order.

## Sources of truth (read, don't restate)

- **Brand / identity:** [`.github/instructions/brand.instructions.md`](../../../.github/instructions/brand.instructions.md)
- **Voice + mechanics:** [`.github/instructions/content-style.instructions.md`](../../../.github/instructions/content-style.instructions.md)
- **Section voice profiles:** [`_data/taxonomy.yml`](../../../_data/taxonomy.yml) — corp / erp / muses / tech
- **The queue:** [`drafts/linkedin/README.md`](../../../drafts/linkedin/README.md); settings in [`zer0.json`](../../../zer0.json) → `distribution.linkedin`
- **The lane, its gates and the call surface:** zer0-CMS [`docs/DISTRIBUTION.md`](https://github.com/bamr87/zer0-CMS/blob/main/docs/DISTRIBUTION.md)

The commands below assume zer0-CMS is checked out beside this repository (`../zer0-CMS`, the fleet layout). The lane is stdlib Ruby 3.3+ and needs no bundle.

## What LinkedIn adds on top of the house style

Everything in `content-editorial` still applies (no banned phrases, acronyms expanded on first use, enact-don't-announce, no invented metrics/clients/certs, US English, no exclamation marks). LinkedIn-specific rules:

- **Commentary is the hook above the card, not the card.** For an article share the card already shows the post title and description — do **not** restate the description. Write 2–4 sentences that give someone a reason to click.
- **Front-load the first ~140 characters.** LinkedIn truncates with "…see more"; the payoff must land before the fold. The preview prints exactly where the fold falls.
- **Length:** hard max 3,000 characters as sent; aim for ~600–1,200. Shorter reads better.
- **Exactly one call to action**, pointing at the reader's next step. For an article the card is the link, so the CTA is a soft "read it / here's why it matters," never a second URL dump.
- **2–3 hashtags**, CamelCase, business-relevant (`#SmallBusiness #ERP #AI`). No hashtag walls. Acronym tags stay upper-case.
- **Voice matches the post's section** (see `taxonomy.yml`): corp = owner/CFO register, erp = back-office wry, muses = essayistic, tech = practitioner.
- **Never invent.** Describe categories of work and what frameworks require; never claim BASH is certified, and never fabricate a result or client.
- **Write plain text.** Parentheses, brackets, asterisks and underscores are fine — the lane escapes them to LinkedIn's text format. A hashtag stays a hashtag. Do not hand-write LinkedIn's escape syntax.

## Procedure

1. **Resolve the target.** For an article, load the post under `pages/_posts/<section>/` and note its `title`, `description`, `sub-title`, `tags` and section. For a standalone update, take the topic from the caller.
2. **Scaffold the draft** (article), which writes `drafts/linkedin/YYYY-MM-DD-<slug>.md` at `status: pending` with a deterministic placeholder body and refuses a post that was already shared:
   ```bash
   ruby ../zer0-CMS/rails/bin/zer0-cms linkedin draft <section/YYYY-MM-DD-slug> --site .
   ```
   For an update, write the file by hand (`type: update`, `status: pending`, the text as the body).
3. **Write the commentary** into the draft's body to the rules above, in the section's voice, replacing the placeholder. The front matter is:
   ```
   ---
   type: article                                   # or: update
   status: pending                                 # never publish until a human merges it
   source: pages/_posts/<section>/<file>.md        # article only
   title: "<post title>"                           # informational, for the reviewer
   url: <canonical URL>                            # informational
   ---
   <the commentary — this body is exactly what posts to LinkedIn>
   ```
4. **Preview it** — the exact request, the mechanical brand guard, the fold, and every gate, with no network call:
   ```bash
   ruby ../zer0-CMS/rails/bin/zer0-cms linkedin preview <draft-id> --site .
   ```
   Fix every `ERROR`; `preview` exits non-zero while one remains. On a clean pending draft the gates left are `status_not_accepted` (here, the merge: CI on `main` publishes a merged pending draft), `publish_disabled` and `no_credential`. None of the three is yours to lift.
5. **Hand off for approval.** The draft sits at `status: pending` in a pull request. A human edits and **merges** it; `linkedin-publish.yml` posts it and sets it to `published`. Do not post from this skill, and never set `ZER0_LINKEDIN_PUBLISH`.

## Guardrails

- A draft never becomes a live post without a human merge; `status` is the record.
- The mechanical guard is a floor, not the ceiling — it can't see voice, an invented claim, or a second CTA. Read the draft as the reviewer will.
- The final voice pass on anything customer-facing is done with Opus 4.8.
