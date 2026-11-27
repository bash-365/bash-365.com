# bash-365-apex

> Client-side redirect from the bash-365.com apex domain to www, served by GitHub Pages for BASH Consulting.

[![Live site](https://img.shields.io/badge/live-bash--365.com-2ea44f)](https://bash-365.com) [![License](https://img.shields.io/github/license/bamr87/bash-365-apex)](LICENSE)

## Overview

Redirects the bare domain `bash-365.com` to `https://www.bash-365.com`, keeping the path.

DNS for `bash-365.com` is hosted in Microsoft 365, which has no ALIAS/ANAME records, so the apex cannot point at the Azure Static Web App that serves `www`. The apex A/AAAA records point at GitHub Pages instead, and this repo answers there with a client-side redirect (`index.html` for `/`, `404.html` for every other path).

Retire this repo if the apex ever moves to a DNS host that supports ALIAS records.

## Features

- `index.html` sends `/` to `https://www.bash-365.com`
- `404.html` catches every other path and redirects it to the same path on `www`
- `CNAME` binds this GitHub Pages site to the `bash-365.com` apex domain

## Quick start

There is nothing to build. Edit `index.html` or `404.html` and push to `main`; GitHub Pages serves the change.

## Project structure

| Path | What it is |
|---|---|
| `index.html` | Redirect for the root path |
| `404.html` | Redirect for every other path, keeping the path |
| `CNAME` | Custom domain for GitHub Pages |
| `.nojekyll` | Serves the files as-is, without a Jekyll build |

## Contributing

Contributions are welcome via pull request. Use [Conventional Commits](https://www.conventionalcommits.org/) and keep the CI checks green. The fleet-wide workflow is described in the hub's [CONTRIBUTING.md](https://github.com/bamr87/bamr87/blob/main/CONTRIBUTING.md).

## Changelog

Notable changes are recorded in [CHANGELOG.md](CHANGELOG.md); the full record is in the [commit history](https://github.com/bamr87/bash-365-apex/commits/main).

## License

Released under the [MIT License](LICENSE).

---

<!-- bamr87-portfolio-footer -->
Part of the [bamr87 portfolio](https://github.com/bamr87) — browse every project on [Amr's GitHub profile](https://github.com/bamr87).
