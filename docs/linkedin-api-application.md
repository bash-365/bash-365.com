# LinkedIn Community Management API — application answers

The text we submit for the LinkedIn Developer application. The form asks two things: one description of the business and product, then a per-use-case description for each capability we request, plus a screen recording.

> *Tell us about your business and the product that will leverage Community Management API access. Please provide a detailed description otherwise your application will be rejected.*

> *For each use case below, please provide a detailed description. What use case does your organization plan to enable with the Community Management APIs?* **Page management** — create and manage company posts, comments, and reactions, and monitor engagement. **Profile management** — the same, on behalf of individual profiles. **Page analytics** — track post analytics and performance.

> *Please provide a screen recording of the application for this submission.*

The app under review is **zer0-CMS**. The component that talks to LinkedIn is its distribution app — the LinkedIn client in `content/distribution/linkedin/` and the governed pipeline in `content/distribution/lane/` (for a site kept as files) and `content/distribution/` (the platform's queue, ledger and statistics) of [bamr87/zer0-CMS](https://github.com/bamr87/zer0-CMS). Its design of record, including the complete list of LinkedIn calls it can make, is [`docs/DISTRIBUTION.md`](https://github.com/bamr87/zer0-CMS/blob/main/docs/DISTRIBUTION.md). This site is its first user: `zer0.json` → `distribution.linkedin`.

**Read this before editing.** Four things carry the application, and weakening any one turns it into a request LinkedIn refuses: every post is approved by a person before it can publish; each account is authorized by its own owner's consent; the audience someone writes for is decided by them and never derived from LinkedIn data; and everything read back is the author's **own aggregate** numbers. Keep what runs and what is planned apart, and keep "implemented" apart from "run against LinkedIn": page publishing has run live, while the member and statistics calls are implemented and tested against LinkedIn's documented shapes but cannot have run live before the grant this application asks for.

## Business and product (paste as plain text)

**Our business.** BASH Consulting LLC is a Denver, Colorado software and information technology (IT) consultancy serving small and medium-sized businesses. We build and run the systems a business depends on — cloud infrastructure, Enterprise Resource Planning (ERP) and accounting platforms, data architecture, and automation with an artificial intelligence (AI) overlay — and we build content tooling alongside the client work, in the open, at https://www.bash-365.com. The practice is owner-operated by Amr Abdel-Motaleb.

**The product: zer0-CMS.** A content management system for sites kept as files in the owner's own repository rather than as rows in someone else's database. It indexes and edits a site's pages, illustrates them, checks them against the site's own rules, and — through its distribution lane — carries them to LinkedIn and reads back how they did. It runs as a command-line tool, as a browser application the owner runs themselves, inside continuous integration, and as a Model Context Protocol server for AI assistants. It is open source.

**Who it is for.** Any business or individual with something worth reading and no publishing operation to push it out: a consultancy sharing what it has learned, a small business owner explaining their trade, a developer or a team whose release notes deserve an audience. It does not assume a marketing department, because the people who need it most do not have one.

**The problem it solves.** People who make things write a great deal as a byproduct — guides, explanations, release notes, answers to a question a customer asked twice — and almost none of it reaches anyone, because "write a LinkedIn post" is a separate task with a blank page. When they do post, they cannot tell which subjects landed, so the next choice is a guess.

**How it works, concretely.** The CMS lists a site's pages that are fit to share: published, titled, described, with a public URL, and not already shared. Choosing one writes a draft into a queue folder in the owner's repository, marked pending, with a plain first commentary taken from the page. A person rewrites it and approves it. Before anything is sent, the CMS shows the exact request it would make — the payload, the point where LinkedIn folds the text, and every check that would stop it: a banned phrase, a draft nobody approved, a page already shared. Publishing uploads the page's existing preview image for the link card, creates the post, and records the returned URN in a ledger keyed by the page's address, so the same page is never posted twice by any surface.

**The loop closes with analytics.** The CMS reads back the aggregate statistics of the author's own posts — impressions, clicks, reactions, comments, shares — joins them onto the pages that produced them through that ledger, and writes them into the site, where the editor turns them into a list of what to write next: strong pages never shared, subjects that earned attention, subjects that did not, and pages that performed and have gone stale. The CMS can already tell a page is thin or out of date, because that is in the file. It cannot tell which subject an audience cares about. That is the gap the analytics use case closes.

**Status, stated plainly.** The distribution lane is built and in use. Page publishing has run live: this site's company page (urn:li:organization:64517157) has been published to by the lane's predecessor, and the rebuilt lane speaks the same Posts API payload, verified byte-for-byte against it; the current Python lane is held to that payload by tests over the rebuilt lane's recorded output. The member publishing call, the page-role check, the page statistics read and the member post statistics read are implemented against LinkedIn's documentation and tested against its documented request and response shapes, with no network; they have not run against LinkedIn, because they need the access this application requests. Nothing in the product invents a number meanwhile: a call the token may not make is refused with LinkedIn's own error. Reading and replying to comments is not built.

**Volume.** Low by design. The product publishes considered posts about real work — a few per author per month. Nothing publishes on a schedule: there is no bulk mode, no queue-ahead and no timed release, so nothing in it rewards or enables volume. The only scheduled calls are reads: the statistics for posts the product published, once a day, and a weekly check that the token still works.

**Our privacy policy is at https://www.bash-365.com/privacy/.**

## Use-case answers (paste as plain text, one per box)

### Page management

A business publishing its own content to its own LinkedIn page, with a named person approving every post.

What we do with it. Create posts on a page the authenticated member administers, via POST /rest/posts with author urn:li:organization:{id}: a link share of a page from the organization's own site, with the card's title, description and thumbnail set in the request and the thumbnail uploaded through the Images API. We confirm the member's role on that page through organizationAcls before posting rather than asserting it, read the post back with GET /rest/posts/{urn}, list the page's own recent posts, and record each post's URN in a ledger keyed by the page's address so the same page is never posted twice.

Scopes requested: w_organization_social and r_organization_social, and rw_organization_admin for the page-role check and the page's statistics — only for pages the authenticated member administers, verified through LinkedIn.

The approval gate, which is the part we would ask a reviewer to look at first. A draft is created pending and is inert. It can publish only after a person approves it — a click in the CMS, a command, or merging the draft in the site's repository — and the publish step re-reads the draft and re-checks every condition before it sends anything. Publishing also has to be switched on in the environment of the process doing it; nothing in a repository's files can switch it on. Nothing publishes on a schedule: there is no queue-ahead, no timed release and no unattended mode.

Comments and reactions. Planned, not built: letting a page answer replies to its own posts from the same place the post was written, with a person reading and sending every reply, and hiding spam on its own threads. There is no automated replying, liking or reacting, and none is planned.

### Profile management

An individual publishing their own work to their own LinkedIn profile, with their approval on every post. For a sole trader, a consultant or a developer, the profile is where their audience is — often there is no page at all.

What we do with it. Create a post on the authenticated member's own profile via POST /rest/posts with author urn:li:person:{id}, from a draft that member approved; learn their own member id through the OpenID Connect userinfo endpoint; and read the aggregate statistics of that member's own posts.

Scopes requested: openid and profile to identify the member who consented, w_member_social to publish, and r_member_postAnalytics to read their own posts' statistics.

Consent. Each person connects their own account through their own three-legged OAuth consent and can revoke it from LinkedIn at any time. The CMS stores that token encrypted, never displays it, and holds no credential that lets it act as a member who has not personally authorized it. There is no administrative path, impersonation mode or shared token that could produce one.

What we will not do, and have not built. We will not post, comment or react as any member who has not personally authorized it. We do not read other members' profiles, connections, followers or feeds, and do not message anyone. There is no automated engagement of any kind. We do not scrape LinkedIn. Member data is not sold, shared or used to train a model.

On audience, because the words invite a wrong reading. The tool helps someone write for readers they have in mind; it does not identify, enumerate, segment or target members, and it derives nothing from connections or followers. The complete list of LinkedIn calls the product can make is printed by the product itself, and a test fails the build if any call on it returns data that is not the author's own.

### Page analytics

This is what closes the loop, and it is the reason the product exists rather than a reporting add-on.

What we read. Lifetime aggregate statistics for the author's own posts: for a page, organizationalEntityShareStatistics for the posts that page published through the product (impressions, clicks, likes, comments, shares), requested in batches by post URN; for a member, memberCreatorPostAnalytics for each of their own posts (impressions, reactions, comments, reshares, link clicks). That is the entire read surface for analytics.

What the author gets. Their own numbers, joined back onto their own pages through the publish ledger, and written into the site as the input to a worklist of what to write next — which subjects people read, which they did not, and which pages performed and have since gone stale.

Boundaries. Statistics stay aggregate and belong to the author whose content produced them. We do not build profiles of members, do not try to identify anyone inside a count, do not join LinkedIn metrics to any other dataset about a person, and do not show one author's numbers to another. Nothing is sold or shared, and no LinkedIn data trains a model. Only the posts the product published are read, and only the fields named above are kept.

## Screen recording (what we submit and what it shows)

To record against zer0-CMS's studio, its **Distribution** area (`/distribution`): a site's pages not yet shared; **Compose a post** writing a draft; the draft screen showing the commentary with LinkedIn's fold, the brand guard, the gates, and the exact POST /rest/posts request with its author URN; a person clicking **Approve**; and the gates clearing. The prototype recording on the `claude/linkedin-community-api-desc-so9f8u` branch showed the same approval flow in an earlier interface and is superseded by this one.

The recording shows a post reaching LinkedIn only if it is made with access LinkedIn has granted, and it says which. It does not stage or fake a success.

## If we are asked for more

- **What exists vs. what is planned.** Running: the queue, the approval gate, the brand guard, the exact-request preview, the page and member publishing client, link-card image upload, the page-role check, the page and member statistics reads, the ledger, the statistics join, the CI workflow, the browser screens and the MCP server. Run live against LinkedIn: page publishing. Planned, not built: reading and replying to comments; moderating a page's own threads.
- **The call surface.** `manage.py linkedin plan` prints every LinkedIn call the product can make, with the scopes each needs and what it returns. The client accepts a call only from that list.
- **No model is required anywhere in the path.** Listing, drafting, the payload, the checks and the statistics join are plain deterministic code. A language model can improve a draft a person is already reading. It is never the only way to get one, and it never publishes or approves.
- **Where credentials live.** In the environment for the command line and continuous integration (a gitignored local file, or CI secrets); encrypted in the CMS database for an account connected through the browser. Never committed, never logged, never shown.
- **Idempotency and rate.** One page produces one post: the ledger is keyed by the page's address, and a page already in it is refused. Writes are not retried after a server error, so a post cannot be sent twice by a retry. Volume is bounded by how often the author approves a post.
- **The code.** [bamr87/zer0-CMS](https://github.com/bamr87/zer0-CMS) — `content/distribution/linkedin/` (the client, on httpx) and `content/distribution/lane/`, in Python, and the tests in `content/tests/distribution/` (`test_linkedin.py`, `test_lane.py`, `test_platform.py`), which run against recorded responses, never LinkedIn.
