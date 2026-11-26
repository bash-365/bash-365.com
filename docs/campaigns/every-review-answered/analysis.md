# Analysis — who needs every review answered, and why restaurants first

The analyze stage of [Every review answered](README.md). It turns [research.md](research.md) into the campaign's argument: the need any local business has, why restaurants show it most clearly, where Beit Shawarma stands, and where BASH fits against the tools already on the market. Figures come from research.md, which links each source.

## The need, for any local business

Three things are true of every business with a Google Business Profile:

1. **The profile is where a new customer decides, and they expect an answer.** 97% of consumers read reviews of local businesses; 89% expect the owner to respond, 32% by the next day; 68% will only use a business with four stars or more (BrightLocal 2026, vendor-run; research.md § 1).
2. **Ratings move revenue; replies change the conversation.** A one-star Yelp increase means 5–9% more revenue for independent restaurants, none for chains (Luca), and an extra half-star makes restaurants sell out 19 percentage points more often (Anderson & Magruder). Replying is a weaker claim: hotels that start replying gain about 0.12 stars and 12% more reviews, and one study finds replies draw more negative reviewing. No study found that replying raises restaurant revenue (research.md §§ 2–3). The campaign argues from expectation and control, never from a promised star.
3. **Nobody owns the queue.** Only 51% of small-business owners say they respond to reviews (60% in food and drink; BrightLocal 2026, research.md § 6.4). Reviews arrive at any hour, the hardest ones need the calmest answer, and the person who could answer is doing the work the review is about.

What changes between kinds of business is the reply that does damage:

| Kind of business | What reviews are about | The reply that does damage | The guidance line that prevents it |
| --- | --- | --- | --- |
| Restaurant | Food, wait, service, delivery, price and fees, allergies, noise | Saying a dish is safe for an allergy; promising a comp; blaming a delivery driver | Never claim allergen safety; never promise refunds or free food; send problems to the manager by phone |
| Trades (plumbing, heating, electrical) | Punctuality, price surprises, cleanliness, emergencies | Arguing over an invoice in public; promising free work | Apologize once; take the invoice to a phone call |
| Clinic or dental office | Wait times, billing, staff, outcomes | Confirming the reviewer is a patient, or discussing their care | Never confirm a relationship or mention care (research.md § 5, HIPAA) |
| Multi-location retail or restaurant group | The same complaints at several locations | Each location answering differently, or not at all | One guidance for the brand, a person per location to approve, insights across locations |
| Professional services | Responsiveness, fees, outcomes | Confirming a client relationship; discussing a matter | Never confirm the engagement; invite a private conversation |

## Why restaurants are the worked example

- **Diners read reviews more than anyone.** In BrightLocal's last survey with an industry breakdown (2020), restaurants were the category consumers most often read reviews for: 93% (research.md § 1.18). It is six years old; no newer edition breaks restaurants out.
- **The work and the reviews collide.** Reviews arrive during lunch and dinner service and after close: exactly when the owner is on the line or counting the drawer.
- **The stakes in a reply are physical.** An allergy question answered wrongly is a safety and liability problem, not a tone problem. That makes the case for a person approving every reply easy to see.
- **Delivery adds a third party.** A cold delivery is often the courier's delay, and blaming the app in public reads as an excuse. The guidance has to own the problem and move it to a phone call.
- **Fees are a live complaint.** Service charges, large-party gratuities and delivery markups show up in reviews; the reply has to explain without arguing.
- **Many restaurants serve guests in more than one language.** A reply in the guest's language is good service, and it needs a person who reads that language to approve it.

The demonstration's fictional restaurant, Larkhollow Kitchen, carries each of these: a late, cold delivery; a peanut-allergy question posted with the guest's phone and address; an undisclosed service charge; noise; a party; catering; a review in Spanish; and one review that tries to give the AI orders. In the recorded run (2026-11-26) the agent flagged the three that needed a person, drafted replies that made no safety claim and repeated no personal detail, and refused the injected instruction; a person added one line before posting the delivery reply.

## Beit Shawarma's baseline (public, 2026-11-26)

