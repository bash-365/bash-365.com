---
title: "Writing an essay inside a governed content repo"
description: "A six-word prompt became a publishable essay because the repository, not the prompt, carried the voice, the rules, and the gates — what that looks like and how to build it"
date: 2026-09-14
categories: [it-journey]
tags: [claude-code, ai-workflows, jekyll, content-governance, linting, ci-cd, github-pages, technical-writing, bash-365]
draft: true
---

## The ask

The whole prompt was six words: *IT is the new Finance department. Write about it.*

That is a thesis, not a brief. No section, no length, no audience, no links, no date. In a blank chat window the result would be a generic think-piece with a confident tone and no home. In the `bash-365.com` repository the same six words produced a placed, linted, cross-linked essay with a changelog entry, because almost everything the prompt left out was already written down somewhere in the tree. This post is about where, and why that matters more than the prompt.

## The repo answered the questions the prompt didn't

Before writing a word, the session read the layers the repo's `CLAUDE.md` points at, in order. Each one removed a decision the prompt had left open.

| Open question | Answered by | The answer |
|---|---|---|
| Which section does this belong in? | `_data/taxonomy.yml` and `posts.instructions.md` | A thesis essay is `muses` (reflective, essayistic, lightly witty), not `corp` (lead with the number, zero whimsy). One primary category, and it must equal the subfolder. |
| What does "on voice" mean here? | The two most recent essays in the same folder | Calibration by example: an argument built on a borrowed frame (Plato, a spreadsheet formula), plain English, an ending that names something the reader can do Monday. |
| What is the brand allowed to say? | `brand.instructions.md` | Finance + IT dual fluency is *the* differentiator, so the essay can speak both languages. No certifications, no headcount, no client logos. The `bash` motif may appear once if it earns its place. |
| What does the frontmatter need? | `posts.instructions.md` | `description` of 120 to 155 characters with no trailing period, `title` under 60, `keywords` of 5 to 10, `tags` of 3 to 8 in lowercase kebab-case, a `preview` path derived from the title by a stated rule. |
| How do internal links work? | The `wikilinks` skill | `[[Exact Page Title]]`, never the aliased `[[a|b]]` form (kramdown turns the pipe into a table cell), and only to collection documents, never root pages. |
| What is "done"? | `CLAUDE.md` operating rules | Lint passes with zero errors, the changelog gets an entry, the build is validated on the stack it ships on, and a final polish pass runs on a stronger model. |

None of that was in the prompt. All of it shaped the output. That is the practical meaning of *governed AI*: the rules are files, so every session starts with the same rules, and a six-word prompt is enough because the other six hundred words are already committed.

## Deterministic gates did the boring checking

Three scripts ran, and each one replaced a category of review a human would otherwise do by eye.

**`scripts/content_lint.py`** checks the editorial contract mechanically: banned marketing phrases (word-boundaried and case-insensitive, with code blocks exempt), description length, exclamation marks in titles, flow-style category lists, the filename date matching the frontmatter date, and any truthy `draft:` value that would leak an unfinished post onto the live site. It reported zero errors on the first run, which is not luck. The rules it enforces were read before the draft was written, so the draft was written to them.

**`tools/unwrap-prose.py`** enforces one paragraph per line. On a pull request the workflow does not just fail on a soft-wrapped paragraph, it fixes the file and pushes the repair back to the branch using the default token, which fires no further workflow events. Zero extra CI runs for whitespace. Running it locally first meant nothing to repair.

**The Pages-stack build.** The sandbox had no Docker daemon and no installed gems, so the repo's documented developer build was unavailable. The fix was to read `.github/workflows/build-validate.yml`, notice that CI writes its own four-line Gemfile for the GitHub Pages stack rather than using the repo's root Gemfile (which pins the theme to a local path that only exists in Docker), and reproduce exactly that in a scratch directory. The lesson generalizes: when the documented local build does not work in your environment, the CI workflow is the executable description of the build that actually ships. Copy the job, not the README.

