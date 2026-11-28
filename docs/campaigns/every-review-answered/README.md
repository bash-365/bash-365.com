# Campaign — Every review answered

The campaign for BASH Consulting's reviews and reputation service. It makes one argument across research, articles, a demonstration, a deck and a real engagement: a local business should read every Google review, answer it in its own voice, and have a person approve each reply, and AI makes that affordable. It is written for any local business and uses restaurants as the worked example. A restaurant gets more reviews than most businesses, the reviews arrive during service, and a careless reply about an allergy or a refund costs more than silence.

This is the charter: the stages, where each piece lives, the rules every piece follows, and what has been done so far. Campaign id `every-review-answered`, the voice overlay in [`_data/characters.yml`](../../../_data/characters.yml); every piece carries the tag `google-reviews`.

## Thesis

A review is the most candid feedback a small business gets and the most public conversation it has. Leaving it unanswered is a queue nobody owns. Answering it at midnight, angry, is a control failure. The fix is the control finance already runs: a draft, a reviewer, an approval, a record. AI writes the draft, a person signs off, and the platform keeps the trail.

## Two tracks

| Track | What it is | Truth rule |
| --- | --- | --- |
| **The market** | The case that any local business needs this, made with restaurants: research, analysis, articles, the service page, LinkedIn | Every figure cites a source we opened ([research.md](research.md)). Demonstrations use fictional businesses only: Larkhollow Kitchen (a restaurant) and Quillfeather Plumbing & Heating. |
| **The client** | Beit Shawarma, Evanston, Illinois: the production-ready example, built as BASH would build it for a paying restaurant. The site rebuild is done; the reviews workflow is set up in code and waits on the owner. | Only public facts until the owner shares more. Beit Shawarma's name, reviews and figures appear in **no public BASH page, post or social copy** until the owner agrees in writing to be named. Until then it is a proposed engagement, never "a client". |

## The stages

| Stage | Deliverable | Where | Status |
| --- | --- | --- | --- |
| Research | Sourced facts on how people read and expect replies to reviews, what ratings and replies do to revenue, Google's rules, the law, the competitors | [research.md](research.md) | Done 2026-11-26 |
| Analyze | Who needs this and why, the restaurant deep dive, Beit Shawarma's public baseline, where BASH fits against the tools on the market | [analysis.md](analysis.md) | Done 2026-11-26 |
| Draft | The anchor article for owners, the service page made restaurant-first, LinkedIn copy | bash-365.com `pages/_posts/corp/`, `pages/_services/reputation.md`, [linkedin.md](linkedin.md) | Drafted; merge to publish |
| Present | A deck for a restaurant owner: the problem, the evidence, the workflow, the Beit Shawarma plan | A claude.ai Artifact (private; share by link) | Drafted |
| Demonstrate | The whole workflow recorded against a simulated profile for a fictional restaurant, replayed on the service page | zer0-CMS `content/reputation/simulator/restaurant.json`, `verify/demos/reputation/run.mjs --scenario restaurant`; bash-365.com `/services/reputation/` | Recorded live 2026-11-26 |
| Market | Article, LinkedIn on the BASH company page, the deck in owner conversations, the Beit Shawarma engagement as the case study once the owner agrees | bash-365.com, `drafts/linkedin/`, the deck | Waiting on the merges below |
| Price | Three tiers per location; the cost of AI, hosting, payments and BASH's time; how BASH bills and collects | [engagement-model.md](engagement-model.md), [billing.md](billing.md); prices and margins in a private claude.ai Sheet | Recommended 2026-11-26; prices wait on the maintainer |
| The client build | Beit Shawarma's site shows the reviews a person chose; the runbook, reply guidance and production checklist | bamr87.github.io `src/beit-shawarma/` ([REPUTATION.md](https://github.com/bamr87/bamr87.github.io/blob/main/src/beit-shawarma/REPUTATION.md)), [beit-shawarma.md](beit-shawarma.md) here | Built; waits on the owner |

## Where it lives

