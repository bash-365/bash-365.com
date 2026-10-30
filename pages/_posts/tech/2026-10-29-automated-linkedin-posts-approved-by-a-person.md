---
title: "Automated LinkedIn posts, approved by a person"
sub-title: "An agent drafts, a person's merge is the sign-off, the pipeline sends it, and six weeks of green checks hid that it could not"
description: "Automate LinkedIn company-page posts and keep a person approving each one: drafts as files, a merge as the sign-off, and checks that go red when it breaks"
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-10-29T12:00:00.000Z
lastmod: 2026-10-29T12:00:00.000Z
draft: false
categories: [tech, ai]
tags: [automation, governance, agentic-ai, devops, smb, linkedin]
keywords: [automate linkedin company page posts, linkedin api approval workflow, linkedin posts api small business, ai drafted social media posts, github actions linkedin publishing, linkedin access token expiry, governed ai content workflow, denver it consultant]
preview: /images/previews/automated-linkedin-posts-approved-by-a-person.png
---

Most small businesses have more worth posting than they ever post. The write-up of last quarter's migration, the how-to a customer asked for twice, the lesson learned the hard way: it sits on the website and never reaches the company's LinkedIn page, because posting is a separate chore that starts from a blank box. The tools that take the chore away usually do it with a scheduler and a bulk queue, which is the opposite of what an owner wants from the account that speaks for the business.

Here is the pipeline we run for the BASH Consulting company page, and what we found this week when we checked whether it still worked. An artificial intelligence (AI) agent writes the first draft, a named person approves every post, and nothing reaches LinkedIn that a person did not sign off on. It runs on plain files in a Git repository, GitHub Actions for continuous integration (CI), and LinkedIn's Posts application programming interface (API).

## The rule: nothing posts without a person's approval

A company page is the business talking. A post that goes out unread, with a wrong claim, an invented number, or a tone you would never use, can be deleted, but not before people have seen it. So the design starts from one rule and works backward: a person approves every post, and the approval is a record rather than a habit.

Everything else can be automated because that rule holds. It is the same split we describe in [how we run the practice](/ai-operations/): rules live in files, agents draft, and people approve anything customer-facing.

## How a post moves from the website to LinkedIn

1. **A page goes live.** The pipeline lists every published post that has a title, a description, and a public address, and hasn't been shared yet.
2. **Someone asks for a draft.** A person, or an agent working for one, runs the draft command. It writes one Markdown file in `drafts/linkedin/`, marked `pending`, with a plain first draft taken from the page. An agent then rewrites it following a written procedure: the hook lands in about the first 140 characters, before LinkedIn's "see more" fold. It has exactly one call to action, two or three hashtags, no banned phrases, and nothing invented.
3. **A preview shows the exact request.** Before anything is sent, the preview prints the payload LinkedIn would receive, where the fold falls, the card image it would upload, the brand guard's findings, and every gate still closed. It makes no network call. LinkedIn does not scrape the link for this kind of post: the card's title, description, and thumbnail travel in the request itself, per the [Posts API documentation](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api). So what the preview shows is what LinkedIn shows.
4. **A person merges the draft.** The draft goes up as a pull request. The reviewer edits the copy in place and merges it. The merge is the approval, and the repository's history records who approved what, and when.
5. **The pipeline publishes what was merged, and only that.** A merge into `drafts/linkedin/` on the main branch starts the publish workflow. It re-reads the draft, re-checks every gate, uploads the card image, creates the post, and writes the identifier LinkedIn returns into a ledger.
6. **The ledger stops repeats.** The ledger is keyed by the page's address, so the same page never posts twice, whether the cause is a re-run or a second tool.

The whole draft is a short file a reviewer can read in one screen:

```yaml
---
type: article
status: pending
source: tech/2026-10-29-automated-linkedin-posts-approved-by-a-person
title: "Automated LinkedIn posts, approved by a person"
---
The commentary goes here. This body is exactly what posts.
```

