# `.claude/` — the native Claude context framework

This directory is the Claude Code layer for the bash-365.com repository. It is the reference implementation of the operating model the site describes at [`/ai-operations/`](../ai-operations.md) and teaches partners at [`/tools/partners/claude-context-framework/`](../pages/_toolkit/claude-context-framework.md): **rules in files, reusable playbooks, agents that draft, humans who approve.**

Start at the root [`CLAUDE.md`](../CLAUDE.md). This file maps what lives here and when to reach for it.

```
.claude/
├── settings.json        # Project settings: hooks wiring (checked in, shared with the team)
├── skills/              # Governed procedures — the same steps, done the same way, every time
│   ├── content-editorial/   Apply house editorial standards + run the content lint gate
│   ├── toolkit-doc/         Author a business- or partner-track toolkit doc end to end
│   ├── wikilinks/           Obsidian [[wikilink]] discipline (the kramdown/index foot-guns)
│   ├── linkedin-share/      Draft on-brand LinkedIn company-page copy, staged for approval
│   ├── brand/               Apply the BASH verbal + visual identity
│   ├── content-loop/        One cycle of the content loop: plan → write from real work → gate → ledger → one PR
│   └── _shared/quarantine.md  Shared guardrails every agent + skill cites: untrusted-input quarantine, honesty rule, merge discipline (agent-context kit v0.4.0)
├── agents/              # Subagents — delegate a bounded job to a fresh context
│   ├── article-reviewer-editor.md   Editorial + SEO + frontmatter review (has project memory)
│   ├── jekyll-build-validator.md    Validate the build across dev / Pages / Azure stacks
│   ├── brand-guardian.md            Audit copy + assets against the brand SSOT
│   ├── preacher.md                  Weekly doctrine enforcement — or mechanize a check (docs/the-preacher.md)
│   ├── content-curator.md           Weekly content review — expand an article or write a new one
│   └── loop-writer.md               The content loop's writer — one piece from the practice's own work (docs/content-loop.md)
├── commands/            # Slash commands — discoverable entry points to common workflows
│   ├── lint-content.md      /lint-content   → run the editorial gate on changed content
│   ├── new-toolkit-doc.md   /new-toolkit-doc → scaffold a new toolkit doc
│   ├── linkedin-draft.md    /linkedin-draft → draft + stage a LinkedIn share
│   ├── brand-check.md       /brand-check    → run the brand audit
│   └── loop-run.md          /loop-run       → run one cycle of the content loop
├── agent-memory/        # Per-agent memory that persists decisions across sessions
│   └── article-reviewer-editor/
├── loop/                # (gitignored) the SessionEnd hook's local session-trace queue
└── hooks/               # Policy enforced automatically on tool events
    ├── pr-review-comments.sh   PostToolUse(Bash): require PR-comment review after gh pr create
    └── session-trace.sh        SessionEnd: record what the session touched for the content loop (scripts/loop/trace.py)
```

## Which primitive do I use?

| I want to… | Reach for | Why |
|---|---|---|
| Do a recurring task the governed way | a **skill** | Encodes the steps + standards so output is repeatable. |
| Hand off a self-contained job | a **subagent** | Runs in its own context; keeps the main thread clean. |
| Give a human a one-word trigger | a **command** | Discoverable as `/name`; wraps a skill or agent. |
| Make a rule apply without being asked | an **instruction** (`.github/instructions/`) or a **hook** | Auto-loads on matching files, or fires on a tool event. |
| Remember a decision between sessions | **agent memory** | Same correction never has to be made twice. |

## Relationship to `.github/`

The repo predates the Claude-native layer and already has a mature **cross-tool** AI surface under `.github/` — `AGENTS.md`, `copilot-instructions.md`, `instructions/`, and the `prompts/` library that Copilot and the extension consume. That stays authoritative and tool-neutral.

`.claude/` does not replace it. It **specializes** it for Claude Code:

- **Instructions** (`.github/instructions/`) are shared rules; skills and agents here cite them
  rather than restating them. The brand and content-style files are the source of truth.
- **Prompts** (`.github/prompts/`) are the portable playbooks; the richer **skills** here are their
  Claude-native counterparts. Keep a shared workflow in sync across both when you change it.

When you add a capability, add it at the right layer: a *rule* → an instruction; a *portable playbook* → a prompt; a *Claude-native procedure* → a skill; a *delegated job* → an agent; a *trigger* → a command. One concern per file.

## Conventions for authoring here

- **Skills:** `skills/<kebab-name>/SKILL.md` with YAML frontmatter `name` (kebab-case, matches the
directory) and `description` (one line, when-to-use — this is what Claude matches on). Bundle helper scripts alongside `SKILL.md` when a step should be deterministic.
- **Agents:** `agents/<kebab-name>.md` with frontmatter `name`, `description` (include trigger
  examples), `model`, optional `color`, optional `memory: project`.
- **Commands:** `commands/<name>.md` with frontmatter `description` (and optional `argument-hint`,
  `allowed-tools`); the filename is the `/name`.
- Keep every file **short and single-purpose**, and cross-link with relative paths so the graph stays
  navigable. Match the house voice — these files are read by people evaluating how BASH works.
