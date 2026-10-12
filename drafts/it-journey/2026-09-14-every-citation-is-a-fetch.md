---
title: "Every citation is a fetch: writing an essay about relics with an AI that had to earn its sources"
description: "A one-sentence prompt, a repository that carries the voice in files, four real-world anchors that each had to be verified against a primary source, and a Jekyll build validated on the stack that ships — without Docker."
date: 2026-09-14
categories: [it-journey]
tags: [claude-code, ai-workflows, technical-writing, primary-sources, jekyll, legacy-systems, content-pipeline, governance, bash-365]
draft: true
---

## The ask

One sentence, no brief: *write a muse about information systems as ancient relics and artifacts that now require techniques and knowledge invented by the dead or retired; new solutions require ancient wisdom.*

That was the whole prompt. The finished piece — "Your business runs on relics, and their makers have left," an essay for the `muses` section of bash-365.com — runs a little over 2,000 words, cites four primary sources, cross-links three other pages on the site, passes the repository's editorial lint, and rendered cleanly on a production build. None of the voice, structure, or rules came from the prompt. They came from files.

The interesting part of the session is not the essay. It is how little the prompt had to carry, and how much of the remaining work was verification rather than writing.

## Where the voice came from

The repository has a layered context framework, and the layers did the briefing:

1. `CLAUDE.md` says what the repo is and points at everything else.
2. `_data/taxonomy.yml` carries a voice profile per section. For `muses`: "reflective and essayistic, lightly witty … every essay still ends pointed at something the reader can do." That single paragraph is the difference between an essay and a listicle.
3. `content-style.instructions.md` holds the mechanics: banned phrases, acronyms expanded on first use, sentence-case headings, exactly one call to action, a description of 120–155 characters with no trailing period, external links only to primary sources.
4. `posts.instructions.md` holds the frontmatter schema, the filename rule, and the rule that derives the banner image's filename from the title.
5. The `wikilinks` skill holds the two rules for internal `[[links]]` that have each cost real time before.

Reading two existing essays in the section — one that reads vendor "best practice" through Plato's Thrasymachus, one about the load-bearing Excel workbook — set the register more precisely than any instruction could. The pattern generalizes: **a short prompt against a well-governed repository beats a long prompt against a bare one.** The rules live in files, the model reads them every session, and a human never has to re-explain the house style.

## Memory is a hypothesis; a citation is a fetch

The essay wanted four real-world anchors: a government report on the age of federal systems, the New Jersey governor's 2020 call for COBOL volunteers, NASA's note that fixing Voyager 1 means reading decades-old documents, and the Antikythera mechanism as the artifact that outlived its own understanding. The model "remembered" all four. Here is what verification found.

| Anchor | What memory said | What the fetch found |
|---|---|---|
| GAO on legacy systems | Report `GAO-19-371`, "8 to 51 years old" | That number returns a 404. The real 2019 report is `GAO-19-471`, and there is a July 2025 successor (`GAO-25-107795`) covering eleven systems 23 to 60 years old, several on COBOL and assembly. The fresher, more precise source won. |
| Voyager's "decades-old documents" | The JPL article on the October 2023 software patch | The quote is not in that article. It is in a NASA Science blog post dated December 12, 2023, word for word. |
| Antikythera, "more complex than any known device for at least a millennium" | Freeth et al., *Nature*, 2006 | Right paper. Getting the abstract took five attempts: Nature bounced through an identity-provider redirect, PubMed showed only a cookie notice, Europe PMC returned 403, the Semantic Scholar API confirmed title, venue, and year but carried no abstract, and the third hop of Nature's own redirect chain finally returned the text with the sentence intact. |
| New Jersey's COBOL call, April 2020 | The governor's pandemic briefing | Search located the transcripts on `nj.gov`; every fetch of them failed through the proxy. The fact went into the essay without a link, because the house rule allows external links only to primary sources, and an unlinked well-documented fact beats a link to a news write-up or to a URL nobody could open. |

