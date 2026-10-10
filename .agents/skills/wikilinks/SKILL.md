---
name: wikilinks
description: Author Obsidian-style [[wikilinks]] that actually resolve on GitHub Pages. Use whenever adding or editing internal cross-links in content — covers the pipeless rule, the non-root-page rule, and how resolution works in production safe mode.
---

# Obsidian wikilinks that survive production

Internal cross-links use Obsidian `[[Page Title]]` syntax. It is convenient and it reads well, but it has two failure modes that have each cost real time. Follow these rules and it just works.

## How resolution actually works

- **Production (GitHub Pages) is client-side.** `assets/js/obsidian-wiki-links.js` runs in the
browser, fetches `/assets/data/wiki-index.json`, and rewrites `[[Title]]` into real links after the page loads. The index is a pure-Liquid template (works in Pages **safe mode**).
- **The server-side plugin does not run in production.** `_plugins/obsidian_links.rb` only runs in
local dev; GitHub Pages builds in safe mode and ignores local plugins. **Never rely on the plugin for correctness** — if it only works in dev, it is broken on the live site. The client-side resolver is the one that ships.

## Rule 1 — pipeless only

Write `[[Page Title]]`. **Never** write the aliased form `[[target|display text]]`.

- kramdown's GFM parser treats any `|` in a paragraph line as a table cell, so `[[a|b]]` gets
mangled into a broken `<td>` before the resolver ever sees it. The bare `[[Page Title]]` form has no pipe and passes through intact.
- Need different display text? **Reword the sentence** so the page title reads naturally inline —
e.g. "explore our [[IT strategy]]" — instead of aliasing. Watch grammar: don't produce "see how we [[IT strategy]]".

## Rule 2 — collection docs and non-root pages only

The wiki index covers **collection documents** and **pages whose `output_ext` is `.html`**. It does **not** index **root-level pages** like `tools.md`, `ai-operations.md`, `about.md`, `index.md`.

- Linking to a root-level page? Use a **normal markdown link**: `[our toolkit](/tools/)`, not
  `[[The BASH toolkit]]`.
- Linking to a collection doc (a post, a service, a toolkit doc)? `[[Exact Page Title]]` is correct —
  the title must match the target's `title:` exactly (case-sensitive).
- CTAs and buttons are always markdown/HTML links, never wikilinks.

## Authoring checklist

- [ ] Every `[[…]]` is pipeless.
- [ ] Every `[[…]]` target is a collection doc or `.html` page, and the text matches its `title:`.
- [ ] Root-page and CTA links are markdown, not wikilinks.
- [ ] Sentences still read grammatically with the title inlined.

## Verify in the browser

After building, load the page in the dev server and run in the console:

```js
// raw brackets left unresolved (should be 0) and broken links (should be 0)
[...document.body.innerText.matchAll(/\[\[.*?\]\]/g)].length;
document.querySelectorAll('a.broken-wikilink, a[href="#"]').length;
```

Zero raw `[[…]]` brackets and zero broken links means every wikilink resolved. If a title shows as raw brackets, it is either not in the index (a root page — use markdown) or the title string doesn't match the target exactly.
