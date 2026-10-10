---
name: toolkit-doc
description: Author or scaffold a BASH toolkit doc — business-track DIY guide or partner-track advanced reference — with correct frontmatter, category-driven URL, topic grouping, wikilinks, and sidebar nav wiring. Use when adding a page under pages/_toolkit/.
---

# Author a BASH toolkit doc

The toolkit (`pages/_toolkit/`) is a two-track library: **business** (DIY guides for SMB owners) and **partners** (deep technical reference for senior consultants). Landing pages loop the collection by `categories` and `topic`, so the frontmatter is load-bearing — the grids build themselves from it.

## How the collection works

- Collection `toolkit` with `permalink: /tools/:categories/:name/` (set in `_config.yml`).
- **`categories` drives the URL and the track.** `[business]` → `/tools/business/<name>/`;
  `[partners]` → `/tools/partners/<name>/`. Exactly one category.
- Landing pages ([`business.md`](../../../pages/_toolkit/business.md),
[`partners.md`](../../../pages/_toolkit/partners.md)) group docs by `topic`, ordered by `order`, labeled by the first doc's `topic_label`, and badge each by `level`. The hub ([`tools.md`](../../../tools.md)) and sidebar nav surface them too.

## Frontmatter template

Copy an existing sibling in the same track as the real template ([`qualification.md`](../../../pages/_toolkit/qualification.md) is a good partner example). Fill:

```yaml
---
title: "<Title — sentence case, ≤ 60 chars>"
sub-title: "<one-line subtitle>"
description: <120–155 chars, one sentence, no trailing period, primary keyword natural>
excerpt: <one- or two-sentence summary for listings>
author: "Amr Abdel-Motaleb"
layout: default
categories: [business]        # or [partners] — drives the URL and track
topic: <see topic list>       # groups the doc on the landing page
topic_label: "<Heading for that topic group>"
level: foundational           # business: foundational|intermediate | partners: advanced
order: 10                      # sort within the topic group
tags: [toolkit, ...]
keywords:
  - <5–10 real search phrases>
lastmod: <YYYY-MM-DDTHH:MM:SS.000Z — today>
mermaid: false                 # true only if the doc has a Mermaid diagram
sidebar:
  nav: toolkit
permalink: /tools/<category>/<name>/
---
```

**Topics** (partner order): `practice, ai, cloud, erp, fintech, data, dev, strategy, security`. Business docs use their own topic grouping — check `business.md` for the current set. Reuse an existing `topic`/`topic_label` before coining a new one, or the landing group won't render as intended.

## Writing rules

1. Obey the **`content-editorial`** skill and `content-style.instructions.md` in full (headings,
   acronyms, banned phrases, one CTA, no invented metrics).
2. **Audience calibration.** Business track: plain-language, ROI- and risk-first, no assumed IT
background, tie every section to a business outcome. Partner track: assume a senior practitioner — architecture, failure modes, trade-offs, named tools — and hold to the BASH doctrine (deterministic-first, AI as overlay).
3. **Cross-link with wikilinks.** Use `[[Exact Page Title]]` to link sibling toolkit docs — pipeless
only, and never to root pages. See the `wikilinks` skill. Link to services/root pages with normal markdown.
4. One `H1` (from `title`), body starts at `H2`, sentence case. External links only to vendor docs,
   primary sources, or regulators — verify each returns 200.

## Wire it in

1. Add a sidebar entry under the correct track group in
   [`_data/navigation/toolkit.yml`](../../../_data/navigation/toolkit.yml) (title + url).
2. Confirm it appears in the track landing page and `tools.md` hub — those are automatic if the
   `categories`/`topic`/`order` are right.

## Verify

```bash
python3 scripts/content_lint.py   # repo-wide editorial gate; fix any error in your new doc
docker-compose exec -T jekyll bundle exec jekyll build --config '_config.yml,_config_dev.yml'
```

Then load the page in the dev server and confirm: URL matches the permalink, the doc appears in its topic group with the right level badge, wikilinks resolve (no raw `[[…]]` brackets), and there is exactly one `H1`.
