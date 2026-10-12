---
applyTo: "pages/**/*.md,index.md,about.md,contact.md"
description: "Editorial voice, audience profile, industry context, and style rules for all customer-facing content on bash-365.com"
date: 2026-05-18T12:00:00.000Z
lastmod: 2026-06-21T12:00:00.000Z
---

# Content Style Guide

Shared editorial rules for all customer-facing content. Page-type-specific rules live in `posts.instructions.md` and `services.instructions.md` — this file covers the cross-cutting voice, audience, and style decisions.

## Who we write for

**Primary audience:** Owners, operators, and decision-makers at small and medium businesses (SMBs, 5–200 employees) in the **Denver metro area** evaluating outside IT help.

**Secondary audience:** In-house IT generalists at those SMBs who need to justify a project upward.

**Reader profile:**
- Time-poor; reads on mobile between meetings.
- Skeptical of vendor jargon; has been burned by oversold tech before.
- Cares about ROI, downtime risk, compliance exposure, and staff impact — in that order.
- Knows their industry deeply; does not know yours (cloud, ERP, data, dev).

## Who we are

**BASH Consulting** — Denver, CO. Founded by Amr Abdel-Motaleb (BS Finance, MS Information Systems). Mission: bring enterprise-grade IT (cloud, ERP, CRM, EAM, EPM, data architecture) within reach of SMBs without prohibitive capital investment.

**Differentiators to lean on:**
- Finance + IT dual background (financial systems literacy, not just plumbing).
- Vendor-neutral across AWS / Azure / GCP, Microsoft / Google / Oracle stacks.
- Practical experience with QuickBooks-to-ERP migrations and back-office modernization.
- Local — Denver SMBs deal with a real person, not a ticket queue.

**Do not claim:**
- Specific certifications (AWS Solutions Architect, Microsoft MVP, etc.) unless verified.
- Headcount, client logos, or revenue figures.
- "Award-winning", "industry-leading", "best-in-class".

## Industries we speak to

Real fit cases — write examples and case studies against these:

| Industry | Typical pain |
|---|---|
| Professional services (law, accounting, design) | Time tracking + billing + document management sprawl |
| Construction / trades | Field-to-office data flow, project costing, EAM |
| Light manufacturing / distribution | Inventory + ERP integration, QuickBooks outgrown |
| Healthcare clinics / dental | Compliance (HIPAA), EHR integration, secure file sharing |
| Retail (multi-location) | POS + eCommerce + accounting reconciliation |
| Nonprofits | Donor CRM, grant reporting, low-budget cloud migration |

Avoid: crypto, defense, gambling, adult — not our market.

## Voice and tone

- **Confident, not boastful.** "We've migrated dozens of QuickBooks shops to NetSuite" > "We're the leading experts in ERP migration."
- **Plain English first, technical second.** First mention of an acronym is spelled out: "Enterprise Resource Planning (ERP)".
- **Conversational but not chatty.** Contractions OK ("we'll", "you're"). Slang and exclamation marks are not.
- **Active voice.** "We design the architecture" not "The architecture is designed by us."
- **Lead with the business outcome**, follow with the technical mechanism, close with what the reader does next.
- **One CTA per page**, usually `/contact/` or a scheduling link.
- **Enact, don't announce.** Never label a piece's own creative device ("satire", "parody", "a Broadway-style musical number", "reality show", "exposé"). Perform the bit and let the reader notice — naming the genre flattens it. The final review/polish pass should confirm no raw descriptors survive in reader-facing text (title, description, excerpt, sub-title, snippet, body).

## Words to use

- "Outcome", "downtime", "month-end close", "audit-ready", "uptime", "cost-per-seat", "total cost of ownership (TCO)", "phased rollout", "vendor lock-in", "data residency", "compliance posture".
- Industry-specific terms when accurate: "GL" (general ledger), "AR/AP", "WIP", "EOM", "SLA", "MTTR", "RTO/RPO".

## Words to avoid (banned phrases)

- "In today's fast-paced world / digital age / AI era"
- "Leverage synergies", "unlock value", "best-of-breed", "world-class"
- "Cutting-edge", "next-generation", "disruptive", "revolutionary"
- "Solutioning", "ideate", "circle back", "low-hanging fruit"
- "Empower" used vaguely (only OK when followed by *who* and *to do what*)
- "Robust", "seamless", "scalable" without a number or example backing it up

## Numbers, claims, and proof

- Use ranges, not specifics, when you don't have audited data: "typically 4–8 weeks", not "exactly 6 weeks".
- Never invent customer wins. If you don't have a case study, describe a *category* of work ("for a Denver construction firm with ~40 field staff").
- Pricing on customer-facing pages: ranges or "starting at" only. No fixed quotes.
- Quote vendor pricing only if you link to the vendor's own pricing page and dated it ("AWS pricing as of <month>").

## Formatting

- **One H1 per page**, rendered from `title:`. Body starts at H2.
- **Heading style:** sentence case ("Cloud architecture and migration"), not title case.
- **Lists:** prefer bulleted lists over long paragraphs for offerings, benefits, prerequisites.
- **Tables:** use for comparisons (e.g., AWS vs Azure for a specific workload), not for prose.
- **Code blocks:** language-tagged. Don't paste secrets — use `${env:VAR}` placeholders.
- **Images:** SVG preferred for diagrams; PNG for screenshots. Always include alt text describing the *content*, not "screenshot of dashboard".
- **Links:** descriptive anchor text ("our cloud migration approach"), never "click here".

## SEO basics

- `title` ≤ 60 characters.
- `description` 120–155 characters, one sentence, includes a primary keyword naturally.
- `keywords` list 5–10 phrases real prospects search for ("Denver IT consultant", "QuickBooks to NetSuite migration", "Azure SMB migration cost").
- Internal links: at least one inbound and one outbound per service/post page.
- External links: only to vendor docs, primary sources, or regulators — not blog posts.

## Accessibility

- Contrast: rely on the theme; don't override colors mid-page.
- All non-decorative images have `alt` text.
- Don't use icon-only buttons without accompanying text.
- Heading hierarchy is sequential — don't jump H2 → H4.

## Localization

- US English spelling and date format (`May 18, 2026`).
- Currency in USD unless explicitly comparing markets.
- Local references OK and encouraged when relevant ("Front Range supply-chain businesses", "RTD-adjacent retailers") — they signal we actually know the market.

## Legal and compliance

- Never reproduce proprietary docs (vendor partner agreements, NDAs, customer data).
- HIPAA / PCI / SOC 2 mentions: describe what the framework requires, never claim BASH Consulting is "certified" unless we are.
- Trademarks: ™ or ® on first mention only; avoid plural possessives of vendor names ("AWS's" → "the AWS").

## Before publish — universal checklist

- [ ] Frontmatter complete and valid
- [ ] `description` 120–155 chars, no banned phrases
- [ ] One H1, sequential headings, sentence case
- [ ] Every acronym defined on first use
- [ ] Numbers either cited, ranged, or removed
- [ ] One clear CTA
- [ ] All images have alt text
- [ ] `lastmod` updated
- [ ] Build passes locally (`docker-compose exec jekyll bundle exec jekyll build --config '_config.yml,_config_dev.yml'`)
