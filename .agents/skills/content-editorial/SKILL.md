---
name: content-editorial
description: Apply the BASH house editorial standards and run the content lint gate on any customer-facing page or post before it ships. Use when writing, editing, or reviewing content under pages/, index.md, about.md, contact.md, tools.md, or ai-operations.md.
---

# Content editorial gate

The governed way to bring any customer-facing content to publishable quality. This is the procedure the site describes at `/ai-operations/` — the editorial scrutiny is written down, so the tenth page gets the same rigor as the first. Follow it in order; do not skip the lint.

## Sources of truth (read, don't restate)

- **Voice + mechanics:** [`.github/instructions/content-style.instructions.md`](../../../.github/instructions/content-style.instructions.md)
- **Brand / identity:** [`.github/instructions/brand.instructions.md`](../../../.github/instructions/brand.instructions.md)
- **Page-type rules:** `.github/instructions/posts.instructions.md` (posts), `services.instructions.md` (services)
- **Section voice profiles:** [`_data/taxonomy.yml`](../../../_data/taxonomy.yml) — corp / erp / muses / tech
- **Frontmatter schema for prompts/instructions:** `.github/FRONTMATTER.md`

## Procedure

1. **Identify the page type** from the path and frontmatter: post (`pages/_posts/<section>/`),
service (`pages/_services/`), toolkit doc (`pages/_toolkit/`), or root page. Load the matching instruction file(s). For a post, read its section's voice profile in `taxonomy.yml`.

2. **Apply the checklist** (from `content-style.instructions.md` — the authoritative version):
   - One `H1`, rendered from `title:`. Body starts at `H2`. Headings **sentence case**, sequential
     (no `H2` → `H4` jumps).
   - Every acronym expanded on first use: "Enterprise Resource Planning (ERP)".
   - **No banned phrases** (cutting-edge, seamless/robust/scalable without a number, revolutionary,
     leverage synergies, "in today's fast-paced world", etc.).
   - **Enact, don't announce** — no reader-facing text names the piece's own device (satire, parody,
     musical number, exposé). The device is performed, never labeled.
   - Active voice; lead with the business outcome; **exactly one CTA**, ending on the reader's next
     step. No exclamation marks. US English.
   - No invented metrics, client names, logos, or certifications. Compliance framing describes what
     the framework *requires*; never claims BASH is certified.
   - Descriptive anchor text (never "click here"); ≥1 internal + ≥1 external link (external only to
     vendor docs, primary sources, or regulators).
   - All non-decorative images have content-describing `alt` text.

3. **Verify the frontmatter:**
   - `title` ≤ 60 chars; `description` **120–155 chars, one sentence, no trailing period**, primary
     keyword included naturally; `keywords` 5–10 real search phrases.
   - `author: Amr Abdel-Motaleb`. Dates ISO-8601 with milliseconds (`YYYY-MM-DDTHH:MM:SS.000Z`).
     Bump **`lastmod`** (not `date`) on edits, to today's real date.
   - `categories`/`tags` flow-style, lowercase; for posts, exactly one primary matching the subfolder
     (+ optional `ai` secondary).

4. **Run the lint gate** and fix everything it reports in your files:
   ```bash
   python3 scripts/content_lint.py             # lints the whole repo, exit 1 on errors
   python3 scripts/content_lint.py --warn-only # report without failing
   ```
It mechanically catches banned phrases, description length, heading case, undefined acronyms, and trailing-period descriptions across all content. Zero errors is the bar.

5. **Validate the build** if structure/frontmatter changed:
   ```bash
   docker-compose exec -T jekyll bundle exec jekyll build --config '_config.yml,_config_dev.yml'
   ```

6. **Final polish is Opus 4.8.** The last read-through — voice, flow, that no device descriptor
   survived — is done with Opus 4.8 before the content is considered done.

## Output

Report readiness as **Ready / Needs minor edits / Needs significant work**, list what you changed, and paste corrected frontmatter and any rewritten passages ready to drop in. For a full editorial + SEO + frontmatter review of a draft, delegate to the `article-reviewer-editor` agent instead — it carries editorial memory across sessions.
