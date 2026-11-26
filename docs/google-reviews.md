# Google reviews: BASH's Business Profile through zer0-CMS

How BASH Consulting's Google Business Profile is run: zer0-CMS's reputation app syncs the profile and its reviews, its `reputation` agent reads each new review and drafts a reply, a person approves every reply before it goes, and the reviews a person chooses appear on the homepage. It is an internal operations doc — `docs/` is excluded from the Jekyll build. The platform's design of record is zer0-CMS [`content/reputation/README.md`](https://github.com/bamr87/zer0-CMS/blob/main/content/reputation/README.md) and its ADR 0014; this page is what is specific to this site.

## What happens, end to end

| Step | Who or what | Where |
| --- | --- | --- |
| Reviews and the public profile are read from Google | zer0-CMS, hourly (and on **Sync now**) | Studio → Reputation → Profiles |
| A new review is read: sentiment, topics, whether a person should look soon | the `reputation` agent, when the profile is set to **Auto draft**; or on request | Studio → Reputation → Reviews |
| A reply is drafted in BASH's voice | the agent (auto draft), a person, or a Claude Code session here (`/review-reply`, the `google-review-reply` skill) | the review's panel |
| The reply's exact text is approved and posted | a person with `reputation.respond_review`, on an armed profile, on a platform with `ZER0_GBP_PUBLISH=1` | the review's panel → **Approve this text** → **Post to Google** |
| A review is chosen for the site | a person (**Show this review in the site's reviews file**) | the review's panel |
| The homepage shows the chosen reviews | `_data/reviews.yml`, downloaded from the profile and committed here in a pull request | `_includes/google-reviews.html`, inside the "Why businesses trust BASH" band |

Nothing in this repository posts to Google, and nothing on the site is written by hand: the reviews file is generated, and a reply is only ever a proposal until a person approves it in the studio.

## Setting it up (once)

1. **Google's side.** A Google Cloud project with the Account Management, Business Information and My Business APIs enabled, and Google's approval of the project for the Business Profile APIs — every one has a quota of zero until then. An OAuth client (web application) whose redirect URI is the platform's `/api/v2/reputation/oauth/google/`. Publish the consent screen: while it is in "Testing", Google expires the refresh token after seven days and the hourly sync stops.
2. **The platform's environment.** `GOOGLE_BUSINESS_CLIENT_ID` and `GOOGLE_BUSINESS_CLIENT_SECRET` (secrets, never in this repository); `ZER0_GBP_PUBLISH=1` only on the platform that may post to Google.
3. **The profile.** Studio → Reputation → Profiles → **Set up a profile** for the BASH site, **Connect with Google** as the account that manages BASH's Business Profile, choose the location, and paste the guidance below into **Guidance for every reply**. Turn on **Auto draft** for the agent to draft each new review's reply; turn on **Armed** only when replies may go.
4. **People.** Whoever answers reviews for BASH gets `reputation.respond_review`; whoever manages the connection gets `reputation.change_profile`.

### Where setup stands (2026-11-26)

- **Google Cloud:** project `bash-365-reputation` in the bashconsultants.com Workspace organization, no billing linked. The Account Management and Business Information APIs are enabled. The v4 My Business API, which serves reviews and replies, refuses to enable until Google approves the project's Business Profile API access request. That form is still to be filed by the account owner, and nothing reaches reviews until Google approves it.
- **Consent screen:** app "BASH Reputation", audience **Internal**, one scope (`business.manage`). Internal means only bashconsultants.com accounts can connect. If BASH's Business Profile is managed by an account outside that Workspace, the audience has to become External, which brings Google's verification for this sensitive scope.
- **OAuth client:** a web client for the local platform with one redirect URI, `http://localhost:8000/api/v2/reputation/oauth/google/`; open the studio at `http://localhost:8000/studio/` so the session that started the connection is the one Google returns to. Its ID and secret live only in the local zer0-CMS `.env`, never in a repository.
- **Not set:** `ZER0_GBP_PUBLISH` (replies stay unpostable until someone decides) and `ZER0_GBP_SIMULATOR`.
- **Still waiting:** the platform's reputation app reaching zer0-CMS's `main` (or a local rebuild from its branch) before a real connection can be tested.

## The reply guidance

The profile's guidance is what the agent follows on every reply, on top of the site's voice that the platform already gives it. For BASH, from the brand SSOT ([`.github/instructions/brand.instructions.md`](../.github/instructions/brand.instructions.md)) and the contact details in [`_data/entity/info.yml`](../_data/entity/info.yml):

```text
Speak as BASH Consulting, one practitioner to another: plain English, no pitch, no hype, no exclamation marks.
Thank the reviewer by first name and answer what they said in two to five sentences.
For a problem, acknowledge it without arguing and invite them to continue by email at info@bash-365.com or by phone at 720-352-4641.
Never describe the engagement, the client's systems or a result the review does not state; never confirm someone is a client if their review does not.
Never offer a refund, a discount or a guarantee. No call to action beyond that contact line.
Sign off as "Amr, BASH Consulting".
```

Change it in the studio; if the brand's voice or contact details change, update both this block and the profile's guidance in the same pull request that changes them.

## The reviews on the site

[`_includes/google-reviews.html`](../_includes/google-reviews.html) renders the first three reviews in [`_data/reviews.yml`](../_data/reviews.yml) inside the homepage's proof band (`_layouts/landing.html`), with Google's average and count and the attribution "Reviews from Google" linking to the profile. It renders **nothing** while the file holds no review, which is how it ships.

To change what it shows: choose reviews in the studio (**Show this review in the site's reviews file**), then **Download reviews.yml** from the profile — or on the platform's machine, `python manage.py reputation export --profile <uuid> --out <this checkout>/_data/reviews.yml` — and commit it here on a branch, through a pull request like any other change.

What the file and the include will not do, on purpose:

- **Show a review nobody chose**, or one that has left Google. A person's choice in the studio is the gate; the file is generated from it.
- **Show a full name.** A reviewer appears as their first name and last initial.
- **Edit a customer's words.** The text is escaped and, past sixty words, shortened with an ellipsis — never rewritten.
- **Add review markup.** Google gives no review stars to a business's reviews of itself on its own site, so `Review` / `AggregateRating` structured data would claim more than it earns.

## Drafting from Claude Code

`/review-reply <review id>` runs the [`google-review-reply`](../.claude/skills/google-review-reply/SKILL.md) skill: it reads the review through zer0-CMS's MCP endpoint as the `reputation` agent, records its analysis, and proposes a reply — with a token minted for those three tools only, so it cannot post. The skill says how to mint the token and add the server to your own Claude Code config; the token never goes into this repository's `.mcp.json`.

## The demonstration on /services/reputation/

The service page replays a recorded run of the platform, not BASH's profile. zer0-CMS's `verify/demos/reputation/run.mjs` starts a simulated Business Profile — a local stand-in for Google's API, for a fictional business with invented reviews (`--scenario restaurant` for Larkhollow Kitchen, a neighborhood restaurant, which the page shows; the default is a plumber) — and a throwaway platform. It then plays the whole story in a browser: connect, read the backlog, auto-draft for new reviews, edit, approve, post, measure, edit the profile. It screenshots every step into zer0-CMS's `test/evidence/reputation-demo-<scenario>/`. The drafts were generated live by the platform's reputation agent and recorded, so `--model recorded` replays them exactly.

To refresh the page after a new run:

```bash
python3 scripts/demos/import_reputation_demo.py --evidence ../zer0-cms/test/evidence/reputation-demo-restaurant   # Pillow for the images
```

It writes `_data/demos/reputation.json` (each review, the agent's reading and draft, what a person added, what was posted) and the cropped WebP screenshots in `assets/images/reputation/`, plus the page's preview banner. Commit the three together with the zer0-CMS evidence they came from. Never edit the data by hand, and never replace the simulated business with a real one: the page says on its face that the business and reviews are fictional.

## What is not here yet

- Questions and answers: Google shut its Q&A API down on 2025-11-03.
- Google Posts (sharing the site's articles as profile updates), the profile's performance metrics, and push notifications for new reviews: possible later steps on the platform, each a row in zer0-CMS's capability ledger.
