# Roadmap v2: GitHub + OSF Blocks / ROLAND Insurance — All Tracks

**Subject:** Account blocks at GitHub ("skovnats", 07–24 April 2026) and at OSF ("skovnats@gmail.com", pre-emptive SPAM flag, early April 2026); ROLAND Claim S-26-01720899; possible common technical cause to be investigated.
**Owner:** Dr. Artiom Kovnatsky
**Status as of 27 May 2026**

---

## Working hypothesis (to be tested, not asserted)

Two automated actions on two independent platforms in the same week, both based on automated abuse/spam detection, both occurring against accounts that had no problematic activity. The simplest explanation consistent with available evidence is a **shared technical signal** — most likely an IP-address or IP-neighbourhood reputation signal — being consulted independently by both platforms' anti-abuse systems. Center for Open Science has publicly stated (academic literature, 2024) that "suspicious activity from a nearby IP address" is one factor in their spam filtering.

This hypothesis is testable. Track 0 (below) tests it without any legal action.

---

## Track 0 — Direct technical investigation (do this first, today, free)

The cheapest and fastest way to test the hypothesis. None of this requires letters, lawyers, or waiting periods.

| Step | Action | Source |
|---|---|---|
| 0.1 | Determine current public IP (with and without VPN, separately) | ifconfig.me, ipinfo.io |
| 0.2 | Check IP against public abuse databases | abuseipdb.com, multirbl.valli.org/lookup, mxtoolbox.com/blacklists.aspx, spamhaus.org |
| 0.3 | Check email reputation | haveibeenpwned.com (both skovnats@gmail.com and artiom.kovnatsky@gmail.com) |
| 0.4 | Identify the CIDR range your residential ISP assigns and its reputation history | bgp.he.net (enter IP) |
| 0.5 | Try sign-up to a new neutral platform (e.g. a fresh Hugging Face or Hashnode account) from your normal network — see whether it succeeds without flagging | direct test |
| 0.6 | Repeat test from a different network (mobile hotspot or different ISP) | direct test |

**Possible outcomes:**

- **If IP is on one or more blocklists** → the technical cause is identified. This is the most likely outcome. Action: request removal from blocklists; switch network if needed; record findings as supporting evidence for the GDPR responses.
- **If IP is clean across all checks** → the hypothesis weakens; GDPR responses will need to identify the real trigger.
- **If new-platform sign-up succeeds normally** → the issue is platform-specific or historical (already-fixed CIDR reputation), not active.

This step is free, takes ~30 minutes, and can resolve the question before any legal action.

---

## Track 1 — Insurance (ROLAND Rechtsschutz)

| Step | Action | Deadline / addressee |
|---|---|---|
| 1.1 | Send Final Appeal v3 to ROLAND | claims@roland-rechtsschutz.de — send now |
| 1.2 | Wait for substantive response | by 10 June 2026 |
| 1.3 | If Deckungszusage received | hand the GitHub case to a Fachanwalt für IT-Recht; narrow mandate: refund + written acknowledgment |
| 1.4 | If denied or silent | submit full chronology to Versicherungsombudsmann e.V. (versicherungsombudsmann.de — free, binding up to €10,000) |

**Realistic outcome:** Deckungszusage at minimum for the Privat-Rechtsschutz (consumer-contract) aspect.

---

## Track 2 — GitHub: GDPR Art. 15 / DSA Art. 17 — Data and reasoning

| Step | Action | Deadline / addressee |
|---|---|---|
| 2.1 | Send GDPR/DSA Request letter to GitHub | privacy@github.com, cc dpo@github.com — send now |
| 2.2 | Wait for response | by 27 June 2026 (one month under GDPR Art. 12(3)) |
| 2.3 | Search DSA Transparency Database for GitHub statements | transparency.dsa.ec.europa.eu — search platform=GitHub for April 2026 |
| 2.4 | Review response: identify any IP-reputation, classifier, or third-party signal cited | match findings with Track 0 |
| 2.5 | If response is incomplete or refused | (a) complaint to BlnBDI (datenschutz-berlin.de) under Art. 77 GDPR; (b) complaint to DSC at Bundesnetzagentur (dsc.bund.de) under Art. 53 DSA |

**Realistic outcome:** Records identifying what was applied to the account; identification of the classifier/trigger; a formalised Statement of Reasons.

---

## Track 3 — OSF: GDPR Art. 15 / DSA Art. 17 — Data and reasoning