| Place | Carries | How it gets there | Approval |
| --- | --- | --- | --- |
| This folder | Charter, research, analysis, the engagement brief, queued LinkedIn copy | Pull request | Merging it |
| bash-365.com posts | Articles for owners. The anchor is a `corp` piece; later pieces may be `tech` how-tos | The content gate (`scripts/content_lint.py`) and a pull request | Merging it |
| `/services/reputation/` | The offer, with the restaurant demonstration | Pull request | Merging it |
| LinkedIn, the BASH company page | One post per article, after the article is live | `drafts/linkedin/`, copied from [linkedin.md](linkedin.md) when its article is on `main` | Merging the draft (merge publishes it at the next cadence slot) |
| zer0-CMS | The product: the reputation app, the restaurant scenario, the recorded demonstration | Its own branch and pull request | The maintainer merging |
| bamr87.github.io `src/beit-shawarma/` | The client build | Its own branch and pull request | The maintainer merging; the owner's go-ahead before launch |
| The deck | The presentation for a restaurant owner | A claude.ai Artifact | Shared only by the maintainer |
| The pricing model | Prices, margins, break-even, the founding-client offer | A claude.ai Sheet, kept out of this public repository because BASH doesn't publish fixed prices | Shared only by the maintainer |

## What the research changed (2026-11-26)

- **"AI drafts, a person approves" is not new.** Google's Gemini drafts replies for free for single-profile owners (since June 2026), and Toast's Reviews Agent drafts and waits for approval for Toast restaurants. Every piece says when the free option is enough, and argues the difference: approval that cannot be switched off, guidance written with the owner, no point-of-sale lock-in, team and multi-profile accounts.
- **No study shows a reply raises revenue.** Ratings move restaurant revenue (Luca; Anderson & Magruder); replies are argued from what customers expect (BrightLocal 2026) and from control, never from a promised star.
- **Google's API policy limits stored review content to 30 days.** The product has to answer it before a client goes live (zer0-CMS ADR 0014; analysis.md).

## Rules every piece follows

1. **Sourced or ranged.** A number comes from [research.md](research.md), with its source linked in the piece, or it is a range or it is cut. Vendor surveys are named as vendor surveys.
2. **No fake reviews, anywhere.** A demonstration review is invented only for a fictional business, and the page says so. Never invent a review, a testimonial or a rating for a real business, Beit Shawarma included.
3. **No real reviewer is quoted.** Public reviews of real businesses are counted, never quoted with a name.
4. **A person approves every reply.** No piece says or implies that the AI posts on its own.
5. **No promises about stars.** The service is every review read and every reply chosen, never a rating outcome.
6. **No review gating, no incentives.** Google and the Federal Trade Commission (FTC) both prohibit them; a piece that touches asking for reviews says so.
7. **The base voice holds.** Campaign moves are in the overlay; the house rules (one CTA, **Book a free consultation**, banned phrases, sentence-case headings) do not move.

## Beats

| # | Date | Event | Piece | LinkedIn | Status |
| --- | --- | --- | --- | --- | --- |
| 01 | 2026-11-26 | The reputation app gets a restaurant: research, analysis, demonstration, anchor article, deck, client build | "Your Google reviews are a queue nobody owns" (`corp`) | [linkedin.md](linkedin.md) § 01 | Branch `feature/reputation-campaign`, stacked on `feature/google-reviews` |

## Merge order

1. zer0-CMS `feature/google-business-profile` (the app, the restaurant scenario, the JSON export).
2. bash-365.com `feature/google-reviews` (the service page and the reviews band), then `feature/reputation-campaign` (this campaign, the article, the restaurant demonstration on the service page).
3. The LinkedIn draft for beat 01, once the article is on `main`.
4. bamr87.github.io `feature/beit-shawarma-reviews` (the client build), whenever the owner conversation is ready for it.

## Next

- **Owner conversation.** Show the Beit Shawarma owner the deck and the recorded demonstration; ask for manager access and the confirmations in REPUTATION.md; ask, separately and in writing, whether BASH may name the restaurant as a case study.
- **Google's approval.** File the Business Profile API access request for BASH's Cloud project. Nothing reaches real reviews until Google approves it.
- **Beat 02 candidates.** A `tech` how-to: writing a restaurant's reply guidance, with the template from the analysis. A `corp` piece: the FTC's review rule for a small business, what it forbids and what it means for asking for reviews.
- **Industries.** Restaurants are not in the "industries we speak to" table in `content-style.instructions.md`. If the campaign continues past beat 02, add the row there so every author has it; that is the maintainer's call.
