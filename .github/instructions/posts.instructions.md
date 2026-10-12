---
applyTo: "pages/_posts/**/*.md"
description: "Blog post standards for bash-365.com — frontmatter, voice, and SEO rules for the _posts collection"
date: 2026-05-18T12:00:00.000Z
lastmod: 2026-07-06T12:00:00.000Z
---

# Blog Post Instructions

Posts live in `pages/_posts/` and are organized by subfolder (`corp/`, `erp/`, `muses/`, `tech/`). They render via the `article` or `news` layout.

> **Voice, audience, banned phrases, and universal checklist** → see [`content-style.instructions.md`](content-style.instructions.md). This file covers post-specific rules only.

## Subfolder routing

| Subfolder | Topic | Typical reader |
|---|---|---|
| `corp/` | Corporate IT, governance, vendor strategy | SMB owner / CFO |
| `erp/` | ERP, financial systems, QuickBooks-to-X migrations | Controller, operations manager |
| `muses/` | Opinion, industry commentary, longer-form | Mixed |
| `tech/` | How-tos, vendor walk-throughs, architecture notes | In-house IT lead |

If a post doesn't fit, default to `tech/` and revisit at next site audit.

## Categories and section voice

The canonical taxonomy lives in [`_data/taxonomy.yml`](../../_data/taxonomy.yml) — category slugs, section URLs, voice profiles, and tag conventions. Summary:

- **One primary category per post**, and it must equal the subfolder: `corp`, `erp`, `muses`, or `tech`.
- **`ai` is the only sanctioned secondary category.** Add it when the post's main subject is artificial intelligence (`categories: [tech, ai]`). Never use a second primary — `[erp, tech]` is invalid.
- **Lowercase flow-style lists only**: `categories: [tech, ai]`, never block lists, never capitalized values.

Each section has a voice profile. Match it, don't average them:

- **corp** — sharp and strategic, for owners and CFOs. Lead with the number or the risk, close with a decision the reader can make this quarter. Minimal humor.
- **erp** — performed comedy with a real business lesson underneath. The device is enacted, never labeled: no reader-facing text calls a piece a "parody", "satire", "sketch", or "musical number" — in-fiction framing (a narrator, a host, an episode title) is the enactment and is fine. Every piece lands a concrete lesson for whoever signs the checks.
- **muses** — reflective, essayistic, lightly witty. Longer-form thinking that still ends pointed at something the reader can do.
- **tech** — crisp, actionable how-to. Concrete steps, honest ranges, named watch-outs, acronyms expanded on first use.

## Required frontmatter

```yaml
---
title: "Sentence-case title, no trailing period"
description: "120–155 chars. One sentence. Business outcome first, tech second."
author: "Amr Abdel-Motaleb"   # or a real contributor name
layout: article                # or "news" for the news index
date: YYYY-MM-DDTHH:MM:SS.000Z
lastmod: YYYY-MM-DDTHH:MM:SS.000Z
draft: false
categories: [tech, ai]         # lowercase flow-style; primary = subfolder, 'ai' only sanctioned secondary
tags: [tag1, tag2]             # lowercase kebab-case flow-style list, 3-8 tags
preview: /images/previews/<slug>.png
---
```

`<slug>` is derived from `title`: lowercase, every run of non-alphanumeric characters becomes a single `-`, leading/trailing `-` stripped, then truncated to 50 characters (a trailing `-` from truncation is kept). The `/images/previews/` short form is correct — the build auto-prefixes `/assets`. See [`docs/preview-images.md`](../../docs/preview-images.md) for the generation pipeline.

## Filename

`YYYY-MM-DD-kebab-case-title.md` under the appropriate subfolder. Date in filename must match `date:` in frontmatter.

## Post-specific structure

A typical post should follow this skeleton (skip sections that don't apply, don't pad):

1. **Hook** — 1–2 sentences naming the problem in the reader's language
2. **Why it matters now** — cost, risk, or opportunity, with a real number when you have one
3. **What we'd actually do** — the recommendation, in plain terms
4. **How it plays out** — phased approach, timeline ranges, what the reader's team has to do
5. **Watch-outs** — the 2–3 things that go wrong in practice
6. **Next step** — link to the relevant `/services/...` page or `/contact/`

## Hard don'ts

- Don't commit posts with `draft: true` to `main` — Pages will publish them.
- Don't reference internal URLs that don't exist; verify with the local build.
- Don't include literal API keys, even as examples — use `${env:VAR}` placeholders.
- Don't bump `date:` on edits — bump `lastmod:` instead.
- Don't write "thought leadership" posts with no recommendation or next step.

## Before commit

- [ ] Subfolder matches topic table above
- [ ] Universal checklist in `content-style.instructions.md` passes
- [ ] Post links to at least one service page or `/contact/`
- [ ] `lastmod` updated
- [ ] Build passes locally
