# **SVE-Case-Activation-Protocol.md**

## **PURPOSE**

Defines how SVE-Case-N precedents transition from templates to binding interpretations of the SVE Public License v1.3.

---

## **AUTHORITY**

Under **Declaration of Interim Custody v1.3** and **SVE Public License v1.3 §8 (Evolution & Amendment)**, case activation follows distributed governance:

- **Exodus 3.0 Initiative** (primary custodian)
- **Authorized Public Custodians** (SVE Registry)
- **Distributed Verification Network** (DVN, if DAO inactive >12 months)

---

## **ACTIVATION PROCESS**

### **Phase 1: Draft (Template Status)**
- Any verified custodian or community member drafts case
- Published as template (`SVE-Case-[N]-TEMPLATE.md`)
- Status: ⚪ **Non-binding** (reference only)

### **Phase 2: Community Review (14 Days)**
- Public comment period via GitHub Issues or forum
- 31-AI validation (Jesus + Socrates + Perelman + Ivan-Durak)
- Minimum 3 custodian endorsements required

### **Phase 3: Vote (7 Days)**
- **Snapshot vote** or equivalent transparent mechanism
- **Simple majority** (>50%) of verified participants
- Quorum: ≥10 votes OR ≥3 custodians

### **Phase 4: Signature & Activation**
- **Single custodian signature** sufficient if vote passed
- Signature methods (priority order):
  1. eIDAS/QES (Estonia) - court-recognized
  2. PGP (verified public key in SVE Registry)
  3. Multi-sig (≥2 custodians, blockchain-recorded)
- File renamed: `SVE-Case-[N].md` (removes "-TEMPLATE")
- Status: 🟢 **Active** (binding on all SVE users)

### **Phase 5: Publication (Immediate)**
- Hash recorded (SHA-256)
- Published: GitHub + IPFS + public timestamp
- Effective: **30 days after publication** (grace period)

---

## **EMERGENCY ACTIVATION**

If **urgent threat to integrity** (e.g., active exploitation of loophole):

- **≥2 custodians** may activate immediately (skip review/vote)
- Temporary (90 days) → must complete standard process to make permanent
- Public justification required within 24 hours

---

## **DEACTIVATION (SUNSET)**

Cases may be superseded or archived:

- **Veche vote** (≥67% supermajority)
- New case replaces old (e.g., Case-01-v2 supersedes Case-01)
- Old case archived (not deleted - historical record)
- Grace period: 90 days overlap

---

## **SIGNATURE REQUIREMENTS**

### **Individual Custodian:**
```
Signed by: [Name]
Role: Authorized Public Custodian
Date: [YYYY-MM-DD]
Signature: [eIDAS/QES or PGP fingerprint]
Hash: [SHA-256 of file]
```

### **Multi-Sig (≥2 Custodians):**
```
Signed by: [Name 1], [Name 2]
Roles: Exodus 3.0 + Public Custodian
Date: [YYYY-MM-DD]
Blockchain proof: [Transaction ID]
Hash: [SHA-256 of file]
```

---

## **CASE HIERARCHY**

If cases conflict:

1. **Meta-License v1.3** (supreme - immutable clauses)
2. **Later case** supersedes earlier (unless explicit override)
3. **More specific** case overrides general
4. **31-AI validation** resolves ambiguity

---

## **TRANSPARENCY**

All activation records published in:
- **SVE Registry** (GitHub: `/cases/active/`)
- **IPFS** (permanent hash)
- **Public log** (timestamped chronological list)

Format:
```
Case-01 | Activated: 2026-03-19 | Custodian: [Name] | Hash: [SHA-256]
Case-02 | Activated: 2026-03-19 | Custodian: [Name] | Hash: [SHA-256]
Case-03 | Template | Not yet active | Hash: [SHA-256]
```

---

## **CURRENT STATUS**

```
Case-01: Spirit Over Letter          → ⚪ Template (awaiting activation)
Case-02: Legal Representation Model  → ⚪ Template (awaiting activation)
Case-03: Medical Data Protection     → ⚪ Template (awaiting activation)
```

**To activate:** Follow Phase 1-5 above.

---

## **GOVERNANCE REFERENCE**

Per **Declaration of Interim Custody v1.3 §5a**:

> "If the S.V.E. DAO becomes inactive, compromised, or never established, all core functions — licensing, audits, updates, and enforcement — automatically devolve to the **Distributed Verification Network (DVN)**."

This protocol operates under DVN authority if DAO unavailable.

---

**Version:** 1.0  
**Effective:** Upon publication  
**Governed by:** SVE Public License v1.3 + Declaration of Interim Custody v1.3  
**Hash:** [To be generated]

---

**"Cases activate when community validates truth."** ✝️

---

**END OF PROTOCOL**