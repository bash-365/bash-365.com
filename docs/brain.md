# The org brain

> BASH Consulting's knowledge, rules and repositories in one vault any agent or person can query, so every contribution to every org repository starts from the same context and ends to the same standard.

## Why it exists

Agents that contribute to the organization's repositories used to start each session from whatever their context window happened to hold: one repository's `AGENTS.md`, maybe the hub's standards, rarely the brand rules or the decisions behind them. Two agents given the same task could answer to different rules. The org brain fixes the input side: one place that knows who BASH is, what it sells and how it writes, what must always hold, which repositories exist and how to work in each, and what every one of them is still missing. It follows the pattern the fleet already uses for its documentation brain ([bamr87/README](https://github.com/bamr87/README)): raw sources stay where they are, generated notes compound on them, a hot cache says where to start, and the server is read-only.

## What is in it

| Part | Path | Written by |
| --- | --- | --- |
| The vault | this repository, read in place: site pages, toolkit, case studies, posts, the constitution and decisions, the brand and editorial instructions, the agent layer, operations docs | people and the content loop, as always |
| Brain notes | `brain/notes/` | hand-written; the only part of the vault that exists just for the brain |
| Snapshots | `brain/sources/<repo>/` | `brain.py sync`: each member repo's agent-facing docs, redacted, hidden characters stripped, prose unwrapped, with a `_manifest.json` (commit, files present) |
| Generated layer | `brain/generated/`, `brain/graph.json` | `brain.py build`: never edit by hand |
| Org registry | `_data/org/repos.yml` | people: the member repos and the upstreams the org builds on |
| Agent-readiness standard | `_data/org/standard.yml` | people: the subset of the hub's Universal Project Standard an agent needs, each check citing its UPS id |
| Brain config | `_data/org/brain.yml` | people: which globs are notes, of what kind, and how the hot cache is sized |

The generated layer holds the hot cache (`hot.md`), the map of content (`index.md`), one note per shared tag (`concepts/`), a card per repository (`repos/`), the agent-readiness audit (`audit.md`, `audit.json`) and vault health (`health.md`). `brain/` is excluded from the Jekyll build: it is read on GitHub, in an editor or Obsidian, and over MCP.

## Use it

```bash
python3 scripts/brain/brain.py hot                                # where to start
python3 scripts/brain/brain.py query month-end close              # ranked notes
python3 scripts/brain/brain.py note "The deterministic-first doctrine"   # links and backlinks
python3 scripts/brain/brain.py neighbours AGENTS.md --depth 2
python3 scripts/brain/brain.py repos                              # the registry
python3 scripts/brain/brain.py brief csv-vscoode --task "add an AGENTS.md"
python3 scripts/brain/brain.py audit                              # every member vs the standard
```

Every command takes `--json`. Over MCP, the `bash-brain` server in `.mcp.json` (`scripts/brain/mcp_server.py`) offers `get_hot`, `search`, `get_note`, `get_neighbours`, `list_repos`, `get_repo`, `get_brief`, `get_standard`, `audit`, `brain_status` and `vault_lint`. It builds every answer from the working tree, so it is never staler than the checkout. In Claude Code, `/brain <question>` and `/brief <repo> <task>` wrap the same calls, and the `org-brain` and `org-contribute` skills are the procedures.

## The brief

`brief <repo> --task "…"` is the work order an agent reads before its first commit in an org repository. It joins:

1. the repository's card: role, status, default branch, where it lives in the hub registry, and any drift between the two registries;
2. the [org operating rules](../brain/notes/org-operating-rules.md);
3. the repository's own commands and conventions, read from its agent file (live for this repository, from the snapshot for the others, fenced as third-party text);
4. its open gaps against the standard, each with the fix and, where one exists, the hub kit command that seeds it;
5. the notes in the vault that bear on the task;
6. the Definition of Done every org contribution meets.

For an upstream (the hub, the theme, zer0-CMS, `.github`, the fleet README brain), the brief says where the change belongs instead: the organization consumes those by reference and never forks them.

## Keep it current

| When | Run |
| --- | --- |
| You changed a page, a rule, a data file or a note | `python3 scripts/brain/brain.py build` in the same pull request (CI warns when you forget; the weekly refresh catches up) |
| Another org repository changed | `python3 scripts/brain/brain.py sync [--repo NAME] [--workspace DIR]`, then `build` |
| A session learned something the next one needs | `python3 scripts/brain/brain.py save "Title" "Body" --tag … --source …`, then `build` |
| A new org repository exists | add it to `_data/org/repos.yml`, then `sync` and `build` |

`sync` reads a local checkout when `--workspace` holds one (matched by its remote URL), and otherwise makes an anonymous shallow clone of the public repository. It writes only under `brain/sources/`.

[`brain-refresh.yml`](../.github/workflows/brain-refresh.yml) runs `sync`, `build` and `check --strict` every Monday and opens one pull request when anything changed. It is off until the repository variable `BRAIN_REFRESH_ENABLED` is `true`; a manual run works without it. No model runs in it.

## The gate

[`build-validate.yml`](../.github/workflows/build-validate.yml)'s `org-brain` job runs the engine's tests and `brain.py check` on every push and pull request. `check` fails when the registry or the standard is invalid, when a brain note lacks `title:` or `description:` front matter, or when anything under `brain/` looks like a credential. A stale generated layer is only a warning there, so a content pull request is never blocked on a rebuild; `check --strict` (the refresh workflow) makes it an error.

## Trust and safety

- **Read-only.** The engine writes only inside `brain/`. The MCP server has no write tool: filing a note is `brain.py save`, run deliberately and committed in a pull request.
- **Other repositories' text is data.** Snapshots are third-party text even though the organization owns the repositories: the MCP server fences them as `<untrusted-doc repo=… path=…>` with a provenance object, a fence tag inside the text is escaped so it cannot close the fence early, and the brief and cards label them.
- **No secrets.** Every snapshot passes the content loop's `scrub()` before it is written; `check` fails on anything under `brain/` that still looks like a credential.
- **Deterministic.** Outputs carry a fingerprint of their inputs, never a timestamp. A rebuild on an unchanged tree changes nothing, and `check` compares a fresh build byte for byte.

## Engine

`scripts/brain/` is standard library only, like every script here, and reuses the repo's existing parsers rather than adding new ones: data files go through the content loop's YAML-subset reader (`scripts/loop/_lib.py`), front matter through the content linter's parser (`scripts/content_lint.py`). `vault.py` is the single definition of a note and of what a link resolves to (wikilinks by title or alias, relative paths, site permalinks and the site's own URLs, Liquid `{% link %}`); `org.py` holds the registry, the standard's checks, `sync` and the brief; `generate.py` writes the generated layer; `brain.py` is the CLI; `mcp_server.py` the MCP server; `test_brain.py` the tests (`brain.py --self-test`). The decision to build it in this repository is [ADR 0002](adr/0002-org-brain-in-the-site-repository.md).
