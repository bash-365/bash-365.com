---
title: "Manufacturing ERP will ship as an operating system"
sub-title: "Why software that has to talk to machines, schedule the floor, and stop a line can't stay an app, and what SteamOS shows about the way out"
description: "Manufacturing ERP already reaches into machines and the plant network. It will ship as an open-source OS distribution, the way SteamOS did for gaming"
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-11-15T17:45:00.000Z
lastmod: 2026-11-15T17:45:00.000Z
draft: false
categories: [muses]
tags: [open-source, manufacturing, linux, erp-implementation, vendor-lock-in, edge-computing, agentic-ai]
keywords: [open source ERP operating system, manufacturing ERP Linux distribution, SteamOS for manufacturing, ERP and PLC integration, OPC UA ERP, soft PLC on Linux, ERP customizations as packages, legacy ERP data migration, Denver manufacturing ERP consultant]
preview: /images/previews/manufacturing-erp-will-ship-as-an-operating-system.png
excerpt: "Steam spent years as an app on somebody else's operating system. Then Valve shipped the operating system. Manufacturing ERP is at the same fork, because a system that talks to machines, schedules the floor, and can stop a line is already doing an operating system's job."
---

In [[The future of manufacturing ERP is a Linux distribution]], I argued that manufacturing Enterprise Resource Planning (ERP) will be open source, shipped the way Linux is shipped, and run close to the shop floor. This essay pushes that one step further. I don't think the ERP will just *run on* a Linux distribution. I think, for manufacturers, it will *become* one.

Here's the reasoning in one line: an app assumes somebody else owns the hardware, the drivers, the network, the update schedule, and the permissions. A manufacturing ERP increasingly has to own all five. Software that owns those things is an operating system, whatever the sales deck calls it.

That's an opinion, and I'll show where it bends. The clearest picture of where it's heading comes from an unlikely place: a gaming handheld.

## An app is the wrong container for a plant

Look at what a plant asks its ERP to do now. It takes counts and scrap from machines rather than clipboards. It turns a temperature excursion into a quality hold. It decides which work order runs on which machine next. It has to keep taking production when the internet connection drops at 6 a.m. Friday. And every one of those touches crosses a boundary an app is supposed to stay behind: device communication, scheduling, local storage, network trust, and updates to hardware that a person can't simply reboot mid-shift.

The usual answer is to stack more apps around the ERP: a gateway for the machines, a manufacturing execution system (MES) for the floor, a historian for sensor data, an integration platform to glue them, and a Windows server somebody patches when they remember. Each piece is reasonable. Together they are an operating system assembled by committee, with no package manager, no shared update path, and no single place to read what changed. For a finance reader, it's a general ledger (GL) spread across six subledgers that never quite tie out.

I've made the economic half of this case before: the machine data is heavy, the network path should be one you own, and pure Software as a Service (SaaS) charges the most to exactly the plant that needs the ERP closest. I won't repeat it. The point here is structural. Once the ERP has to own the floor, the honest move is to ship it as the floor's operating system (OS) rather than pretend it's one more app on top.

## What SteamOS actually changed

For most of its history, Steam was something you installed on top of an operating system somebody else made. With the Steam Deck, Valve shipped the operating system itself. Valve lists the Deck's OS as ["SteamOS 3 (Arch-based)"](https://www.steamdeck.com/en/tech), and its license page describes SteamOS as [based on the open-source Arch Linux](https://store.steampowered.com/steamos/download/?ver=steamdeck).

Three design choices in that distribution matter for manufacturing, and none of them are about games:

- **A compatibility layer, so the old library still runs.** Proton is Valve's tool that [lets games made only for Windows run on Linux, using Wine](https://github.com/ValveSoftware/Proton). Nobody had to rewrite their catalog before the new platform was useful.
- **Updates that can't brick the device.** Collabora, which built the update system with Valve, describes an ["A/B" design with two OS partitions](https://www.collabora.com/news-and-blog/news-and-events/portable-linux-gaming-with-the-steam-deck.html): the new version is written to the partition not in use, and if it fails to boot, the device falls back to the old one. In normal use the OS partition is read-only; a developer mode unlocks it and Arch's `pacman` package manager.
- **One OS, more than one hardware maker.** At CES 2025, Lenovo announced the Legion Go S "Powered by SteamOS", which it called [the world's first officially licensed handheld powered by SteamOS](https://news.lenovo.com/pressroom/press-releases/lenovo-legion-unleashes-next-gen-gaming-power-at-ces-2025/), sold next to a Windows version of the same device. Valve's own [Steam Machine](https://store.steampowered.com/hardware/steammachine) runs SteamOS too.

Put those together and the platform stopped being an app fighting for room on a general-purpose OS. It became a purpose-built distribution that hardware makers can ship, with a bridge to the old world and an update path that fails safe. That's the shape I expect manufacturing ERP to take.

## The mapping, piece by piece

Analogies are cheap, so here is the one I mean, layer by layer:

| SteamOS layer | Manufacturing ERP equivalent | What already exists, in the open |
|---|---|---|
| Linux kernel and drivers | Machine communication: the protocols and runtimes that talk to programmable logic controllers (PLCs), sensors, and cells | [OPC Unified Architecture (OPC UA)](https://opcfoundation.org/about/opc-technologies/opc-ua/), a platform-independent framework from the OPC Foundation; soft PLC runtimes on Linux such as [CODESYS Control for Linux SL](https://store.codesys.com/en/codesys-control-linux-sl-1.html) (commercial) and [OpenPLC Runtime](https://github.com/autonomy-logic/openplc-runtime) (GNU GPL v3) |
| The distribution (SteamOS on Arch) | An industry build: the ERP core, manufacturing modules, localizations, and machine connectors, tested together for one kind of plant | The open-source cores from the last essay: [ERPNext](https://github.com/frappe/erpnext), [Odoo Community](https://www.odoo.com/documentation/18.0/legal/licenses.html), and others |
| Package manager (`pacman`) | Modules and customizations, installed, versioned, and removed as packages | Odoo modules and Frappe apps, plus vendor runtimes delivered as packages: CODESYS ships its runtime [as a Debian or IPK package](https://content.helpme-codesys.com/en/CODESYS%20Control/_rtsl_preparation_linux.html) |
| Compatibility layer (Proton) | Legacy ERP and data import, so years of history and open orders come along | ERPNext's [data import tool](https://docs.frappe.io/erpnext/user/manual/en/data-import) and [QuickBooks migrator](https://docs.frappe.io/erpnext/quickbooks-migrator); Odoo's [import from Excel or CSV into any business object](https://www.odoo.com/documentation/18.0/applications/essentials/export_import_data.html) |
| A/B partitions | Upgrades with a tested rollback, so a failed release falls back instead of stopping the plant | Not standard in ERP yet. This is the gap |

Read the table as a bill of materials. Most of the parts are on the shelf today. What's missing is the assembly: somebody curating a job-shop build, or a build for regulated lots, that installs as one image, talks OPC UA out of the box, and upgrades the way the Deck does. In accounting terms, the A/B partition is a reversing entry for software. You post the upgrade, and if it doesn't tie, the system reverses it before anyone has to.

## Why the operating system has to be open

An app can be closed and you can still leave it; you export the data and walk. An operating system is harder to leave, because everything else is built on it. If the ERP becomes the plant's OS, a closed one would hold the drivers, the update keys, and the integration surface for every machine you own. That's not vendor lock-in at the software layer. It's lock-in at the bolts.

That's why my position is that the manufacturing ERP-as-OS should be open source and aligned with Linux, not just hosted on it. Open code means a machine builder can ship the distribution on its own controller, the way Lenovo ships SteamOS on its handheld. It means a support partner can maintain your build without the original vendor's permission. And it means the protocols at the bottom of the plant, which are already open, meet an ERP at the top that's open on the same terms.

There's a shell joke in here, and I'll allow myself one. `bash` is the [GNU Project's Bourne Again SHell](https://www.gnu.org/software/bash/), a free, sh-compatible shell that gave the older Bourne shell a second life in the open. It's also where BASH gets its name: Bourne Again Solutions Hero. Manufacturing ERP is due for the same kind of rebirth, as an open platform rather than a sealed product.

## Agents make a distribution something a plant can maintain

The old objection to all of this is staffing: a distribution needs maintainers, and a 60-person plant has no IT staff. I've argued that AI coding agents change that math, and that [[ERP customizations should be the default]] once agents can draft, document, and re-apply them. The OS model is where those two ideas meet.

In a distribution, a customization isn't a confession buried in the core. It's a package with a version, a dependency list, an owner, and a test. That's a format agents handle well. An agent can draft the package, write the acceptance test, rebuild it against the next release, and open a pull request. The controller or the plant engineer reviews it, the same maker-checker control finance already runs on journal entries. The "no IT staff" objection turns into a smaller question: do you have one person who can review a change? That's a much smaller ask than a development team.

## Where the analogy bends

I'd rather you hear the weak points from me:

- **SteamOS isn't fully open.** Valve's own terms say SteamOS includes [open-source software alongside proprietary components, and the Steam client is its main interface](https://store.steampowered.com/steamos/download/?ver=steamdeck). An open OS can still carry a closed storefront. Ask the same question of any ERP distribution: who controls the module store, and can you install packages from somewhere else?
- **The ERP stays out of the control loop.** Calling machine communication the "kernel" is about who talks to whom, not about putting the ERP in charge of a press. Hard real-time control and safety functions stay on the PLC and the safety system. The ERP reads, schedules, and records. It doesn't run the motion.
- **A distribution needs a maintainer and a business model.** SteamOS has Valve behind it. An ERP distribution needs a support subscription, a partner network, or a machine builder that bundles it. Without one, an open-source build becomes abandoned software you happen to have a copy of.
- **A compatibility layer is a bridge, not a destination.** Import tools move masters, balances, and open documents. They don't move the process knowledge behind them, and every migration still has to tie out to the old ledger before you trust it.

## What to do before your next ERP decision

None of this needs a plant-wide bet. These steps help whichever way the market goes:

- **List where your ERP already acts like an OS.** Write down every place it touches devices, schedules machines, stores data locally, or needs an update coordinated with the floor. That list is the real scope of your next ERP, whatever the vendor says.
- **Ask how customizations are packaged.** Can a change be installed, versioned, rolled back, and re-applied after an upgrade, as a unit? If the answer is a services quote, you're buying the committee-built OS again.
- **Run a one-work-order pilot.** On a spare Linux box, stand up an open-source ERP core, a soft PLC runtime in a container, and an OPC UA connection between them. Push one work order from release to completion and see which steps you had to wire by hand. Each hand-wired step is a package your future distribution needs.
- **Plan the bridge before the destination.** Pick the history you actually need to bring forward, run a trial import, and reconcile it to the old system's trial balance. If it doesn't tie, you've learned what your compatibility layer has to do.

## Next step

Valve didn't make the Steam Deck work by building a better app. It shipped the operating system, kept a bridge to the old library, and made updates safe. I think manufacturing ERP is headed the same way, and the plants that plan for it now will choose their distribution instead of having one chosen for them. If you're weighing an ERP decision for a plant, the first call is a conversation about your systems and the one or two problems that matter most, and you leave with a clearer picture whether or not you hire us. [Book a free consultation](/contact/).
