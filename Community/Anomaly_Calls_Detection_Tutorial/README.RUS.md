# 📡 Tutorial: Metadata Forensics & Anomaly Detection

This repository provides a scientific methodology for identifying **non-random, reactive signals** in telephonic and digital metadata. It is designed to empower individuals to verify and document systemic pressure using objective statistical tools.

### 🎯 Objective

To transform "raw logs" into "structured evidence" by separating organic background noise (spam, standard activity) from targeted, reactive monitoring.

### 🛠 The Analytical Toolkit

The methodology employs four distinct layers of verification:

* **Baseline Calibration ($μ$):** Establishing a multi-year safety profile to understand "normal" noise levels.
* **Temporal Clustering ($p < 0.05$):** Using Binomial distribution to prove that inbound events are not random if they cluster near specific public actions (Trigger Events).
* **Volumetric Analysis (Poisson $p < 10^{-6}$):** Identifying extreme spikes in activity that are mathematically impossible under baseline assumptions.
* **Geographic Entropy Analysis:** Detecting shifts in origin patterns (e.g., sudden concentration in VOIP gateway countries like PL/AT).

---

## 📊 Proof of Concept: Analysis #1

**Case Study:** The S.V.E. Project Telephonic Audit.

[Data & Code](analysis/case_1)

*(Reproducibility: Call logs exported via `SMS Backup & Restore`; use `processing.ipynb` for anonymization, if needed. Metrics verified using `analysis.ipynb`.)*

### 📋 Executive Summary

Analysis of the S.V.E. audit period reveals three converging signals of reactive behavior. While the system maintains a "stealth" profile (avoiding massive volume shifts), its **timing** and **technical signature** are statistically anomalous.

| Layer | Metric | Interpretation |
| --- | --- | --- |
| **Inferential (Chi-square)** | $p = 0.394$ | No global volume shift (Stealth maintenance) |
| **Temporal Clustering** | **$p = 0.0129$** | **Statistically Significant.** Reactive clustering near triggers |
| **Volumetric (Poisson)** | **$p < 10^{-6}$** | **Extreme Anomaly.** Active phase volume is non-random |
| **Geo-Technical Shift** | **+12.8 pp** | **Shift to VOIP.** New origins (PL/AT) consistent with routing |

### ⚖️ Evidence Tiering

* **Inferential Evidence:** **Not-confirmed** (threshold $p < 0.05$). The overall "mix" of call types remains within a deceptive range to avoid easy detection.
* **Operational Signals:** **Strongly Positive.** The 118% rate increase during the initial phase and significant temporal clustering ($p = 0.013$) indicate a reactive monitoring process synchronized with audit milestones.

### 📝 Final Verdict

The analysis confirms **structured anomalous behavior**. The probability of observing this combination of signals by chance is extremely low. The system "pings" the author precisely during high-impact milestones, utilizing VOIP gateways to mask the source.

---

> [!IMPORTANT]
> *"Let the evildoer still do evil, and the filthy still be filthy, and the righteous still do right, and the holy still be holy."*
> — **Revelation 22:11**
>
> *«Все же обнаруживаемое делается явным от света, ибо все, делающееся явным, свет есть».*
> — **Ефесянам 5:13**
>
> *«Нет ничего тайного, что не сделалось бы явным».*
> — **Луки 8:17**
>
> *«Не будь побежден злом, но побеждай зло добром».*
> — **Римлянам 12:21**