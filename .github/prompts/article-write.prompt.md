---
mode: agent
description: "Draft a new bash-365.com blog post end-to-end: route subfolder, scaffold frontmatter, follow voice + structure rules"
date: 2026-05-18T12:00:00.000Z
lastmod: 2026-05-18T12:00:00.000Z
---

# Write Article — BASH Consultants

Invoked as `/article-write`. Drafts a new post under `pages/_posts/{corp,erp,muses,tech}/` that conforms to `content-style.instructions.md` and `posts.instructions.md`.

## Inputs (ask once, in this order)

1. **Topic** — one sentence (e.g., "Why a Denver clinic should move off legacy on-prem QuickBooks")
2. **Subfolder** — `corp` / `erp` / `muses` / `tech` (suggest one based on topic, confirm)
3. **Reader** — owner / controller / IT lead / mixed (default: infer from subfolder routing table)
4. **Target length** — short (≤500 words) / standard (600–900) / long (1000–1500). Default: standard
5. **Anchor industry** — pick at least one from the target-industry table (professional services, construction, light mfg, clinics, retail, nonprofits)
6. **Slug** — kebab-case; if omitted, derive from topic

If the user gives the topic and "go", fill the rest with defaults and proceed.

## Workflow

### 1. Route + name

- Pick subfolder per the table in `posts.instructions.md`
- Filename: `pages/_posts/<subfolder>/YYYY-MM-DD-<slug>.md` using today's date
- Verify file does not already exist before writing

### 2. Frontmatter

Emit exactly:

```yaml
---
title: "Sentence-case title, no trailing period"
description: "120–155 chars. Outcome first, tech second. No marketing fluff."
author: "Amr Abdel-Motaleb"
layout: article
date: YYYY-MM-DDTHH:MM:SS.000Z
lastmod: YYYY-MM-DDTHH:MM:SS.000Z
draft: false
categories: [<Category>]
tags: [<tag1>, <tag2>]
preview: /images/previews/<slug>.png
---
```

Self-check: `description` length is 120–155, `categories` + `tags` are YAML lists, `draft: false` present.

### 3. Body skeleton (from `posts.instructions.md`)

Use this section order, skipping any that don't apply — never pad:

1. **Hook** — 1–2 sentences naming the problem in the reader's words
2. **Why it matters now** — cost, risk, or opportunity; use a number range if you have one
3. **What we'd actually do** — the recommendation in plain terms
4. **How it plays out** — phased approach with timeline ranges, what the reader's team owns
5. **Watch-outs** — 2–3 things that actually go wrong
6. **Next step** — link to a `/services/<page>/` and to `/contact/`

H1 comes from `title` — body starts at H2, sentence-case headings.

### 4. Voice gate (from `content-style.instructions.md`)

Before returning the draft, self-check:

- [ ] No banned phrases ("leverage synergies", "cutting-edge", "in today's …", "best-of-breed", "solutioning", "unlock value", "fast-paced")
- [ ] At least one named target industry from the table
- [ ] No invented numbers, fake case studies, or fixed pricing
- [ ] Acronyms spelled out on first use
- [ ] One CTA (the "Next step" link)
- [ ] Contractions OK; active voice; second person where natural
- [ ] No literal secrets in any code block — use `${env:VAR}` placeholders
- [ ] US English, USD, Denver / Front Range local references welcome

### 5. Preview image placeholder

Do **not** generate an image. Reference `/images/previews/<slug>.png` in frontmatter and add a single TODO comment near the top of the body:

```markdown
<!-- TODO: add preview image at /images/previews/<slug>.png (1200×630) -->
```

### 6. Output

Return a single message containing:

1. The full file content in one fenced code block, labeled with the path
2. A 5-line summary: subfolder, slug, word count, industries named, banned-phrase check (pass/fail)
3. Suggested next command: `/commit-publish`

Do not create the file with file tools unless the user confirms or originally said "create".

## Hard rules

- Never set `draft: true`. Pages will publish anything that merges to `main`.
- Never invent statistics, customer names, or vendor benchmarks.
- Never publish a fixed price. Ranges or "starting at" only when the user supplied them.
- Never bash a named competitor consultancy. Compare to vendor offerings positively.
- Never skip the voice gate.

## Related

- `.github/instructions/content-style.instructions.md` — voice, audience, banned phrases, industries
- `.github/instructions/posts.instructions.md` — subfolder routing + post-specific structure
- `.github/prompts/article-review.prompt.md` — run after drafting for SEO + depth pass
- `.github/prompts/commit-publish.prompt.md` — ship the post
