---
name: project-bash-365
description: bash-365.com is a Jekyll site; instruction files in .github/ are the authoritative style/SEO/frontmatter source
metadata:
  type: project
---

bash-365.com is a Jekyll (zer0-mistakes theme) marketing/blog site for BASH Consulting.

**Why:** The repo's `.github/instructions/*.instructions.md` files ARE the editorial standard — review content against them, not generic SEO best practice. `.github/FRONTMATTER.md` is the canonical schema for the instruction files themselves (not for content pages).

**How to apply:**
- Service pages: `pages/_services/` (cloud, data, dev, erp, fintech, strat + index.md hub). Standards in [[reference-service-page-standards]].
- Cross-cutting voice/SEO/style: [[reference-content-style]].
- Build check: `docker-compose exec jekyll bundle exec jekyll build --config '_config.yml,_config_dev.yml'`.
- Linked service routes resolve to `pages/_services/<slug>.md` via `permalink:` (e.g. /services/cloud/ -> cloud.md). Contact page is `contact.md` at repo root -> /contact/.
