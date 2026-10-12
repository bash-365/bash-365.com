# Domains and email: the M365 tenant runbook

This page documents the BASH domain portfolio and email architecture in the Microsoft 365 tenant, including the 2026-08 MX outage and its standing workaround. It is an internal operations doc — `docs/` is excluded from the Jekyll build.

## The domain portfolio

All domains are verified, Authoritative accepted domains in the single M365 tenant (`bashconsultantscom.onmicrosoft.com`, "BASH Consulting LLC"), and all of them delegate DNS to **Microsoft 365's own nameservers** (`ns1–ns4.bdm.microsoftonline.com`). DNS records are managed in the M365 admin center (**Settings → Domains → \<domain\> → DNS records**), *not* at Squarespace or Google — the leftover `MS=`/`google-site-verification` TXT records are relics, not evidence of where the zone lives.

| Domain | Role | Notes |
| --- | --- | --- |
| `bash-365.com` | **Primary.** Canonical site domain + default M365 domain | MX `bash365-com01b.mail.protection.outlook.com` (the tenant's live mail endpoint) |
| `bashconsultants.com` | Legacy. Retired site mirror; receive-only email alias domain | MX: see the outage section below |
| `eissalab.com` | Secondary, parked in the tenant | Authoritative accepted domain |
| `bashconsultantscom.onmicrosoft.com` | Tenant fallback (MOERA) | Never referenced publicly |

Both site domains' A/www records point at GitHub Pages (`amr-bash.github.io`, `185.199.108–111.153`).

## Email architecture

One mailbox, two addresses. The `AmrAbdel-Motaleb` mailbox has primary SMTP **`amr@bash-365.com`** with **`amr@bashconsultants.com`** as a receiving proxy alias — mail to either address lands in the same mailbox, and outbound sends as `amr@bash-365.com`. No forwarding rules, no second mailbox. This was the end state of the 2026-08 bash-365 email migration.

Admin access for scripted changes: PowerShell + `ExchangeOnlineManagement` / Microsoft Graph modules. **Device-code sign-in is blocked** by the tenant's Conditional Access baseline (error 53003) — use plain interactive browser auth (`Connect-ExchangeOnline`, `Connect-MgGraph`) instead.

The site's published contact address is **`info@bash-365.com`** (`_config.yml` `contact-email`, `_data/entity/info.yml`, the homepage FAQ, the privacy policy, `llms.txt`, and the chat widget's messages); it exists as a recipient in the tenant (confirmed 2026-10-12). If it is ever removed, the published contact email silently bounces — check with `Get-Recipient info@bash-365.com` before changing mail routing.

## The 2026-08-10 MX outage and its workaround

**Symptom:** mail sent to `amr@bashconsultants.com` from external senders (e.g. Gmail) never arrived.

**Root cause:** the Microsoft-managed MX record for `bashconsultants.com` points at `bashconsultants-com.mail.protection.outlook.com`, a hostname that is **NXDOMAIN on every public resolver** — Microsoft decommissioned the old-style endpoint in its sharded mail-endpoint migration (`bash-365.com` got a new-style `…-com01b` endpoint; this domain's was dropped) without updating the tenant's expected records. The admin center's health check still reports the record "OK" because it only compares DNS against its own (stale) expectation, and Graph `serviceConfigurationRecords` still returns the dead name. Senders that cannot resolve the only MX target eventually bounce the mail.

**Workaround in place (2026-08-10):** a custom **MX priority 10 → `bash365-com01b.mail.protection.outlook.com`** was added alongside the dead managed priority-0 record. Per RFC 5321, senders skip an MX target that does not resolve and fall through to the next priority, so delivery works. Exchange Online Protection front doors accept mail for every accepted domain in the tenant, so the bash-365 endpoint happily receives bashconsultants.com mail. Note the admin center refuses additional MX records while the "Exchange" service manages the domain's records — the custom record was added after reconfiguring the domain's services via the **Manage DNS** wizard.

**Do not remove the custom priority-10 MX** until Microsoft re-provisions a working endpoint for the domain. The proper fix is a Microsoft support ticket: *the tenant's expected MX target for bashconsultants.com is NXDOMAIN; please re-provision the mail endpoint.*

Verification one-liners:

```bash
dig +short MX bashconsultants.com              # both records; prio-10 must remain
dig +short A  bash365-com01b.mail.protection.outlook.com   # must resolve
dig +short A  bashconsultants-com.mail.protection.outlook.com  # NXDOMAIN until MS fixes it
```

## Mail authentication posture

| Record | bash-365.com | bashconsultants.com |
| --- | --- | --- |
| SPF | `v=spf1 include:spf.protection.outlook.com -all` | same |
| DKIM | selector1/selector2 CNAMEs → onmicrosoft | same |
| DMARC | `p=none; rua=mailto:amr@bash-365.com` (added 2026-08-10) | `p=none; rua=mailto:postmaster@…, mailto:dmarc@…` |

Next step when DMARC reports look clean for a few weeks: tighten `bash-365.com` to `p=quarantine`, then `p=reject`.

## Cleanup backlog (cosmetic, not urgent)

The `bashconsultants.com` zone still carries dead weight from its Google Workspace era, all removable in the admin center's DNS records page:

- The managed priority-0 MX (harmless while unresolvable, but clutter — removable only if Microsoft fixes or fully detaches it)
- Orphaned TXT `include:_spf.google.com ~all` (not a valid SPF record — no `v=spf1` prefix — so it is ignored)
- Two `MS=…` verification TXTs and the `google-site-verification` TXT
- `google._domainkey` DKIM TXT (Google Workspace signing key, unused)
- Seven `ghs.googlehosted.com` CNAMEs: `calendar`, `docs`, `drive`, `groups`, `mail`, `sites`, `start`
