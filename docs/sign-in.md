# The sign-in page

> How a visitor gets from bash-365.com into an application on the hosted platform, and how to open the page for the first one.

BASH's platform (zer0-CMS first, then each application behind it) is hosted on Google Cloud and entered through this site. The decision is ADR 0020 in the hub, [bamr87/bamr87 `docs/adr/0020-platform-on-google-cloud.md`](https://github.com/bamr87/bamr87/blob/main/docs/adr/0020-platform-on-google-cloud.md), and the operator page is [`docs/HOSTING.md`](https://github.com/bamr87/bamr87/blob/main/docs/HOSTING.md) there.

## What is here

| File | Role |
| --- | --- |
| [`pages/sign-in.md`](../pages/sign-in.md) | The page at `/sign-in/`. It lists every application in `_data/platform.yml` whose `enabled` is true, each as a link to that application's own sign-in |
| [`_data/platform.yml`](../_data/platform.yml) | The applications: title, one-line summary, host, sign-in path and the `enabled` switch. A copy of `services:` in the hub's `_data/hosting.yml` |
| [`_data/navigation/main.yml`](../_data/navigation/main.yml) | The header menu. The "Sign in" entry is written there as a comment, waiting |

## How it works

- **This site links, and never signs anyone in.** Each application signs people in on its own address, `https://<host><sign_in>`. This site holds no session and asks for no password. An application is never framed here: zer0-CMS's own content policy forbids it.
- **A visitor only sees what is open.** With no application enabled the page says so in one sentence, it is left out of the sitemap, and the menu has no entry for it.
- **Every address ends in `bash-365.com`.** The page tells the visitor to check that, because a sign-in page is what a phishing site copies.

## Open the page for the first application

Do these in one pull request, after the hub's `_data/hosting.yml` has the application's `enabled: true` (which the hub allows only when the application answers, has its own sign-in with sign-up closed, and owes nothing in its `needs`):

1. Set the application's `enabled: true` in `_data/platform.yml`.
2. Uncomment the "Sign in" entry in `_data/navigation/main.yml`. It is the sixth top-level item, which is the limit.
3. Remove `sitemap: false` from `pages/sign-in.md` and bump its `lastmod`.
4. Open the pull request's staging site and follow the link: it must reach the application's sign-in screen over `https://`.

## What this page is not

- It is not a client portal with accounts of its own. Accounts live in each application.
- It does not link to the Harness Console. That holds the fleet's credentials and has no sign-in of its own, so it is not offered here (hub ADR 0020, decision 7).
