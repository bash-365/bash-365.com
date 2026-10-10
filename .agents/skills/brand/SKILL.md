---
name: brand
description: Apply the BASH verbal and visual identity to any page, asset, headline, or agent output. Use when naming the brand, writing positioning copy, choosing colors or logo treatment, or checking that work is on-brand.
---

# Apply the BASH brand

Fast application of the identity. The authoritative detail is [`.github/instructions/brand.instructions.md`](../../../.github/instructions/brand.instructions.md) — read it for anything not covered here. This skill is the working quick-reference.

## The name — get this right every time

- **BASH** is full caps, always. Not "Bash", not "bash". "BASH Consulting" on first mention, "BASH"
  after.
- Expansion: **Bourne Again Solutions Hero** — a play on the Unix **Bourne Again SHell** (`bash`, set
in monospace when you mean the shell). The wordmark says what the firm does: it turns typed intent into running systems.
- Founder / author byline: **Amr Abdel-Motaleb**.

## The one-liner

> Enterprise-grade IT for small business — cloud, ERP, data, and AI-augmented automation, from
> Denver, Colorado.

## Voice in three moves

1. **Practitioner, not platform.** Speak from experience; never from hype. Banned: revolutionary,
   cutting-edge, world-class, seamless/robust/scalable-without-a-number.
2. **Finance + IT in one breath.** Close and consolidation on one side, landing zones and RPO/RTO on
   the other. The dual fluency is the edge.
3. **Easy but hard.** Welcoming at the door, uncompromising on quality. Enact it; don't announce it.

The doctrine every piece should express: **deterministic foundations first, AI as an overlay; governed, not improvised; build in the open and own what you build; easy but hard.**

## Color

| Use | Name | Hex |
|---|---|---|
| Logo primary | Red | `#a11111` |
| Logo accent | Yellow | `#ffe900` |
| Logo deep | Teal | `#376986` |
| UI primary (theme `aqua`) | Blue | `#007bff` |

Keep the **logo palette** (identity) distinct from the **theme palette** (UI). Don't repaint the UI in logo colors. Hex values in `_config.yml` stay quoted.

## Logo

`assets/brand/favicon.svg` is the mark; `assets/brand/logo/` holds the wordmark variants (prefer latest `v2`). Never stretch, recolor, or add effects. Details in `assets/brand/logo-standards.txt`.

## Don't

- Claim certifications, headcount, client logos, revenue, or awards.
- Say a compliance framework is "met" or that BASH is "certified" — describe what the framework
  *requires*.
- Override theme typography/colors mid-page or restyle the logo.

## Check your work

Run the `brand-guardian` agent or `/brand-check` before shipping identity-bearing copy or assets. It reads the brand SSOT and reports drift (name casing, banned claims, off-palette color, voice).
