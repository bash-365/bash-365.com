---
title: "Hold the major: a software update policy you can sign off on"
description: "A three-lane software update policy that keeps security fixes fast, routine updates automatic, and breaking upgrades on your schedule"
excerpt: "Most update outages aren't caused by updating. They're caused by having one rule for every kind of update. Split the rule into three lanes and write down when each hold ends."
author: "Amr Abdel-Motaleb"
layout: article
date: 2026-10-15T12:00:00.000Z
lastmod: 2026-10-15T12:00:00.000Z
draft: false
categories: [corp]
tags: [change-management, patch-management, it-governance, vendor-lock-in, risk-management]
keywords: [software update policy, patch management policy smb, major version upgrade risk, dependabot ignore major versions, change management for small business it]
preview: /images/previews/hold-the-major-a-software-update-policy-you-can-si.png
---

Every business that runs software eventually picks an update policy, usually by accident. Either everything updates automatically and something breaks on a Tuesday, or nothing updates until a security scanner turns the dashboard red. Both are policies. Neither is one you'd sign off on if someone wrote it down.

## The risk is one rule for three different kinds of change

A patch that closes a published vulnerability, a minor release with a new feature, and a major release that changes how the product works are three different business decisions. Treating them the same is the mistake. "Update everything" puts a breaking change on the same fast track as a security fix. "Freeze everything" holds the security fix hostage to the fear of the breaking change.

We saw this play out in our own portfolio in the first two weeks of October. The repositories behind our sites and tools use GitHub's Dependabot to propose dependency updates automatically, grouped into one pull request per batch to cut down the noise. Three times in one week, a single incompatible major version took a whole batch down with it:

- In one application, a TypeScript 5 to 7 upgrade could not install at all, because the linting toolkit it sits beside only accepts TypeScript versions below 6.1 ([aieo#115](https://github.com/bamr87/aieo/pull/115)).
- In another, a testing library's version 3 conflicted with the test runner, which still requires version 2. The whole grouped update failed at install, and closing it did nothing, because the tool recreated the same batch with the same bad upgrade in it ([law-ai#153](https://github.com/bamr87/law-ai/pull/153)).
- A day later, in the same application, ESLint 10 removed a function that a widely used React plugin still calls, so the next regrouped batch failed at the lint step instead ([law-ai#157](https://github.com/bamr87/law-ai/pull/157)).

Nothing here is exotic. Every one of those was a vendor shipping a major release before the rest of its ecosystem caught up. That's normal. What turns it into downtime is a policy that can't tell it apart from a routine patch.

## What we'd actually do: three lanes, each with an owner

**Lane 1: security fixes go fast.** When a published vulnerability has a fixed version, it moves in days, not at the next maintenance window. In the same fortnight, a Denial of Service (DoS) advisory against Django turned a project's dependency scan red; the fix was a one-step patch bump within the same 5.2 line ([barodybroject#196](https://github.com/bamr87/barodybroject/pull/196)). Another project raised the minimum allowed version of its test runner to clear a security alert, without pinning it to one exact release ([bamr87#356](https://github.com/bamr87/bamr87/pull/356)). Neither change needed a meeting.

**Lane 2: minor and patch updates flow automatically, with tests as the gate.** These are the updates the "update everything" crowd is right about. If your tests pass, take them. Holding them back is how you end up three years behind and facing one enormous upgrade instead of thirty small ones.

**Lane 3: major versions are held on purpose, with a written exit condition.** This is the lane most businesses skip. A hold is not "we'll get to it." It's a line in the configuration that names the product, the version being held, the reason, and the signal that ends the hold. In each of the three cases above, the fix was a short `ignore` rule in the Dependabot configuration file, which GitHub documents as able to skip a single semantic-versioning level such as major updates ([Dependabot options reference](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/dependabot-options-reference)). Each rule carries a comment saying when to remove it, for example "drop this once the React plugin supports ESLint 10," and each hold is logged in the project's backlog so it doesn't become permanent by neglect.

The same principle applies to your own shared tools. Our sites all run one shared quality-check workflow. Until this month, most of them pointed at its live development copy, so any change to it reached every site at once. When a stricter version shipped, we released it under a version label, `v2`, and moved each site to that label through its own reviewable change ([bamr87#354](https://github.com/bamr87/bamr87/pull/354) and the follow-up pin pull requests). Now a change to the shared tool reaches a site only when that site opts in.

## How it plays out

For a typical small business, this is a policy document and a few hours of configuration, not a project.

1. **Inventory what updates itself.** Your line-of-business apps, your Microsoft 365 or Google Workspace tenant, endpoint software, and any custom code. Note which of them can be held at a major version and which can't. Software-as-a-Service (SaaS) vendors often decide this for you.
2. **Write the three lanes down.** One page. Who approves a security fix (usually nobody beyond whoever applies it), what testing gates a minor update, and who decides when a major hold ends.
3. **Turn holds into records.** Every held major gets a reason and an exit condition, in the tool's configuration where possible and on your IT ledger either way. Review them at a set interval, the way finance reviews open items at month-end close.
4. **Pin shared things to versions, not to "latest."** Scripts, templates, and integrations that more than one system depends on should move by deliberate release, so one upstream change can't break every downstream system on the same morning.

## Watch-outs

- **A hold with no exit condition is a freeze.** Six months later nobody remembers why, and you're now facing the exact large, risky upgrade the policy was meant to avoid.
- **Don't let a major hold block a security fix.** Check that your tooling still delivers security updates for held products, and if a vulnerability is only fixed in the new major, the hold ends now, on purpose.
- **Closing the noisy update isn't the same as deciding.** As the testing-library case showed, an automated tool will often re-propose the same change. Write the decision into the configuration, or you'll make it again every week.

## Next step

If your business runs on software that updates itself on someone else's schedule, the policy above is a one-afternoon conversation and a short document. Our [[Managed IT services]] engagements start with exactly this kind of inventory, or [get in touch](/contact/) and we'll walk through your update lanes with you.
