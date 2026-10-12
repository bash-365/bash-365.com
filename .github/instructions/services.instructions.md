---
applyTo: "pages/_services/**/*.md"
description: "Service page standards for bash-365.com — frontmatter, structure, and conversion-focused content rules"
date: 2026-05-18T12:00:00.000Z
lastmod: 2026-05-18T12:00:00.000Z
---

# Service Page Instructions

Service pages live in `pages/_services/` (`cloud.md`, `data.md`, `dev.md`, `erp.md`, `fintech.md`, `strat.md`) plus the `index.md` hub. These are the primary conversion pages for the site.

> **Voice, audience, industry context, banned phrases, and universal checklist** → see [`content-style.instructions.md`](content-style.instructions.md). This file covers service-page-specific rules only.

## Required frontmatter

```yaml
---
title: "Service Name"
sub-title: "Short value-prop tagline"
description: "120–155 chars. What you do + who it's for + outcome."
preview: /assets/images/<service>.svg
snippet: "1-sentence pitch shown in service cards on the hub page."
author: "Amr Abdel-Motaleb"
layout: default
keywords:                # YAML list — used for SEO
  - Primary Keyword
  - Secondary Keyword
tags:                    # YAML list — used for cross-linking
  - Tag1
  - Tag2
lastmod: YYYY-MM-DDTHH:MM:SS.000Z
---
```

## Page structure (in order)

1. **Headline** (H1 via `title`) + sub-headline tying outcome to audience
2. **Problem statement** — the pain SMBs in our target industries actually feel (see industry table in `content-style.instructions.md`)
3. **What we do** — 3–6 concrete offerings as a bulleted list
4. **Who it's for** — 1–2 industry examples from our target list (construction, professional services, light manufacturing, clinics, retail, nonprofits)
5. **Approach / methodology** — how we engage (discovery → plan → deliver → support)
6. **Outcomes** — measurable results in ranges (uptime %, cost reduction band, time-to-value weeks)
7. **Tech stack / partners** — vendors and platforms we work with (AWS, Azure, GCP, NetSuite, QuickBooks, Microsoft 365, etc.)
8. **Call to action** — link to `/contact/` or a scheduling link

## Service-specific content rules

- **Concrete > abstract.** "Migrate your on-prem SQL Server to Azure SQL in 6–8 weeks" beats "leverage cloud transformation."
- **Name the buying signal.** When a reader self-identifies ("we've outgrown QuickBooks", "audit failed on access controls"), they're the right fit — make those moments explicit.
- **No competitor bashing.** Compare positively to vendor offerings, never to other consultancies by name.
- **Pricing:** never publish fixed prices; ranges or "starting at" only when accurate. See `content-style.instructions.md` for the full rule.
- **Logos and trademarks:** use vendor marks only with attribution; SVGs in `/assets/images/`.

## Hub page (`index.md`)

When adding a new service:
1. Create `pages/_services/<slug>.md` with full content
2. Update `pages/_services/index.md` cards to include the new service
3. Update site navigation in `_data/navigation/` if applicable

## Before commit

- [ ] At least one industry from the target-industry table named in the body
- [ ] At least one call-to-action linking to `/contact/`
- [ ] No fixed pricing claims
- [ ] Universal checklist in `content-style.instructions.md` passes
- [ ] Build passes locally