| Step | Action | Deadline / addressee |
|---|---|---|
| 3.1 | Send GDPR/DSA Request letter to OSF / COS | support@osf.io, cc contact@cos.io — send now |
| 3.2 | Wait for response | by 27 June 2026 (one month under GDPR Art. 12(3)) |
| 3.3 | Search DSA Transparency Database for OSF statements | transparency.dsa.ec.europa.eu — search by platform |
| 3.4 | Review response: identify whether IP-neighbourhood / email reputation / external blocklist signal was used (as documented in COS literature) | cross-reference with Track 0 and Track 2 findings |
| 3.5 | If non-response continues past 27.06.2026 | given OSF's 38+ day silence already on file, this becomes a clear Art. 12 GDPR violation: lodge complaint with BlnBDI immediately; lodge parallel complaint with DSC under Art. 53 DSA |

**Specific aggravating factor here:** the action was **pre-emptive** — taken against an account with no platform activity, no uploads, no interactions. This is a stronger transparency demand than the GitHub case.

**Realistic outcome:** Identification of the spam-filter signal that triggered the action. If — as COS's own published methodology suggests — it was an IP-neighbourhood signal, this would corroborate the technical hypothesis and likely explain the GitHub block as well.

---

## Track 4 — Consumer-contract refund (direct to GitHub)

| Step | Action | Deadline / addressee |
|---|---|---|
| 4.1 | Direct demand for refund of GitHub Pro for the inaccessibility period 07–24 April 2026 | billing@github.com / via Support |
| 4.2 | If refused | PayPal dispute on the original transaction; or hand to Fachanwalt once Deckungszusage from ROLAND is in |
| 4.3 | Goal | refund + written acknowledgment under § 812 BGB |

---

## Cross-track synthesis (after responses arrive)

Once Track 2 (GitHub) and Track 3 (OSF) responses arrive (deadlines both 27 June 2026):

- **If both responses cite IP-neighbourhood or shared blocklist signals** → technical cause confirmed. Document the finding. Pursue blocklist removals. The pattern is explained without need for any further hypothesis. The insurance/refund tracks proceed in parallel for their own narrow outcomes.

- **If one cites a technical signal and the other does not** → partial explanation; further investigation needed.

- **If neither identifies a coherent reason** → escalate via BlnBDI and DSC; non-transparency is itself a regulatory violation worth pursuing.

- **If responses appear contradictory or evasive** → consider DSA Article 21 out-of-court dispute settlement, which is cheaper and faster than litigation.

---

## What is still NOT achievable through any track

Stated again, because the question keeps recurring:

- **Anonymised cross-user moderation data** for population-level bias testing is not obtainable through individual GDPR, DSA, or civil litigation in Germany / EU.
- A **court-ordered audit** of GitHub's or OSF's algorithms — there is no procedural basis for this in German civil law for an individual claimant.
- A **public apology** from either platform — not generally obtainable through German civil law.
- Compensation for **"delayed life's work" or "lost momentum"** — without specific lost contracts with documented amounts, German courts award nothing under this head.

What two-incident data does NOT yet establish:

- **Coordinated censorship** is not the simplest explanation of the available evidence. A shared technical signal (IP reputation, common abuse-detection vendor, similar heuristics) is consistent with COS's own published methodology and is the standard explanation for cross-platform false-positive flagging. This should not be discounted in favour of stronger hypotheses without specific evidence.

---

## Decision tree

```
Today (27 May 2026)
├── Run Track 0 (technical investigation) — ~30 minutes
├── Send Track 1 letter (ROLAND v3)
├── Send Track 2 letter (GitHub GDPR/DSA)
└── Send Track 3 letter (OSF GDPR/DSA)

Day +14 (10 June 2026)
├── ROLAND deadline
│   ├── Deckungszusage → Fachanwalt for narrow GitHub case (Track 4)
│   └── Denied / silent → Versicherungsombudsmann

Day +31 (27 June 2026)
├── GitHub deadline (Track 2)
│   ├── Substantive response → synthesise with Track 3
│   └── Incomplete → BlnBDI + DSC
├── OSF deadline (Track 3)
│   ├── Substantive response → synthesise with Track 2
│   └── Incomplete → BlnBDI + DSC (with the additional 38+ day delay on the record)

After both responses
├── Synthesise: is there a common technical signal? (Most likely answer.)
└── Adjust further action accordingly.
```

---

## Energy and time budget

Total realistic effort across all tracks: 15–30 hours spread over 2 months. Most of it is review of responses and forwarding to escalation bodies. Beyond this envelope, marginal returns drop steeply. Time beyond should go to stenon work and SVE, not to this dispute.
