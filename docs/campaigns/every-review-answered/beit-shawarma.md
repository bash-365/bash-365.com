# The Beit Shawarma engagement (proposed)

The client track of [Every review answered](README.md): what BASH Consulting would deliver to Beit Shawarma, 1601 Simpson St, Evanston, Illinois, and what is already built. It is a proposal. The owner has not yet agreed to the engagement or to being named, so nothing here goes on a public BASH page (charter rule, "Two tracks").

The operating detail lives with the restaurant's site source, in bamr87.github.io [`src/beit-shawarma/REPUTATION.md`](https://github.com/bamr87/bamr87.github.io/blob/main/src/beit-shawarma/REPUTATION.md): the flow, the setup steps, the reply guidance for the owner to confirm, and the production checklist. This page is the engagement around it.

## Why this restaurant is the right example

- **Its reviews are on Google.** 5.0 stars from 262 reviews on 2026-11-26, against 16 ratings on Apple Maps and 22 on Postmates. Google is where an answer is read, so Google is where the work goes.
- **The website now shows reviews; the old one didn't.** The old beitshawarma.com linked to no review anywhere. The rebuild (preview at bamr87.github.io/beit-shawarma) already links "Read our reviews" to Google, and now shows the reviews the owner chooses.
- **It is a small, owner-run restaurant.** One location, open daily from 11 AM to 10 PM, a menu where allergies and halal questions come up. That is the business the service is for: the person who could answer a review is the person running the counter.

## What BASH delivers

| Phase | What happens | What the restaurant does | What exists today |
| --- | --- | --- | --- |
| 0. Show | The deck and the recorded demonstration (a fictional restaurant, every reply approved by a person) | Watch; ask questions | Done: the demonstration on bash-365.com `/services/reputation/` and the deck |
| 1. Baseline | Count the owner's replies among the newest 20 Google reviews and the date of the newest one; read Yelp and Tripadvisor signed in; record it | Nothing, or sit in for ten minutes | Public half done (analysis.md); the signed-in count is outstanding |
| 2. Connect | The owner adds BASH as a manager on the Business Profile; BASH connects the location in zer0-CMS | One invite, about two minutes | Code done (the reputation app); waits on Google's API approval for BASH's project |
| 3. Guidance | BASH and the owner settle the reply guidance: sign-off, phone line, allergy rule, halal line, languages | Confirm the lines marked *confirm* | Drafted in REPUTATION.md |
| 4. Supervised start | Auto draft on, profile not armed, for two weeks: every new review gets a draft; BASH and the owner read them together and tighten the guidance | Read the drafts with BASH, about fifteen minutes a week | Ready |
| 5. Run | The profile is armed: the person with the right to respond approves and posts; the website shows the reviews they choose | Approve replies, usually within a day | The site's reviews band is built (bamr87.github.io `feature/beit-shawarma-reviews`) |
| 6. Review | Monthly: response rate, time to reply, reviews waiting, topics that pull ratings down, against the phase 1 baseline | A short monthly look | The platform's Insights view |

## What the restaurant owns and can leave with

- The Business Profile stays the owner's. BASH is a manager the owner can remove in one click.
- The reply guidance is a text the owner can paste anywhere.
- The website is a folder of static files the owner can host anywhere, and the reviews file is plain JSON.
- zer0-CMS is open source; the owner can run it without BASH.

## Acceptance

The engagement is done when every box in REPUTATION.md § "Ready for production when" is ticked, the first month's numbers are reported against the baseline, and the owner has approved at least one reply of each kind: praise, a complaint and a question.

## Open decisions (the maintainer's)

- **Price and terms.** Not set. The running cost is small (about $0.007 a review for the model in the recorded demonstration; Google's Business Profile APIs need no billing account); the cost is BASH's time and hosting. Price it against the free option the owner already has: Google's Gemini drafts replies for a single profile on a personal account (research.md § 4d).
- **Where the platform runs** for a client: BASH's hosted zer0-CMS, or the client's own.
- **The case study.** Ask the owner, in writing, after phase 5, whether BASH may name the restaurant and show its numbers.
- **Google's storage rule.** Google's API policy keeps stored review content to 30 days and forbids aggregating it (research.md § 4e.5). zer0-CMS ADR 0014 holds the decision; phase 2 does not connect a real profile until it is made.

## Say the free option first

In phase 0, tell the owner plainly: if they answer every review themselves from a personal Google account, Gemini plus the written guidance may be all they need. The engagement is worth more than that when a manager drafts or approves, when the guidance has to hold on every reply, when the restaurant wants its chosen reviews on its own site, or when it wants the monthly numbers. Saying so first is what makes the rest credible.
