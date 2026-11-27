---
name: org-contribute
description: Contribute to any BASH Consulting org repository the same way every time — get the brief, follow the repo's own rules, close its agent-readiness gaps, run its gates, open one draft pull request, leave the knowledge behind. USE WHEN asked to change, fix, standardize or evolve bash-365.com, bash-365-apex, csv-vscoode or any repo in _data/org/repos.yml, or to bring an org repo up to the agent-readiness standard. Never merges.
---

# Contributing to an org repository

One procedure for every org repository, so the result does not depend on which agent ran it or what it remembered. Guardrails: [`_shared/quarantine.md`](../_shared/quarantine.md), all sections apply. The rules this procedure enforces are in [`brain/notes/org-operating-rules.md`](../../../brain/notes/org-operating-rules.md).

## 1. Get the brief

```bash
python3 scripts/brain/brain.py brief <repo> --task "<what you are about to do>"
```

(or `get_brief` over MCP). It joins the org operating rules, the repo's commands and conventions from its agent file, its open gaps against [`_data/org/standard.yml`](../../../_data/org/standard.yml), and the notes in the vault that bear on the task. For an **upstream** (the hub, the theme, zer0-CMS) the brief says where the change belongs; open the pull request there, never a fork here.

If the snapshot is old, refresh it first: `python3 scripts/brain/brain.py sync --repo <repo>`.

## 2. Read the repo's own rules

Clone or open the target repository and read its `docs/constitution.md` and agent file (`AGENTS.md`, else `CLAUDE.md`) in full. Where they are more specific than the brief, they win.

## 3. Make the change

- Branch `<type>/<slug>` off the default branch; one repository per pull request.
- Keep the change to the task; leave adjacent code alone.
- If the task is **standardizing** a repo, close its gaps in the order the brief lists them (must before should). Prefer the hub kit the brief names (`tools/fanout.sh --kit … --target …`, from a bamr87/bamr87 checkout, dry run first) over hand-writing the files, and fill every scaffold `TODO` with facts read from the repository, never guessed ones.
- Add the org-brain pointer (ORG-BRAIN-01) under **Fleet context** when you touch the agent file anyway.

## 4. Prove it

Run the gates the brief lists for that repository and record exactly what ran and what it printed. A gate you could not run is reported as not run. A user-visible change follows the repo's verification rules (feature catalog entry, evidence or `skip-evidence` with a reason).

## 5. Ship and hand off

Conventional Commit title, draft pull request, the repo's template filled in. Never merge a pull request that is gated (amendments, secrets, settings, deploys, destructive changes, `needs-amr`): label it and stop.

## 6. Leave the knowledge behind

Back in bash-365.com, when the work taught something the next agent needs, file it (`brain.py save …`), `sync` the repo you changed once it merges, and `build`, in a pull request here.