The pattern is worth stating plainly, because it is the typical failure of a language model doing research and it is not the one people fear. **Memory was right about the substance in all four cases and wrong about the address in two.** Not fabrication — misattribution. A real quote pinned to the wrong page; a real report under the wrong number. The house rule that forces a primary-source link is what forces the fetch, and the fetch is where the corrections happen. A rule about *links* turned out to be a rule about *truth*.

Two habits fell out of this:

- **Keep a fallback chain for paywalled papers and write it down.** Publisher page → PubMed Central or Europe PMC → the Semantic Scholar or CrossRef API for metadata → the publisher's redirect chain, one hop at a time. Each rung gives you something different; the API gave venue and year with no abstract, which was enough to confirm the citation even before the abstract arrived.
- **A source you cannot open is a fact you can state but not link.** Do not downgrade to a secondary source to get a hyperlink. Say the thing, or cut it.

## The wikilink with an apostrophe

The site resolves Obsidian-style `[[Page Title]]` links two ways: a Ruby plugin on builds where plugins run, and a small JavaScript resolver on GitHub Pages, which builds in safe mode and ignores local plugins. Both normalize titles to lowercase with collapsed whitespace and look them up in a generated index.

The essay wanted to link the site's "Frankenstein's ERP" post. That title has an apostrophe, and kramdown's typographic-quotes pass turns a straight `'` in body text into a curly `’` before the client-side resolver ever sees it, while the index keeps the frontmatter's straight one. Whether the resolver copes with that was not known and was not worth an afternoon to find out. The post has an explicit permalink, so it got an ordinary markdown link instead.

The rule: **when a link's correctness depends on a resolver you have not tested for that character, use the dumb link.** The other three wikilinks — a case study, a toolkit reference, the doctrine page — had plain titles and resolved on the first build.

## Building the stack that ships, without Docker

The repository's local-dev stack expects a theme checkout mounted at `/zer0-mistakes` via Docker Compose. The sandbox had Ruby 3.3 and Bundler but no Docker daemon and no mount, so the documented developer check was unavailable.

The site ships on two other stacks, though, and one of them needs neither. The Azure build uses `Gemfile.azure` (the published theme gem from RubyGems, no remote-theme plugin) and `_config.azure.yml` (which clears `remote_theme`, sets `theme:`, and replaces the plugin list). That is a stack a bare shell can run:

```bash
export LANG=C.UTF-8 BUNDLE_GEMFILE=Gemfile.azure BUNDLE_PATH=/tmp/gems
bundle install --jobs 4
bundle exec jekyll build --config _config.yml,_config.azure.yml -d /tmp/_site
```

Gem install took a few minutes; the build took fourteen seconds. `LANG=C.UTF-8` is there because a previous session in this repository lost time to Ruby deriving a US-ASCII default encoding from an unset locale and rejecting a non-ASCII byte in a stylesheet — a lesson that was written down, which is the only reason it was cheap this time.

What the build proved: the post rendered at its permalink, all three wikilinks resolved server-side, the meta description came through at 146 characters, the section index listed the piece, and — the check that matters for production — the generated `wiki-index.json` that the client-side resolver reads on GitHub Pages contained all three targets. `CLAUDE.md` says it directly: validate against the stack the change ships on. When the documented check is unavailable, find the shipping stack you *can* run rather than skipping validation.

## The gate and the second reader

Deterministic checks ran first. `scripts/content_lint.py` walks every reader-facing page and fails on banned phrases, description length, missing frontmatter, a title with an exclamation mark, or a filename date that disagrees with the frontmatter. The new post produced zero findings; the thirteen warnings in the run all belonged to other files and predate it. That is the point of a deterministic gate: the model's judgment is spent on the essay, not on counting characters.

Then a second reader, in a fresh context: the repository's `article-reviewer-editor` subagent, run with a specific instruction — *do not edit any files; report only; quote the exact current text and the proposed replacement for every recommended edit.* Separating writer from reviewer is the same idea as separating the person who codes from the person who approves the pull request. Asking for verbatim before-and-after text makes the review mechanically applicable and stops the reviewer from restating the style guide.

