---
type: article
status: pending
source: pages/_posts/tech/2026-10-29-automated-linkedin-posts-approved-by-a-person.md
title: Automated LinkedIn posts, approved by a person
url: https://www.bash-365.com/posts/2026/10/29/automated-linkedin-posts-approved-by-a-person/
---

Our LinkedIn pipeline showed green checks for six weeks, and it could not have posted a thing.

One missing brace in a settings file sent the publisher back to its defaults, so a merged post would have been answered with "Nothing to publish". The token check skipped every week because no token was set, and a skip counts as a pass. The configuration check flagged the broken file in seven straight runs and passed each time, because it was only allowed to report.

The approval gate held: nothing ships unless a person merges it. What failed was everything meant to tell us the rest had stopped. Worth a read before you trust a green badge on anything that publishes for you.

#Automation #DevOps #AI
