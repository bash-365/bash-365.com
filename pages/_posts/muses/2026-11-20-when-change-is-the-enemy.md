---
title: "When change is the enemy"
sub-title: "Third-party software, lock-in, and the new make-versus-buy math"
description: "When a vendor owns the change, every release is someone else's operations decision, and agent harnesses are rewriting the make-versus-buy math"
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-11-20T21:45:00.000Z
lastmod: 2026-11-20T21:45:00.000Z
draft: false
categories: [muses]
tags: [erp, make-vs-buy, vendor-lock-in, ai-coding-agents, smb, denver-smb]
keywords: [vendor lock-in software, make versus buy software, ERP switching costs, AI coding agents, Denver IT consultant, custom vs commercial software, third-party software support, SMB ERP migration]
preview: /images/previews/when-change-is-the-enemy.png
excerpt: "Change is the point of engineering, until the software isn't yours. Then every release is someone else's operations decision landing on your desk, and the people closest to the pain have the least say."
---

## When the change isn't yours

Engineering exists to change things. That is the job: look at a process, find the friction, alter the system so the friction is gone. A good engineer is someone who is allowed to keep doing that.

The trouble starts when the system you need to change is not yours. Then every improvement arrives as a release calendar you didn't write and a Tuesday morning when the screens look different and nobody can find the button that used to close the month. The vendor calls it innovation. Your plant calls it an outage with a changelog.

This is the inversion nobody puts on the slide. Change is the point of engineering, and change is also the thing you have learned to dread, because when the change is not yours, it is someone else's operations decision landing on your desk. The vendor shipped. A product manager decided that your workflow was an edge case. You discover that at eight in the morning, with a line waiting on a work order and a controller who needs the report that no longer runs.

Enterprise resource planning software makes the pattern obvious: the ERP is where the company keeps the truth about inventory, orders, costs, and who may post what. The dread around ERP is rarely about missing features. Vendors are excellent at features. The dread is about migration and retraining — mapping old fields, relearning screens, and losing tribal knowledge that lived in a custom report. People are not afraid of a better bill of materials. They are afraid of a rewrite by a company that does not walk their floor.

If you have lived through one of these upgrades, you know the texture. The project was sold as a lift, then became a scavenger hunt, a training schedule, and a quiet agreement to keep a spreadsheet on the side, "just until things settle," which is how side systems are born. The software changed. The work did not get easier. The people closest to the work absorbed the difference.

## Three seats, one vote

There are three ways to sit with that pain, and they do not vote equally.

The users feel the disruption first. The planner who could close a shortage in a few clicks now needs a tour of a "simplified" menu. The receiving clerk who knew the old exception path now has a ticket open because that path was retired in the name of standardization. None of this shows up as a line item. It shows up as slower days and a conviction that the system is something done *to* them.

Information technology (IT) absorbs the fallout and, with impressive reliability, the blame. The inbox fills with "the system is down" when the system is up and the process moved. The weekend is spent re-permissioning a role the vendor renamed. The post-mortem asks the team that was not allowed to refuse the upgrade why it went poorly. IT did not choose the release date. IT is the department in the room when the room is angry.

Management sees something colder, and more accurate: vendor leverage, and switching costs that have become a threat. Once the general ledger, the work orders, and the customer history live in one rented system, leaving is a second implementation, paid for while you are still paying for the first. The renewal conversation is no longer about the product. It is about how badly you need not to move. The salesperson does not have to be unkind about this. The math is unkind all by itself. I have made a related argument, about who writes the rules you buy by, in [[Best practice is the interest of the stronger]].

The pattern is almost elegant, if you have the stomach for it. The people who feel the change in their hands have the least say in whether it happens. The people who clean up after it are graded on the cleanup. The people who could say no face a switching cost that makes "no" look like a career risk. Pain goes downward; decision rights go out the door to a vendor who does not sit in the standup. "Change management" pretends the problem is attitude. The problem is governance.

## The trade you actually make

Make versus buy is usually sold as a speed question, which is how you end up answering the wrong one.

When you buy, you are trading roadmap control for speed. You get a working system sooner than you could have built one. You also get a roadmap you do not set, a release train you do not stop, and a product philosophy that will collide with the slightly embarrassing way your company actually operates. The collision is not a failure of the software. It is the deal. You paid not to wait, and the price included not getting to steer.

When you make, you are trading build cost for control. You spend more time up front, and you accept that you will have to keep the thing alive. In exchange, a change to the process can be a change to the software, made by people who can walk ten feet and ask why the process exists. That is a different kind of speed: slower to start, faster to be specific.

The honest rule is narrower than the slogans. Buy when the domain is the vendor's core competency and not yours. A payroll engine, a tax table, a payment network, a map of carrier rates — these are not where a machine shop should invent a product. The vendor's whole business is staying current on that work. Buy the thing they are in business to be good at.

Buy more carefully when the domain is *your* competency wearing a vendor's label. The scheduling logic that makes your floor unique, the quality hold that exists because of one customer and one process, the costing method your controller can defend to an auditor — these are not "customizations" in the dismissive sense. They are the business. Parking them inside a platform you cannot revise is how a company accidentally outsources its own judgment.