The verdict came back *needs minor edits*, as ten numbered items, each quoting the current text and a replacement. Most went in as proposed or lightly adapted: a quotation that had been introduced with a verb the source did not support was re-cut to the source's own clause; a paragraph of two hundred words carrying three examples was split; the Rosetta Stone's "three scripts" gained "and two languages" so it no longer sat four words from "bilingual" looking like a mistake; and a fix that the essay had placed under a December 2023 link was re-pointed at the April 2024 post that actually describes it. The most instructive item was a figure. The GAO page had said "eight of the 11 systems" use legacy languages; the fetch result in this very session said so; the essay said "several." The reviewer, re-reading the same source, restored the number. **A fetched source is data, and data has to be read twice** — once to confirm it exists, once to take everything it offers.

One suggestion was declined on judgment, a keyword-heavy sub-title in place of the essay's own phrase, and one was taken in spirit with different wording. The blocking item, the missing banner image, stays with the owner because the sandbox has no image-model credentials. The reviewer also wrote to its own memory directory in the repository: the four verified sources with their exact figures, the fetch workarounds for paywalled papers, and the observation that the section's ending convention had shifted. That memory is committed alongside the post, which is how the next review starts a step ahead of this one.

## Working this way with an AI

- **Put the voice in files, not in the prompt.** A one-line ask worked because the taxonomy, the style guide, the frontmatter schema, and the link rules were all in the repository, versioned, and read every session.
- **Treat every remembered citation as an address to verify, not a fact to paste.** The common failure is misattribution, not invention. A rule that external links must be primary sources is the cheapest enforcement available.
- **Write down the fallback chain for sources**, the way you would write down a deployment runbook. It is reusable and the next session will need it.
- **Validate on a stack that ships, and know which of your configurations can run where.** The dev stack needed Docker; the Azure stack needed a gem. One of them was available.
- **Split writer and reviewer, and make the reviewer's output verbatim-applicable.** "Report only, quote current text and replacement" is the instruction.
- **Run the fleet's formatters before its bots do.** This repository enforces one paragraph per line and has a workflow that fixes violations by pushing to your branch. Running `python3 tools/unwrap-prose.py --check` before a push costs seconds and keeps the branch history yours.
- **The essay's own warning applies to the tool that wrote it.** Its central hazard is "confident archaeology": a model reading an undocumented system produces fluent, plausible stories about what each layer means, unchecked against the one person who could check them. A model citing from memory does exactly the same thing. The cure is identical in both cases — a bilingual artifact: a reconciliation that ties out, a fetch that returns the quote, a number you did not generate that your conclusion has to collide with.

## The residue

- **The banner is not painted.** The site's preview images are generated from title and description by a script that needs an image-model key, and the sandbox has none. The filename is already determined by the house rule — lowercase the title, collapse non-alphanumerics to hyphens, truncate to fifty characters — which yields `your-business-runs-on-relics-and-their-makers-have.png`, cut mid-phrase. Settle the title before painting the banner; retitling orphans the image.
- **A hygiene bot pushed to the branch.** The repository's `markdown-oneline` workflow enforces one paragraph per line and, on a pull request, fixes the file and pushes the repair itself rather than failing. The reviewer agent had written three soft-wrapped lines into its memory file; the bot joined them and committed `style: unwrap soft-wrapped markdown prose` on top of the push. The runs that commit triggered sat at "action required" because the pusher was the Actions bot, and the workflow's own header comment explains why that is harmless: the repository runs no required status checks, and the previous head had already passed every check. Read the workflow file before treating a bot's side effect as a failure; the design intent is usually written at the top.
- **Three sources that could not be opened from inside the sandbox** (`nj.gov`, the ACM Digital Library, Europe PMC) were reachable through other routes or stated without a link. A proxy that returns 404 for a page that exists looks identical to a page that does not; the distinction only appears when a search engine has already seen the page. Keep both signals.
