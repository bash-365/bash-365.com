# Engagement model — the review service as a service and a portal

How BASH Consulting sells [Every review answered](README.md): the tiers, what each costs to run, where the money is made, and the choices that set those costs. [billing.md](billing.md) covers how BASH charges for it and collects.

The prices, margins, break-even and the Beit Shawarma offer live in the private pricing model, a claude.ai Sheet the maintainer shares by link. They aren't here because this repository is public and BASH doesn't publish fixed prices ([`pages/_services/index.md`](../../../pages/_services/index.md)). Everything below is either a sourced market or vendor fact, or a property of the model that holds whatever the prices are.

## What we sell

One subscription per Google Business Profile location, in three tiers, plus a one-time setup fee per location. The client always keeps the profile, the reply guidance and their website. The platform is zer0-CMS's reputation app ([ADR 0014](https://github.com/bamr87/zer0-CMS/blob/main/docs/adr/0014-reputation.md)).

| Tier | Who approves replies | What BASH does | For |
| --- | --- | --- | --- |
| **Portal** | The owner, in the studio | Connects the profile, starts them on the template guidance, answers email | An owner who answers reviews personally and wants the queue, AI drafts and a record of every reply |
| **Guided** | The owner or a manager they name (up to three people) | Writes the guidance with the owner, runs the two-week supervised start, puts chosen reviews on the website, sends the monthly report, holds a quarterly call | Most restaurants |
| **Done for you** | BASH, under the owner's written authorization; the owner decides 1- and 2-star reviews and anything flagged | Everything in Guided, plus reading every draft and approving it within one business day, and a monthly call | Busy or multi-location operators |

- **Terms:** monthly, or annual paid up front with two months free.
- **Done for you** includes a monthly number of reviews per location and charges a set price for each one beyond it.
- **Add-ons:**
  - The website reviews band, for a site BASH didn't build.
  - A dedicated instance of the platform in the client's own cloud account.
- **Models:**
  - Every review is read and drafted by Claude Sonnet 5.5.
  - From Guided up, 1- and 2-star reviews and anything flagged (an allergy, an injury, a legal threat, personal details) go to Claude Opus 5.5.

**Done for you and Google's policy.** Google's Business Profile API policy forbids triggering a reply "without the user's prior specific and express consent" ([research.md § 4e](research.md)). In Done for you the consenting user is a named person at BASH, a manager on the profile, approving each specific reply, under a standing written authorization the owner signs and can revoke. The escalation list (which reviews go back to the owner) is part of that authorization.

## What it costs to run

### AI: under 1% of the price

The recorded restaurant run on 2026-11-26 made 12 calls to Claude Sonnet 5.5, one per review, for $0.0867: $0.0072 a call. Each call read about 2,000 tokens and wrote 192 to 376. At Anthropic's list prices ([pricing](https://platform.claude.com/docs/en/about-claude/pricing)):

| Model | Input / output, per million tokens | One review, one call |
| --- | --- | --- |
| Claude Haiku 5.5 | $0.10 / $0.50 | about $0.0004 |
| Claude Sonnet 5.5 | $2 / $10 | about $0.007 |
| Claude Opus 5.5 | $4 / $20 | about $0.020, allowing for its thinking |

Twenty-five reviews a month cost about $0.50 a location, counting:

- a quarter of drafts asked for a second time;
- 15% of reviews on Opus 5.5;
- a monthly insights summary;
- a quarterly replay of 150 test reviews whenever the guidance changes.

That is under 1% of revenue in every tier. Switching to Haiku 5.5 would save cents and cost quality on the reviews that matter, so the model choice is made for quality.

### Where each AI loop runs

| Loop | Harness | Decision |
| --- | --- | --- |
| Reading and drafting each review | Messages API through zer0-CMS's `anthropic` provider, billed per token on an API key | **Production.** A draft is one structured call; there is nothing to orchestrate. |
| Guidance tests and monthly insights | Message Batches API, half price | **Use.** Nobody waits on them. |
| Repeated instructions | Prompt caching (cache reads at 5% of the input price on Sonnet 5.5) | **Later.** An hourly sync of one restaurant rarely reuses a five-minute cache; it pays once many reviews arrive together. |
| Today's reputation agent | Claude Agent SDK, zer0-CMS's `claude_code` provider | **Development and demos only.** Anthropic does not allow a claude.ai login in products offered to customers ([Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)), so client traffic can't run on a Claude Code OAuth token. |
| Long autonomous jobs | Managed Agents: tokens plus $0.08 per session-hour | **Not needed.** A draft is one call; runtime would buy nothing. |
| BASH's own build, demos and content loop | Claude Code on a Claude plan (Max from $100 a month, [claude.com/pricing](https://claude.com/pricing)) | **Internal overhead.** Never carries client traffic. |