## The gates, and what each one stops

| Gate | What it stops |
|---|---|
| Not approved | A draft nobody merged |
| Publishing not armed | Any run except the one publish step that is allowed to send. The switch lives in that step's environment, and no file in the repository can turn it on |
| Brand guard | A banned phrase, or commentary over 3,000 characters |
| Already published | The same page posting twice |
| Unconfirmed attempt | A second try after LinkedIn errored mid-request, when the first may have posted. A person checks the page before anything is sent again |
| No credential | Every live call, until a page admin issues a token |

Two of these exist because of how writes fail. A request that dies halfway may still have created the post, so the pipeline never retries a write after a server error, and it records the doubt before doing anything else.

## No model is load-bearing

The agent is optional. The first draft, the payload, the gates, and the ledger are plain code that behaves the same on every run. The model only improves text a person is about to read, and it never approves or publishes. That is [[The deterministic-first doctrine]] applied to a marketing channel: if the model is down or wrong, the worst outcome is a weaker draft waiting in a pull request.

## What we found when we checked

The question we asked was simple: if we merged a draft today, would it post? It would not have, for three reasons, and none of them showed up as a red check.

- **One missing brace silenced the settings.** In mid-September, a routine merge dropped a single closing brace from the site's settings file. The publisher did not crash. It fell back to its defaults, a different queue folder and a stricter approval status, so a merged draft would have been answered with "Nothing to publish" on a green run. Only the status command treated the file as an error.
- **The tool moved.** The content management system (CMS) behind the pipeline, our own open-source zer0-CMS, had been rewritten from Ruby to Python. The automated runs kept calling the right code, because they reach the CMS's shared workflow by name. Every command a person runs locally, and the connection our AI assistant uses to draft posts, still pointed at a file that no longer existed.
- **The checks stayed green.** The weekly token check skipped every Monday because no LinkedIn token was configured, and a skip reports as success. The weekly configuration check did catch the broken file. It flagged the file as invalid in seven consecutive weekly runs. It was set to report instead of fail, so all seven runs passed.

## What we changed

- **The configuration check can fail now.** It fails on an error, and it also runs on any pull request that touches the settings files, so a broken file stops at review instead of landing on the main branch. Warnings still only report.
- **One script knows where the tool lives.** A small wrapper is now the only file that knows where the CMS is checked out and which Python runs it. The drafting procedure, the command that starts it, the assistant's connection, and the docs all call the wrapper, so the next move upstream is a one-line change.
- **We validated on a real post: this one.** The status command reads the settings correctly, this article appears in the list of pages not yet shared, and the LinkedIn draft that shares it was written, previewed, and rehearsed locally through the same gates before anyone reviewed it.
- **The token stays a person's job.** LinkedIn access tokens last 60 days, and programmatic refresh is available only to a limited set of partners, per [LinkedIn's OAuth documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow). A page admin issues the token by hand. With the app's client ID and secret stored beside it, the weekly check fails a week before the token expires. Without them, it can only confirm the token still works. Until that token is in place, nothing posts. That is the gate doing its job.

## Watch-outs if you build this

- **Read the skip notices.** A scheduled check that skips for want of a credential usually shows green. Make a missing credential loud, or read the notice before you trust the badge.
- **Make a bad settings file fatal where it counts.** A tool that falls back to defaults is friendly on a laptop and dangerous in production. Check the file in every pull request that changes it.
- **Plan for LinkedIn's calendar.** LinkedIn publishes a new marketing API version every month and supports each one for at least a year before retiring it, per its [versioning documentation](https://learn.microsoft.com/en-us/linkedin/marketing/versioning). Posting to a company page also needs API access LinkedIn reviews on its own schedule. Setting up the repository side typically takes days. Apply for access before you start.

## Next step

If your business publishes good work that never leaves the website, we can set up the same pipeline for your company page, with your repository, your approval rules, and a token your own page admin holds. [Talk to us about governed AI automation](/contact/).