From the baseline agent's signed-out reading (kept in the session's scratchpad; nothing here names a reviewer or quotes a review):

| Listing | Reading |
| --- | --- |
| Google | 5.0 stars from 262 reviews; primary category Mediterranean restaurant; hours, phone and website agree with the rebuilt site |
| Apple Maps | 100% from 16 ratings (food, service and atmosphere each 100%) |
| Postmates (Uber) | 4.2 from 22 ratings |
| Yelp, Tripadvisor, DoorDash, Uber Eats | Not read: each blocked automated reading |
| The old website | No link to any review |

What it means for the proposal:

- **Google is the channel.** It holds more than ten times the reviews of any other listing that showed a count.
- **The rating is not the problem; the queue is.** At 5.0 the case is not repair. It is keeping every guest who took the time to write answered, and catching the first hard review before it sits.
- **The reply rate is unknown.** Google shows signed-out visitors a limited view with no review list, so the share of reviews with an owner reply could not be counted. That count, done signed in, is phase 1 of the engagement ([beit-shawarma.md](beit-shawarma.md)).
- **The website now helps.** The rebuild links to the Google listing and, once the owner chooses reviews, shows them; the old site had neither.

## Where BASH fits

"AI drafts, a person approves" is not unique any more (research.md § 4d and § 7):

| Option | Drafts with AI | A person must approve | Fit |
| --- | --- | --- | --- |
| Google's Gemini web app (since June 2026) | Yes, free | Not documented | One verified profile, personal Google account, outside the EEA and UK |
| Toast Reviews Agent | Yes, Google reviews only | Always | Restaurants on Toast with the IQ Grow package per location; no tone, voice or blocked-term settings |
| Birdeye | Yes | Configurable; its product page auto-publishes 4- and 5-star replies | Multi-location; price not published |
| Yext | Yes | Configurable; can auto-send | Multi-location; price not published |
| Reputation | Yes | Not stated | $80 per location per month and up |
| Podium | Yes | Not stated | Price not published |

The position the campaign takes, supported by those sources:

- **Say when the free option is enough.** A single-location owner who answers reviews personally from a personal Google account can start with Gemini and the guidance template. Saying so is the brand's "people over profits" in practice, and it makes the rest of the pitch credible.
- **Approval is mandatory, not a setting.** zer0-CMS cannot post a reply nobody approved, and a changed word needs a new approval. That also satisfies Google's API policy, which forbids triggering replies "without the user's prior specific and express consent" (research.md § 4e.4).
- **The guidance is written with the owner.** The rules that matter for a restaurant (allergy, comps, delivery) are in the guidance from day one. Toast's agent cannot set tone or blocked terms.
- **No point-of-sale lock-in, and team accounts work.** Toast needs its own package per location; Gemini excludes work accounts and anyone managing more than one profile.
- **Open and portable.** zer0-CMS is open source; the guidance is plain text; the reviews file is plain JSON. The owner can leave with all of it.

## A constraint the product has to answer before production

Google's Business Profile APIs policy says review content may be stored "temporarily for no more than 30 calendar days" and "cannot be manipulated or aggregated in any way" (research.md § 4e.5). zer0-CMS's reputation app keeps every synced review, computes insights from them, and exports chosen reviews into a file a website commits. Before any client goes live, one of these has to be decided and recorded in zer0-CMS's ADR 0014:

- keep review text only as long as the policy allows (purge or re-fetch within 30 days) and compute insights on the fly, or from data that is not review content;
- have the website's reviews band refresh from the platform within the window instead of committing review text to the site's repository;
- or obtain Google's written agreement for longer storage.

This is the maintainer's decision. Until it is made, the client checklist in REPUTATION.md stays open on it.

## The offer, in one paragraph

BASH connects a restaurant's Google Business Profile to zer0-CMS, writes the reply guidance with the owner, and runs two supervised weeks before anything posts. After that every new review is read within the hour, a reply is drafted in the owner's voice, and the owner (or whoever they name) approves the exact text before it goes. The reviews the owner chooses appear on their own website, and once a month the numbers say what guests keep saying. The owner keeps the profile, the guidance and the website.
