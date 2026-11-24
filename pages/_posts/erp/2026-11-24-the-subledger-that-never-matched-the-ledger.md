---
title: "The subledger that never matched the ledger"
sub-title: "Thirty posts on one side, three on the other, and a control that finally made them agree"
description: "A reconciliation story for controllers: how a 27-of-30 gap between two records got caught, and the cadence and approval gates that keep it closed"
excerpt: "Two records of the same work, 27 entries apart, and nobody noticed until a count was run. The fix was the one your close already uses."
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-11-24T12:00:00.000Z
lastmod: 2026-11-24T12:00:00.000Z
draft: false
categories: [erp]
tags: [erp-implementation, segregation-of-duties, change-management, automation, smb]
keywords: [month-end reconciliation, subledger to general ledger reconciliation, approval workflow controls, segregation of duties small business, reconciliation cadence, controller close checklist, Denver ERP consultant]
preview: /images/previews/the-subledger-that-never-matched-the-ledger.png
---

*A conference room, 4:50 on a Thursday. A whiteboard reads "SUBLEDGER" on the left and "LEDGER" on the right. Only one of them has anything under it.*

**Narrator**: "Every shop keeps two records of the same work. One is where the work happens. The other is where the world sees it. Tonight, a count is about to be run."

**Linda** *(the controller, holding a printout)*: "Thirty entries in the one book. Three in the other."

**Dave**: "That can't be right. We post all the time."

**Linda**: "You post when someone remembers. Twenty-seven of thirty were never posted. And one entry went out before the thing it described existed."

This is an ordinary finding. The practice that runs this site hit it on its own work in November 2026, and the fix is the same one a controller already trusts every month.

## What the count showed

BASH keeps two records of its published work: the 30 articles on this site, and the company page on LinkedIn where those articles are shared. They are supposed to mirror each other. On 2026-11-05, the first reconciliation said 3 shared, 27 missing, out of 30. Worse, when merged shares finally went out they went out all at once, and one of them posted before its page was live.

Put that in accounting terms. A subledger and a general ledger drifted apart because nothing forced them to meet. One entry was recorded before its source document existed. Nobody was careless. The posting step simply depended on someone remembering it.

The work that fixed it is public: [the commit that put a cadence, a weekly feature and a review loop in place](https://github.com/bash-365/bash-365.com/commit/38c54605695674e0f3740a04ae76cabd0d4c19d6), 11 files and about 500 added lines.

> **Commercial break, the lesson:** If posting depends on memory, your two books are only equal on the days someone remembered. You find out at the count, not before.

## The three controls, in finance terms

**Dave** *(arms crossed)*: "So we hire someone to post things."

**Linda**: "We make the books reconcile on a schedule. Same as the bank account."

The fix had three parts, and each has a close-checklist twin.

1. **A cadence, not a burst.** Shares go out in fixed slots, Tuesday and Thursday at 9:00 a.m. Denver time, no sooner than 36 hours apart and no more than one a day. Nothing posts until its page answers, and no sooner than two hours after the page landed. That is a posting calendar with a cutoff: entries land in their period, after their source document exists.
2. **A weekly pick and a catch-up.** Each week one article is featured, the sections taking turns, and one more share closes the gap for a page that was never posted. The backlog shrinks by a known amount per cycle instead of waiting for a heroic cleanup. This is the aged-items list you clear a little each close.
3. **A review loop.** Each week the published item longest without a review gets re-read against primary sources and corrected if it needs it. That is a periodic review of a standing balance, the check on a reconciling item that nobody has touched in a year.

Under all three sits the control Bob taught the alliance in the [[ERP Survivor, episode 2: the great chart of accounts debate]]: the person who drafts is not the person who approves. Drafts are written by an agent. A human merges. The merge is the approval, and nothing posts without it. That is segregation of duties, applied to a LinkedIn share instead of a journal entry.

> **Commercial break, the lesson:** A reconciliation that runs on a calendar, with a named approver and an aged-items list, closes a gap. A reconciliation that runs on goodwill reports one.

## How it plays out in your close

You do not need our tooling to use the pattern. Take any pair of records that are meant to agree: purchase receipts against vendor invoices, shipments against billing, the bank feed against the ledger, a CRM against the revenue schedule.

- **Count first.** Run one comparison this week and write down the gap. A count like "27 of 30" is the best argument you will ever have for a control.
- **Set the cadence.** Pick the day the comparison runs and the cutoff for what counts. Put it on the close calendar with an owner.
- **Clear the backlog at a fixed rate.** A known number of items per cycle beats an annual cleanup.
- **Separate the maker from the approver.** If an AI tool drafts the entry, the approver is a different person. The [[The AI audit trail: log prompts like journal entries]] post covers the register that keeps that provable.
- **Review the oldest standing item every cycle.** The balance nobody has looked at is the one that surprises the auditor.

Standing this up for one pair of records is usually a few weeks of part-time work. The first count takes an afternoon.

## Watch-outs

- **Automation moves the failure, it does not remove it.** The gap here happened because posting was a manual afterthought. A scheduled job with no reconciliation behind it just misses on schedule.
- **Cutoff rules need a reason.** Our two-hour wait and 36-hour spacing suit one page's audience. Your cutoff should come from your period-end, not from ours.
- **A control with no owner is decoration.** Someone's name goes next to every step on the calendar.
- **Don't reconcile everything.** Start with the pair where a mismatch costs you cash or credibility.

## Next step

Which two of your records are supposed to agree and have never been counted against each other? If you would rather not run that count alone, see our [ERP consulting](/services/erp/) service for the controls and close design that make the books meet on a schedule.

---

*The characters are fictional. The 27-of-30 count is not.*