### Hosting: one small server carries dozens of clients

The platform is a Django web process, a Celery worker and scheduler, Postgres with pgvector, and Redis. Monthly list prices, 2026-11-26:

| Option | Monthly | What it is |
| --- | --- | --- |
| **One DigitalOcean server** (recommended to start) | about $73 | A 4 GB Droplet running the whole compose stack ($24), off-site backups in Spaces ($5), Postmark email ($15), Sentry error tracking ($29). The 8 GB Droplet is $48 when it's needed. |
| Managed Azure | about $117 | Container Apps on consumption pricing, PostgreSQL Flexible Server B1ms, Azure Managed Redis B0 (Azure Cache for Redis Basic stopped taking new customers in April 2026), the same email and error tracking |
| Render | about $123 | Web service and worker at 2 GB, Postgres 1 GB, Key Value, the same email and error tracking |

Hetzner is out: its June 2026 price change moved US plans above DigitalOcean's. Google's Business Profile APIs need no billing account.

### BASH's time: the real cost

What it costs to serve a client is mostly BASH's time. The model assumes:

- setup, a few hours per location;
- a tenth of an hour a month for Portal;
- more than half an hour for Guided;
- for Done for you, three minutes a review on top.

Platform operations (updates, backup checks, monitoring, Google API changes) take about four hours a month whatever the client count. Professional liability cover for a service that posts on a client's behalf needs a quote.

## What the model shows

These hold across reasonable prices; the Sheet has the figures.

- **Margins fall as BASH does more**, from Portal to Guided to Done for you. Each tier's effective hourly rate falls in the same order.
- **Done for you is limited by hours, not tokens.** It's the tier that fills BASH's week, and the one to cap or price per review.
- **Break-even comes after a handful of clients.** Until then, the four hours of platform operations a month outweigh everything else.
- **Payment fees outweigh AI.** On a Guided client paying by card, the processor's fee is more than ten times the month's AI cost ([billing.md](billing.md)).

## The market the prices answer to

| Kind | Examples | Price | Source |
| --- | --- | --- | --- |
| AI reply tools | RepliFast | $29 a month | [replifast.com](https://replifast.com/pricing) |
| Self-serve review platforms | BrightLocal Grow | $65 a month ($49 billed annually) | [brightlocal.com](https://www.brightlocal.com/pricing/) |
| Self-serve review platforms | Reputation Rep Core | $80 per location | [reputation.com](https://reputation.com/pricing/) |
| Self-serve review platforms | GatherUp, Grade.us | $99 | [gatherup.com](https://gatherup.com/pricing/), [grade.us](https://www.grade.us/home/plans/) |
| Self-serve review platforms | NiceJob | $95 to $135 | [nicejob.com](https://get.nicejob.com/pricing) |
| Larger platforms | Birdeye | about $299 to $449 | estimate, [SocialPilot](https://www.socialpilot.co/reviews/blogs/birdeye-pricing) |
| Larger platforms | Podium | about $399 to $599 | estimate, [eesel](https://www.eesel.ai/blog/podium-pricing) |
| Larger platforms | Toast IQ Grow | reported $499 a month at launch | [Pulse 2.0](https://pulse2.com/toast-iq-grow) |
| Agencies | Restaurant range | $149 to $249 a month, setup $250 to $1,000 | a review-software vendor's recommendation, [EmbedMyReviews](https://www.embedmyreviews.com/resources/pricing-reputation-management-services/) |
| Agencies | WebFX, one location | $125 a month plus $500 | [webfx.com](https://www.webfx.com/review-management.html) |
| Managed replies | Marqii | from $100 for 50 reviews | [marqii.com](https://marqii.com/pricing) |
| Free | Google's Gemini | drafts replies for a single profile on a personal account | [research.md § 4d](research.md) |

BASH can't win on price per reply: Marqii sells managed replies for about $2 each. The case is the one the campaign makes:

- a person approves every reply;
- the guidance is written with the owner and holds on every draft;
- there's no point-of-sale lock-in;
- the reviews appear on the client's own site;
- the platform is open source, so the client can leave with it.

## Decisions for the maintainer

1. **The prices.** The Sheet recommends a price for each tier and a founding-client offer for Beit Shawarma; nothing reaches a client until you set them.
2. **The cost of an hour of BASH time.** Every margin in the Sheet moves with it.
3. **Whether Done for you launches now.** It's the most labor and the most policy-sensitive tier.
4. **Production AI on an API key.** Point the reputation agent at the `anthropic` provider before the first real client. That's a zer0-CMS change.
5. **Google's 30-day storage limit.** It still blocks any real profile (zer0-CMS ADR 0014).
6. **A quote for professional liability cover.**