There is a reason this decision used to default to buy, and it was not stupidity. Building was expensive: a team, a slipped timeline, and a maintenance burden that outlived the people who understood it. "Don't invent what you can purchase" was, for a long time, good husbandry. The question is whether the cost side of that sentence still holds. First, though, a quieter way the buy decision goes sour.

## The ticket that has to travel

Support is where a vendor relationship stops being a slide and becomes a week.

When the people who fix the software are far from the workflow that broke, quality degrades for a boring reason: distance, not talent. A ticket has to carry a floor's worth of context through a form. The person reading it has never stood at the bench, never watched the receiving clerk work around the serial field, never heard why that one customer cannot get the standard lead time. Days become weeks, not because nobody is working, but because each round trip is a translation, and translations drop detail.

Be precise about what is being criticized. This is not an argument about nationality, or a complaint about the people doing the work. Plenty of excellent engineers will take a ticket from a queue in another time zone and do their best with what they were given. The failure is the arrangement. A vendor that staffs support far from the customer's operation is making a cost decision and calling it a follow-the-sun model. The signal is not subtle: you were cheaper to serve at a distance than up close.

The degradation is predictable. The first response asks for screenshots of a screen you already described. The second offers a workaround that would be reasonable in a clean demo and is unusable on a dirty floor. The third closes the ticket as "working as designed," meaning the design does not include you. Meanwhile the planner has a spreadsheet, the controller has a manual reconciliation, and IT has a standing meeting about a problem that is no longer considered a problem by the only party who can change the code.

Distance is not the only way to fail. You can staff that same queue in the next building and still lose if the incentive is to close tickets rather than to understand the work. Distance just makes the incentive easier to keep. A cost-first support model keeps the people who can tell a real break from a confusing one somewhere else.

## Year one, and then year five

Picture two paths, not as a study but as a story a shop might actually live.

You buy. Year one is dazzling. The demo was clean, the implementation partner was present, the dashboards lit up, and for a while it feels as if you purchased time. People complain, because people complain, but the complaints are about learning, and learning is survivable.

Year two, a custom report breaks. It was the report the controller actually used, the one that made the close possible, built when saying yes was still part of the sale. A release renamed a field, or retired it, or moved it behind a permission nobody has. The ticket goes in. The work goes to the spreadsheet.

Year three, fixes take three weeks. Not because the change is hard, but because the queue is long, and because your request is a "configuration" until it is a "customization," which is a conversation about whether it will survive the next upgrade. Three weeks is long enough for the floor to stop asking and start working around. The workarounds become the process. The system of record is now a system of almost-record.

Year five, the renewal arrives with a forty percent increase, and the alternative is a migration that will gut the year. That number is the shape of the scenario, not a market statistic: large enough to sting, not quite large enough to make leaving look cheap. You can pay, or you can leave, and leaving means retraining, remapping, and a second dread you already understand too well. The buy path, run to term, starts as speed and ends as leverage.

Now the other path. You make. Year one is slow. The first version is narrower than the brochure you did not buy. People are impatient, and they are not wrong to be. But every change is yours. The report the controller needs walks down the hall. The exception the receiving clerk found on Tuesday can be in the software on Thursday, or at least in a branch waiting for review. No upgrade gets to retire your process without passing through someone who has to look that process in the eye.

Year five, a user with a problem reaches someone ten feet away instead of a vendor forum and a ticket number. That sentence is the whole return on the slower start. The system still has bugs; software always does. The difference is that the bugs live in a shop that can fix them, on a schedule set by the work. You traded a dazzling first year for a fifth year you still own.

## The remaining cost is judgment

The old reason to buy was that making was too expensive. A custom system required a bench of specialists, a project plan that aged into folklore, and a maintenance burden that made the next manager want to rip it out and buy anything with a support number on the box. That math was real. For a long time it was decisive.

It is not as decisive as it was. I have argued that agents change the cost of writing a change in [[ERP customizations should be the default]]. Harnesses in the class of Claude Code — artificial intelligence (AI) coding agents wired into a repository, a test suite, and a review loop — collapse much of the build cost that used to make "make" look like vanity. The scaffolding, the first draft of a report, the migration script, the test that proves the exception path still works: these are no longer a months-long opening bid. They are work a capable person can direct, inspect, and keep.

What does not collapse is judgment. Someone still has to know which process is load-bearing and which is a habit; which field the auditor will ask about; which hold keeps a bad lot from shipping; which shortcut will haunt the close. The agent will write the change. It will not know whether the change should exist. That cost was always the real one. We used to bury it under the cost of typing.

So the make-versus-buy question is not disappearing. It is getting cleaner, which is more uncomfortable. You can no longer hide a loss of control behind the claim that you could not have built the thing anyway. In more domains, you could have built the part that is actually yours and bought the part that isn't. The remaining question is the one the inversion started with: when the software changes, who steers?

If the answer is a vendor, change will keep arriving as an operations decision on your desk, and you will keep calling that your process. If the answer is you, change gets to be engineering again — a thing you do on purpose, to a system you can still recognize as yours.

Change is only the enemy when it isn't yours.

## Next step

A shell is useful because it runs the command you typed. The systems that run a company are the same: they are only yours if you can still steer them when they change. If you are weighing a renewal, a migration, or whether to keep building around a platform you cannot revise, the first call is a conversation about your systems and the one or two problems that matter most, and you leave with a clearer picture whether or not you hire us. [Book a free consultation](/contact/).
