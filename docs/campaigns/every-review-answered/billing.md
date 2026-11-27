# Billing and collections — charging for the review service

How BASH Consulting charges for the review service described in [engagement-model.md](engagement-model.md): who holds the money, how a client goes from yes to paying, what happens when a payment fails, the tax questions, the books, and what the integration with zer0-CMS looks like. It is a design, not yet built. Billing code, keys and the price list fall under the constitution's review gate ("secrets, budgets and billing"), so every step of it lands through a pull request the maintainer merges.

**Superseded in part (2026-11-26).** BASH's billing now has a home of its own: DjangoERP's [billing platform plan](https://github.com/bamr87/djangoerp/blob/main/docs/plan/billing-platform.md) and its proposed ADR 0005 make DjangoERP the record of customers, subscriptions and invoices, with Stripe only moving money. That replaces "Stripe Billing collects" and the zer0-CMS integration below, which will listen to DjangoERP's events instead of Stripe's. The processor fees, the collections timeline, the tax questions and the refund terms here still hold, as DjangoERP's payment, collections and tax configuration.

Fees and rules below were read from the providers' own pages on 2026-11-26 unless marked otherwise. The prices themselves are in the private pricing model; its Payments tab works these fees out for each tier.

## The decision

- **Stripe Billing collects.** Subscriptions, one-time setup fees, card and bank debit, automatic retries, reminder emails, the customer portal and usage meters are all in Stripe's pay-as-you-go plan (0.7% of billing volume, [pricing](https://stripe.com/billing/pricing)).
- **The books stay the books.** Payouts and fees flow to QuickBooks Online, or to whatever ledger BASH keeps, through a sync.
- **zer0-CMS follows Stripe and never charges anyone.** It mirrors each client's status from signed webhooks and turns features on and off from that status alone.
- **Start with no code.** Stripe's hosted Checkout links and customer portal carry the first few clients. The webhook mirror comes when clients sign up without BASH in the loop, or when Done for you needs usage billing.

## Principles

1. **BASH never sees a card or bank number.** Clients type them only into Stripe's hosted pages: Checkout, the hosted invoice page and the customer portal.
2. **Not paying never holds the profile hostage.** The Google Business Profile, the reply guidance and the website stay the client's whatever they owe. The worst that non-payment does:
   - stops BASH's work and the AI drafting;
   - ends with BASH removing itself as a manager.
3. **Deterministic.** Usage is counted from the platform's own records by a scheduled job. No model touches billing.
4. **Bank debit first.** It costs a fraction of a card payment (below), so the Checkout page offers it first. Cards stay available for clients who prefer them.

## Choosing the processor

Fees on a $100 payment (rates from [Stripe](https://stripe.com/pricing), [Stripe's bank debits](https://stripe.com/pricing/local-payment-methods) and [QuickBooks Payments](https://quickbooks.intuit.com/payments/payment-rates/)):

| Way of collecting | Fee on $100 | What it adds | What it lacks |
| --- | --- | --- | --- |
| Stripe card, with Billing | $3.90 (2.9% + 30¢ + 0.7%) | Retries, reminder emails, customer portal, webhooks, usage meters, tax automation | |
| Stripe bank debit (ACH), with Billing | $1.50 (0.8%, capped at $5, + 0.7%) | The same | Business accounts can dispute only for two business days, but a failed debit costs $4 |
| QuickBooks Payments card, recurring invoice | $2.99 (2.99%) | Lands in QuickBooks with no sync | Autopay only on invoices up to $5,000. Editing the invoice amount or frequency cancels autopay. No subscription state for the platform to follow. |
| QuickBooks Payments bank (ACH) | $1.00 (1%, $1 minimum) | The same | The same |
| Check or transfer, invoiced by hand | $0 | Nothing | BASH's time on every invoice and every late one |

QuickBooks Payments is cheaper per payment. Stripe wins because of the integration: the platform can follow a subscription's state, clients manage their own payment method, and failed payments are retried and chased without BASH. If BASH would rather not integrate anything, QuickBooks recurring invoices with autopay are the cheaper way to run a handful of clients by hand, and the collections timeline below works the same.

## What lives in Stripe

Each product has a monthly and an annual price per location; the quantity is the number of locations. The amounts are the maintainer's, set in Stripe and in the private Sheet.

| Object | Kind | Lookup key | Notes |
| --- | --- | --- | --- |
| Portal | Recurring, flat | `review-portal-monthly`, `review-portal-annual` | |
| Guided | Recurring, flat | `review-guided-monthly`, `review-guided-annual` | |
| Done for you | Recurring, flat | `review-dfy-monthly`, `review-dfy-annual` | |
| Reviews beyond the allowance | Recurring, usage on a meter `reviews_handled`, graduated so the allowance is free | `review-dfy-overage` | Billed in arrears on the next invoice |
| Setup | One-time | `review-setup-portal`, `review-setup-guided` | Added to the first invoice |
| Founding client | Coupon, repeating 12 months | `founding-12` | Never tied to a testimonial or a case study |
| Additional locations | Coupon or volume price | `extra-location` | |

If the tax review below says platform access and services must be separate lines, each tier becomes two prices on the same subscription, `…-platform` and `…-service`.

Stripe's customer portal lets a client change a flat subscription but not one with a usage price: Done for you clients can only cancel there, so tier changes for them go through BASH ([Stripe docs](https://docs.stripe.com/customer-management)).

## From yes to the first payment

1. **The agreement, before any money.** The owner signs:
   - the engagement terms: tier, price, payment terms, the collections timeline below, cancellation and refunds;
   - for Done for you, the reply authorization and the escalation list.

   They also accept BASH's manager invite on the Business Profile.
2. **The Checkout link.** BASH sends a Stripe Checkout link in subscription mode:
   - the tier's price times the number of locations, and the setup fee as a one-time line;
   - bank debit (verified instantly through the client's bank sign-in) and card;
   - a link to the signed terms.

   Setup is charged at signing. The first monthly charge falls when the two-week supervised start ends: a trial period, or a billing date set to that day.
3. **The platform hears about it.** With the integration, `checkout.session.completed` links the Stripe customer and subscription to the client's account and sites. Without it, BASH sets the account up by hand.
4. **Every month after.** Stripe invoices in advance and charges the saved method automatically, then emails the receipt. Done for you's reviews beyond the allowance are billed on the following invoice.

A client who needs an invoice instead (a group with accounts payable) gets the same subscription with `collection_method: send_invoice` and 15 days to pay. Stripe's emails and the hosted invoice page do the rest.

## Collections: when a payment fails

Stripe retries a failed card up to 8 times within 2 weeks on its default schedule, and a bank debit at most twice within 40 days, only for insufficient funds ([Smart Retries](https://docs.stripe.com/billing/revenue-recovery/smart-retries)). After the last retry, set the subscription to **unpaid**: Stripe's guidance is to revoke access at `unpaid` or `canceled` ([subscription statuses](https://docs.stripe.com/billing/subscriptions/overview)), and `unpaid` keeps the invoice open for recovery where `canceled` is final.

| When | The client sees | BASH does | The platform does |
| --- | --- | --- | --- |
| Day 0, the charge fails | Stripe's email with a link to update the card; a banner in the studio | Gets the alert | Full service (status `past_due`) |
| Days 1 to 14 | Stripe's retries and reminders | Emails on day 3 and calls on day 7, in person: a small client relationship is worth more than a script | Full service |
| Retries end (day 14 for cards; later for bank debit) | A notice that AI drafting and BASH's approvals are paused until the balance is paid | Sends the notice | Status `unpaid`: AI drafting, Done for you approvals and the monthly report pause. Sync continues, and the owner can still read reviews, write and post their own replies, and export. |
| Day 30 | Notice that the service has ended, with an export of the reply guidance, the reviews file and the record of replies | Cancels the subscription, removes itself as a manager on the profile | Gives Google's grant back, stops syncing, deletes stored review content |
| Day 45 to 60 | A final written demand for the balance | Decides between collection and a write-off | |

Paying at any point before day 30 restores everything at once (`invoice.paid`).

## Disputes, refunds and cancelling

- **Disputes.** A card dispute costs $15 when it arrives and another $15 to contest it, refunded on a win ([Stripe](https://support.stripe.com/questions/june-2025-pricing-updates-for-disputes)). Answer with:
  - the signed terms;
  - the invoices;
  - the platform's record of who approved which reply, and when.
- **Cancelling.** A monthly client cancels at the end of the paid period, from the customer portal or by asking. There's no partial refund.
- **Annual refunds.** Unused whole months are refunded at the monthly rate, which takes back the annual discount.
- **Setup.** The setup fee isn't refunded once the guidance workshop has happened.
- **Leaving.** A client who leaves gets the same export as at day 30, and BASH removes itself as a manager the same day.

## Sales tax: ask the accountant before the first Colorado client

What the state and city pages say today:

- **Illinois (Beit Shawarma, Evanston).**
  - **SaaS:** The Department of Revenue says it "is generally not subject to Illinois sales tax" when nothing is downloaded. That's in a non-binding letter, [ST-26-0026-GIL](https://taxarchive.illinois.gov/content/dam/soi/en/web/taxarchive/research/legal/letter-rulings/sales-tax/2026/st26-0026-gil.pdf), from July 2026. Clients use the studio in a browser; nothing is downloaded.
  - **Chicago:** Chicago's cloud tax (its Personal Property Lease Transaction Tax) is 15%, with 20% proposed for 2027, and it follows where the software is used. Evanston has no such tax ([home-rule taxes](https://cityofevanston.org/business/home_rule_taxes/index.php)). The Chicago figures come from secondary sources, because the city's pages refused automated reads.
- **Colorado.**
  - **Services:** The state "does not generally impose sales tax on services" ([sales tax guide](https://tax.colorado.gov/sales-tax-guide)).
  - **Hosted software:** Not taxed at the state level through 2026. From January 1, 2027, [HB26-1223](https://leg.colorado.gov/bills/hb26-1223) makes software generally taxable, remote access included. The exceptions are custom software and a negotiated license signed by both parties; a click-through agreement doesn't count. The state is still writing the rules ([Department of Revenue, October 2026](https://tax.colorado.gov/sites/default/files/2026-10/SUTT_Computer_Software_Oct_2026.pdf)).
- **Denver.** Denver already taxes SaaS at 5.15% (9.15% combined) when it's used in Denver. Consulting isn't taxed, but a service the customer must buy to get the software is taxed even when it's listed separately (Denver Tax Guide, Topics 18 and 70; [business tax FAQ](https://denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Department-of-Finance/Our-Divisions/Treasury/Business-Tax-Information/Business-Tax-FAQ)).

Questions for the accountant:

1. Must BASH collect Denver's tax on the platform part of a Denver client's fee now, and register?
2. From 2027, does a signed engagement agreement meet Colorado's negotiated-license exception?
3. Should invoices separate platform access from services, and is the setup fee taxable where the software is?

Stripe Tax costs 0.5% per transaction and only works where BASH is registered ([pricing](https://stripe.com/tax/pricing)). Turn it on once a registration exists; until then, Illinois clients need no tax line.

## The books

- **No first-party sync.** Stripe has no QuickBooks Online sync of its own ([Stripe](https://docs.stripe.com/stripe-apps/accounting-software-integrations)). The third-party options:
  - Acodei, from $12 a month by its own page (Stripe's listing says there's a free tier);
  - Synder, from $65 a month;
  - Intuit's own Stripe Connector, which publishes no price.
- **What the sync books:**
  - revenue at the gross price;
  - Stripe's fees as an expense;
  - each payout matched to its bank deposit.
- **Revenue recognition:**
  - **Monthly fees:** revenue in the month of service.
  - **Annual prepayments:** deferred and recognized monthly.
  - **Setup fees:** ask the accountant whether they're deferred over the expected relationship.

## The integration in zer0-CMS (phase 1)

It's a new `billing` app, with an ADR of its own first. Its parts:

- **Records:**
  - `Account`: the client, their Stripe customer and subscription, their sites, tier, status, seats and the end of the current period.
  - `BillingEvent`: one row per Stripe event ID, append-only, with its type, when it arrived and when it was processed.
  - `UsageReport`: per location per day, the count sent and the meter event identifier.
- **Webhook:**
  - **Where it lands:** `/api/v2/billing/stripe/`.
  - **What it checks:** the `Stripe-Signature` header (an HMAC over the timestamp and the raw body), refusing events older than five minutes.
  - **What it does:** stores the event ID (a repeat is ignored), queues the work on the Celery worker, and answers at once.
  - **Why it must be fast and idempotent:** Stripe retries failed deliveries for three days, and events can arrive twice or out of order ([webhooks](https://docs.stripe.com/webhooks)).
- **Entitlements:** one function, `entitled(profile, feature)`, read by:
  - the reputation agent's trigger (auto draft);
  - the studio (the banner and seats);
  - the Done for you queue.

  It never changes the owner's own `auto_draft` or `armed` settings, so paying restores the client's setup as they left it.
- **Usage:** a nightly scheduled job counts each location's reviews that BASH approved that day and sends them to the `reviews_handled` meter, with `"{profile public id}:{date}"` as the identifier so a retry can't bill twice. It runs daily, not monthly, because Google's 30-day limit can delete the review rows. Only counts leave the platform, never review text.
- **Billing link:** "Billing" in the studio's account menu opens a customer portal session, created server-side for the signed-in person's account.
- **Event:** `billing.account.changed.v1`, a CloudEvent in `schemas/events/`, when a status changes, for the studio's banner and the operations console.
- **Keys:**
  - A restricted Stripe key and the webhook secret live in the platform's environment, never in a repository.
  - Development uses test-mode keys and the Stripe CLI to forward webhooks.
  - Recorded webhook fixtures keep the tests offline.

What each Stripe event does ([subscription webhooks](https://docs.stripe.com/billing/subscriptions/webhooks)):

| Event | The platform |
| --- | --- |
| `checkout.session.completed` | Links the customer and subscription to the account and its sites |
| `customer.subscription.created`, `.updated` | Mirrors tier, status, locations and period end; re-reads entitlements |
| `customer.subscription.trial_will_end` | Reminds the owner that the supervised start is ending |
| `customer.subscription.deleted` | Starts the day-30 offboarding |
| `invoice.created` | Answers at once: without a success reply, Stripe holds the invoice up to 72 hours |
| `invoice.paid` | Clears the banner, restores entitlements |
| `invoice.payment_failed` | Shows the banner, alerts BASH, starts the collections clock |
| `invoice.payment_action_required` | Shows the banner with the hosted invoice link (the bank wants the cardholder to confirm) |
| `charge.dispute.created` | Alerts BASH and gathers the evidence |
| `charge.refunded` | Records it |

What each status allows:

| Status | Sync | AI drafts | BASH approves (Done for you) | Owner writes and posts | Monthly report |
| --- | --- | --- | --- | --- | --- |
| `trialing` (the supervised start) | Yes | Yes | Yes | Yes, once the profile is armed | No |
| `active` | Yes | Yes | Yes | Yes | Yes |
| `past_due` (retries running) | Yes | Yes | Yes | Yes | Yes |
| `unpaid` (retries ended) | Yes | Paused | Paused | Yes | Paused |
| `canceled` | Stopped, grant given back | No | No | In Google, directly | Final export |

## Build order

| Phase | When | What |
| --- | --- | --- |
| 0 | The first clients | Stripe products and prices, Checkout links sent by hand, the customer portal, retries and reminder emails on, a sync to the books. BASH follows the collections timeline by hand, pausing drafting with the profile's own switch. No code. |
| 1 | When a client signs up without BASH, or the second Done for you client signs | The `billing` app: webhook, `Account` mirror, entitlements, the studio's Billing link and banner |
| 2 | When Done for you has overage to bill, or Portal sells from the website | The usage meter, and a public Checkout for Portal |

## Open decisions

1. Stripe, or QuickBooks Payments with no integration, for the first clients.
2. The collections timeline's days, and whether day 30 cancels or waits longer.
3. The refund terms above.
4. The accountant's answers on Denver, Colorado from 2027, and the setup fee.
5. Which sync to the books.