The first run of that copied job failed anyway, on an SCSS file inside the remote theme: *Invalid US-ASCII character*. The sandbox had no `LANG` set, so Ruby read every file as ASCII and choked on the first UTF-8 character it met. The CI runner never hits this because its image ships with a UTF-8 locale. Two environment variables (`LANG=C.UTF-8 LC_ALL=C.UTF-8`) and the build passed in eighteen seconds. The general point is that an error inside a dependency's file, in a stack the repo's own tests never touch, is usually the environment and not the code. Check the locale before you check the theme.

## Sources were verified, not generated

The repo has a hard rule: *don't generate or guess external URLs.* The essay wanted two primary sources, the Sarbanes-Oxley Act and Alfred Chandler's *The Visible Hand*. The government publishing page for the Act fetched and confirmed as Public Law 107-204. The publisher's page for the book returned an HTTP 202 with an empty body, which is a bot challenge, not a page. So the Act is linked and the book is named without a link.

That is the correct outcome, and it is worth noticing why. A model can produce a plausible URL for any book ever printed. The rule does not make the model smarter; it makes an unverified link a violation instead of a shortcut, so the cheap path is to check. A one-line rule in a file is far cheaper than a fact-checker, and it never gets tired.

## A second model did the polish

The repo specifies that the final read-through on any content is done by a stronger model than the one that drafted it. In practice that meant handing the finished draft to the repository's `article-reviewer-editor` agent, running on a different model, with the same instruction files as its rubric and an explicit *do not edit, report exact replacements* brief.

It found six things, none of which the linter could have caught and all of which a good editor would. A link had been introduced with "already written down in this section" when the linked post lives in a different section: a false claim wrapped around a correct link. A sentence about the Sarbanes-Oxley Act read as if it applied to every audited company, when the statute reaches public companies and a private firm meets the same questions through its cyber-insurance renewal and its customers' due diligence. The word "actually" appeared five times. The closing sentence was a mirrored construction that never resolved its own predicate, at the one position in an essay where the sentence matters most. An acronym had been expanded inside a possessive. And two illustrative figures ("six departments", "a week to build") read as data in a house that wants ranges wherever there is no audited number. Every one of those became an exact old-text, new-text pair, and the reviewer also wrote the patterns into its own memory file so the next review starts with them.

The point of a second reader with the same written rules is that the review becomes checkable. "This paragraph is weak" is taste. "This acronym is expanded twice, the second expansion is on line 40, and the wikilink target does not match any `title:` in `pages/`" is a defect with a location. The rules make the second opinion an audit rather than an argument.

## What the essay itself argues, briefly

Because it is the artifact the session existed to produce: finance became a department, rather than a clerk with a ledger, when companies grew past what an owner could see, and its authority comes from holding the system of record. In a modern small business every event is recorded in a system with a timestamp and a username before it becomes a journal entry, and operating spend has moved to metered software, cloud, and AI tokens. The function that runs the systems now holds the view finance used to hold alone. The controls are the same ideas under different names (segregation of duties is least privilege, the reconciliation is the access review, the audit trail is the log), and what IT still lacks at small-business scale is what finance built over a century: a close on the calendar, a language every manager reads, and a seat at the table. The essay ends with four moves, including copying the fractional-CFO structure for IT.

## Tips for building this way

- **Put the voice in a file, per section.** A voice profile of four sentences in `taxonomy.yml` did more to shape the essay than any prompt phrasing could. Averaging voices produces mush; naming them produces range.
- **Make the frontmatter contract executable.** Description length, title length, tag format, and date parity are all things a script checks better than a person does. Every rule that moves from a style guide into a linter stops being a review comment forever.
- **Derive filenames from titles by a stated rule.** The preview image path here is computed from the title by a documented slug rule, which means a retitle is a known event with a known consequence instead of a mystery of missing images.
- **Let CI be the reference build.** The workflow file is the one description of the build that is guaranteed to be current, because it runs. When the local instructions fail, read the workflow.
- **Forbid guessed links outright.** It is the single cheapest anti-hallucination measure available, and it costs one sentence.
- **Separate drafting from polishing, and give the polisher the rubric.** The value is not the second model. It is the second reading against the same written rules.
- **Treat the changelog as part of done.** An entry written while the change is fresh is a paragraph; written a week later it is archaeology.

The session ended with one essay, one changelog entry, one lint pass at zero errors, one production-stack build, and one pull request. Six words in, because everything else was already in the repository.
