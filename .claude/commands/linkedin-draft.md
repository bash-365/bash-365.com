---
description: Draft on-brand LinkedIn company-page copy for a post or update and stage it for approval
argument-hint: "<section/slug | \"standalone update text\">"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(scripts/linkedin.sh draft:*), Bash(scripts/linkedin.sh preview:*), Bash(scripts/linkedin.sh queue:*), Bash(scripts/linkedin.sh sources:*), Bash(date:*), Bash(git status:*), Bash(git diff:*), Bash(git checkout:*), Bash(git add:*), Bash(git commit:*), Bash(gh pr create:*)
---

Draft a LinkedIn share for the BASH company page following the **`linkedin-share`** skill, and stage it for human approval. Target: `$ARGUMENTS`.

**Do this:**

1. Read the **`linkedin-share`** skill and apply the **`content-editorial`** + **`brand`** rules it points to. Decide the type from the argument:
   - Looks like a post reference (`section/slug`, a path, or a slug that matches a file under `pages/_posts/`) → **article**. Load that post; note its `title`, `description`, `sub-title`, `tags`, and section voice profile in `_data/taxonomy.yml`.
   - Otherwise → **update** (free-form text).
2. For an article, scaffold the draft with `scripts/linkedin.sh draft <ref>` — it writes `drafts/linkedin/<YYYY-MM-DD>-<slug>.md` at `status: pending` and refuses a post that was already shared. For an update, get today's date (`date -u +%Y-%m-%d`) and write `drafts/linkedin/<YYYY-MM-DD>-<slug>.md` with `type: update` and `status: pending`.
3. Write the commentary into the body per the skill: hook front-loaded in the first ~140 chars, ~600–1200 chars, the post's section voice, exactly one CTA, 2–3 CamelCase hashtags, no banned phrases, no exclamation marks, nothing invented. For an article, do **not** restate the card description.
4. Preview and run the mechanical guard — fix every `ERROR` it reports:
   ```bash
   scripts/linkedin.sh preview <draft-id>
   ```
5. Open a PR for approval (mirrors the content-gardener flow; never post here, never push to main):
   - Branch `linkedin/draft-<YYYY-MM-DD>-<slug>`, commit the single draft file with message `content(posts): linkedin draft — <slug>`.
   - `gh pr create` against `main`. The PR body states the target, shows the drafted commentary and the preview's fold line, and gives the reviewer the approval checklist: edit the copy in `drafts/linkedin/<file>.md`, confirm voice/CTA/claims, then **merge** — merging is the approval that lets `linkedin-publish.yml` post it.

Post nothing to LinkedIn from this command, and never set `ZER0_LINKEDIN_PUBLISH`. The draft stays `status: pending` until a human merges it. The final voice pass is done with Opus 4.8.
