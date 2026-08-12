---
share_link: https://share.note.sx/qcrrrxfo#mnvyh3Y2iBMAlA3vCSYsWoNnCQ7/eDuCjDA/7hT1KW8
share_updated: 2026-02-11T20:15:30+01:00
---
# FINAL SUBMISSION CHECKLIST — v5

## "Who Watches the Watchmen?" — TIK Framework for NeurIPS

**File:** `neurips_TIK_FINAL_v5.tex`  
**Structure:** 7 main sections + 18 appendices (A–R)  
**Target:** ≤ 9 pages main text + unlimited appendix

---

## 🔴 PHASE 0: THE ELEPHANT — ARE THE NUMBERS REAL?

> **Nothing else matters until this table is answered.**  
> Think of it like building a house: no point choosing wallpaper if the foundation is sand.

| #   | Claim                                 | Location         | Real? | If Projected: Action              | Effort         |
| --- | ------------------------------------- | ---------------- | ----- | --------------------------------- | -------------- |
| 1   | 91% AUC H/F detection                 | Sec 4, Table 4   | ☐     | Train RoBERTa on 9K questions     | ~2 days, 1 GPU |
| 2   | σ=0.04/0.11 perturbation stability    | Sec 5.1, Table 5 | ☐     | Run Monte Carlo perturbations     | ~1 day         |
| 3   | r=+0.72 uncertainty↔holes correlation | Sec 5.2, Table 6 | ☐     | Falls from #2 above               | —              |
| 4   | 94% Socratic convergence rate         | Sec 3.7          | ☐     | Run 50 questions through pipeline | ~2 days + API  |
| 5   | d=0.83 human eval effect size         | Sec 7.2, Table 7 | ☐     | Prolific study (N=444)            | ~$5K, ~1 week  |
| 6   | r=+0.89 TIK↔human correlation         | Sec 6            | ☐     | Falls from #5 above               | —              |
| 7   | Active learning 0.54→0.86             | App E            | ☐     | Run actual loop                   | ~1 day         |
| 8   | Cross-lingual MAD=0.04                | Sec 6 (merged)   | ☐     | Translate 100q × 6 langs          | ~$200, 1 day   |

**If ALL real:** ✅ Skip to Phase 1.  
**If ANY projected:** ⛔ This IS the blocker list. Everything else waits.

---

## 🔴 PHASE 1: STRUCTURAL BLOCKERS (paper not submittable without these)

### B1. Compile & Page Budget

- [ ] Compile with `neurips_2024.sty` — verify no errors
- [ ] Main text ≤ 9 pages before references
- [ ] If over: tighten Sec 3 (method), compress tables, reduce remark boxes

### B2. Four Figures (Only These Four)

Every empirical claim needs one figure. No claim = no figure.

|#|Figure|Location|Why Blocking|
|---|---|---|---|
|1|Training curves + confusion matrix|Sec 4|"Did you actually train this?"|
|2|Perturbation scatter + violin plots|Sec 5|Shows robustness is real|
|3|Benchmark comparison bar chart|Sec 6 (Table 3)|The money shot|
|4|Human eval forest plot (Cohen's d)|Sec 7|d=0.83 needs visualization|

- [ ] Create these 4 figures
- [ ] All remaining TODOs → gray placeholder boxes (use `\placeholderfig{}{}` )

### B3. Bibliography — 5 Previously Missing Cites (Now Added)

- [ ] Verify all `\cite{}` resolve against `\bibitem` entries
- [ ] Added: Emelin (Moral Stories), Lourie (Scruples), Talmor (CommonsenseQA), Hendrycks (MMLU), Maia (GAIA)

### B4. Cross-References

- [ ] All `\ref{}` resolve (target: ~80 labels)
- [ ] Cyrillic renders correctly (test T2A + babel)
- [ ] New v5 labels all resolve: `app:self-audit`, `app:integration`, `app:baselines`, etc.

### B5. Appendix Content — Fill the Stubs

These appendices are referenced but incomplete:

|App|Status|Action|
|---|---|---|
|O (Datasheet)|Stub|Fill all 8 Gebru sections (1 paragraph each)|
|P (Human Eval)|Stub|IRB text, 3 scenarios, scales, ANOVA, demographics|
|K (Termination)|Algorithm only|Add comparison table: TIK vs GPT-4/Claude/Llama on 50–100 forbidden-fruit questions|

---

## 🟡 PHASE 2: MAKES IT CONVINCING (after blockers)

### C1. Strengthen the 3 Weakest Links

|Weakness|Fix|Time|
|---|---|---|
|Circularity ("LLM labels LLM")|Expand App D: show disagreement map (which holes do LLMs miss vs humans?)|3h|
|"Numbers look too clean"|Add bootstrap CI ranges to Table 3 (already have σ values — surface them)|1h|
|No documented failure|Already added 1 failure case in Sec 5.2. Verify it's concrete and honest.|30min|

### C2. Tone Calibration

- [ ] Search for rhetorical flourishes; soften 10–15% of strongest claims
- [ ] Verify Gödel argument is framed as "formal motivation" not "proof about all AI"
- [ ] Ensure no remaining language that reads as "manifesto" rather than "infrastructure paper"

### C3. One More Socratic Reversal Example

- [ ] Write 1 worked example from Social Chemistry for App F. Target: 4 total examples.

---

## 🟢 PHASE 3: MAKES IT 9/10 (stretch — if time permits)

|#|Experiment|What It Proves|Effort|
|---|---|---|---|
|S1|**Hole rate → downstream failure.** Fine-tune model on high/med/low TIK benchmarks; show correlation with independent human eval.|TIK is a _law_, not just a metric|2 weeks|
|S2|**Open-model replication.** Run pipeline with Llama/Mixtral; show `r ≥ 0.82` with GPT-4|Not model-dependent|3 days|
|S3|**Causal training experiment.** Remove top-H questions → retrain → measure bias reduction|Killer evidence|1 week|

**If you do only one: S1.** It transforms the paper from "tool" to "law."

---

## 🔧 PHASE 4: USING ELICIT TO MAKE THE PAPER BULLETPROOF

### 🔗 https://elicit.com/

Think of Elicit as a **literature X-ray machine**: it finds the papers that a hostile reviewer would cite to attack you, _before_ the reviewer does.

### Step A: Literature Gap Hardening

Run these queries in Elicit:

```
Query 1: "meta-evaluation of AI ethics benchmarks"
Query 2: "formal arguments applying Gödel's incompleteness to AI safety"  
Query 3: "cross-cultural invariance in AI alignment"
Query 4: "dataset auditing frameworks with formal metrics"
Query 5: "common criticisms of benchmark auditing in machine learning"
Query 6: "normative uncertainty in social choice theory"
Query 7: "construct validity of AI evaluation benchmarks"
Query 8: "LLM-as-judge reliability and circularity"
```

**For each query, do:**

1. Open the top 10 results
2. Check: does any paper do something close to TIK?
3. If yes → add an explicit contrastive sentence in Related Work:
    - _"Unlike [X], we provide a computable, per-question meta-metric."_
    - _"Unlike [Y], we validate empirically across 9 benchmarks with 9K questions."_
    - _"Unlike [Z], our framework is kernel-agnostic and tested with 9 alternative kernels."_
4. If the paper is a genuine predecessor → cite it and explain the difference

### Step B: Attack Mining

```
Query: "What are common criticisms of benchmark auditing frameworks?"
Query: "criticisms of applying Gödel outside mathematics"
Query: "LLM evaluation circularity problems"
Query: "cultural bias in AI ethics measurement"
```

**Action:** For each criticism found:

- Check: is it already in our Limitations (Sec 7.3) or Self-Audit (App Q)?
- If not → add it
- Rule of thumb: **a reviewer who sees you already addressed their attack loses 50% of their aggression**

### Step C: Theoretical Reinforcement

```
Query: "formal treatments of normative uncertainty"
Query: "Arrow impossibility theorem applied to AI"
Query: "measurement theory construct validity AI"
Query: "social choice theory and preference aggregation AI"
```

**Action:** Find 2–3 rigorous papers and cite them in Appendix A (Gödel) section A.9 where we discuss Arrow, Tarski, Löb. This transforms "philosophical metaphor" into "well-grounded formal reasoning with literature support."

---

## 🔧 PHASE 5: USING NOTEBOOKLM AS A REVIEWER SIMULATOR

### 🔗 https://notebooklm.google.com/

Think of NotebookLM as a **simulated reviewer panel**: it reads your paper alongside top papers in the field and finds exactly the over-claims and inconsistencies that a real reviewer would catch.

### Step A: Setup — Upload These Documents

Upload to a single NotebookLM notebook:

1. **Your paper** (`neurips_TIK_FINAL_v5.tex` or a PDF version)
2. **5–10 top NeurIPS benchmark/evaluation papers**, e.g.:
    - Bowman & Dahl 2021 (What will it take to fix benchmarking?)
    - Gebru et al. 2021 (Datasheets for datasets)
    - Hendrycks et al. 2021 (ETHICS)
    - Awad et al. 2018 (Moral Machine)
    - Pasquini et al. 2024 (PertBench)
3. **2–3 critical papers on AI ethics and dataset bias**, e.g.:
    - Blodgett et al. 2020 (Language technology is power)
    - Hovy & Prabhumoye 2021 (Five sources of bias)
    - Gabriel 2020 (AI values and alignment)

### Step B: Weakness Detection — Ask These Prompts

```
Prompt 1: "What are the potential weaknesses or overstatements in the TIK paper?"

Prompt 2: "Where does the reasoning rely on analogies that are not fully justified? 
           List specific passages."

Prompt 3: "List all strong claims that would require replication or additional evidence 
           to be convincing at a top venue."

Prompt 4: "Which terms are used inconsistently or ambiguously across the paper?"

Prompt 5: "Compare the TIK paper's methodology to the benchmark evaluation approaches 
           in the other uploaded papers. Where is TIK strongest? Where is it weakest?"

Prompt 6: "If you were a skeptical reviewer trying to reject this paper, what would 
           be your top 5 arguments?"

Prompt 7: "Does the paper's theoretical framework (Gödel-based argument) hold up to 
           scrutiny? What are the logical gaps?"

Prompt 8: "Are the experimental results sufficient to support the claims? What 
           additional experiments would strengthen the paper?"
```

### Step C: Actions for Each Finding

For each flagged over-claim:

- [ ] Either soften the language ("we demonstrate" → "our results suggest")
- [ ] Or add supporting evidence (CI, additional experiment, citation)

For each inconsistent term:

- [ ] Standardize naming across entire paper (search & replace)
- [ ] Key terms to check: TIK components, kernel names, CogOS strata, judge names

For each logical gap:

- [ ] Verify it's addressed in App A (Gödel) scope limitations (A.10)
- [ ] Or add explicit acknowledgment in Limitations

### Step D: Claim Audit Mode

```
Prompt: "List every claim in this paper that contains a specific number 
         (percentage, correlation, effect size, etc.). For each, indicate 
         whether the paper provides sufficient methodological detail to 
         reproduce the result."
```

**Action:** Go through the list. For each claim:

- Is there a table? A figure? A method description?
- Could a reader reproduce it from the paper alone?
- If not → add missing detail to the relevant appendix

### Step E: Comparative Positioning

```
Prompt: "Based on all uploaded papers, how should the TIK paper position 
         itself in Related Work? What comparisons are missing?"

Prompt: "Which of the uploaded papers addresses problems similar to TIK? 
         How does TIK improve on their approach?"
```

**Action:** Update Related Work (Sec 2) with 2–3 additional contrastive sentences.

---

## 🔧 PHASE 6: NOTEBOOKLM — GENERATE AUDIO OVERVIEW (Bonus)

NotebookLM can generate an **audio discussion** of your paper — essentially a podcast where two AI voices discuss the paper's strengths and weaknesses. This is surprisingly useful for:

- Hearing how your arguments sound when explained aloud
- Catching jargon that doesn't land
- Identifying which parts are genuinely exciting vs. confusing

```
Action: Click "Generate Audio Overview" in NotebookLM after uploading all sources.
Listen for:
- Where the hosts sound confused (= a reviewer will be confused too)
- Where they sound excited (= this is your hook)
- Where they skip over details (= those details may not matter)
```

---

## 📋 PHASE 7: FINAL PRE-SUBMISSION SANITY CHECKS

- [ ] **All experiments are real** (Phase 0 table complete)
- [ ] Compiles clean with `neurips_2024.sty`
- [ ] Main text ≤ 9 pages
- [ ] 4 main-text figures present and high quality
- [ ] All remaining TODOs → gray placeholders
- [ ] All `\ref{}` and `\cite{}` resolve
- [ ] App O (Datasheet) complete (8 Gebru sections)
- [ ] App P (Human Eval Materials) complete
- [ ] Acknowledgments paragraph present
- [ ] Ethics Statement present and matches guidelines
- [ ] NeurIPS checklist (end of PDF) — all justifications updated
- [ ] No "Author Meta-Checklist" or internal notes in submission PDF
- [ ] De-anonymize for camera-ready only (authors, affiliations)
- [ ] Repository URL placeholder present
- [ ] Dataset DOI placeholder present
- [ ] Supplementary zip prepared (code, data, prompts, configs)
- [ ] PDF < 50MB
- [ ] **One honest read-through: "would I accept this?"**

---

## 📐 PAPER STRUCTURE SUMMARY (v5)

### Main Text (7 sections, ≤ 9 pages)

|#|Section|Content|
|---|---|---|
|1|Introduction|Griboyedov → Swift → problem → LLM⊕CogOS → contributions|
|2|Related Work|Benchmarks, meta-eval, robustness (PertBench/SPARTA/RoP)|
|3|Method|3+1+1 judges → TIK definition (7 components) → kernel → CogOS → Lyapunov brief|
|4|Learned Predictor|RoBERTa, 91% AUC, 12ms/q, circularity note|
|5|Robustness|Adversarial (3 vectors + Goodhart) + Uncertainty (MC, r=+0.72). **Merged.**|
|6|Benchmark Analysis|Table 3 (9 benchmarks) + cross-lingual + validation + BenchmarkMeta + baselines|
|7|Human Eval + Conclusion|N=444, d=0.83, 7 limitations, broader impact|

### Appendices (18 sections, A–R)

|App|Content|Status|
|---|---|---|
|A|Gödel argument (10 subsections, 9 proofs)|✅ Complete|
|B|9 alternative kernels comparison|✅ Complete|
|C|Kernel sensitivity analysis|✅ Complete|
|D|Multi-annotator agreement|✅ Complete|
|E|Active learning for benchmark curation|✅ Complete|
|F|Socratic Reversal worked examples (4)|⚠️ Need 1 more|
|G|Laputa–Lyapunov Index (LL-Index)|✅ Complete|
|H|Connection to AI regulation|✅ Complete|
|I|Living benchmarks + temporal drift|✅ Complete (merged)|
|J|Lyapunov full treatment + Bayesian|✅ Complete (merged)|
|K|Termination protocol|⚠️ Need comparison table|
|L|Baselines + ablation + saliency|✅ Complete (merged)|
|M|Ethical singularities|✅ Complete|
|N|Implementation + metric definitions|✅ Complete (merged)|
|O|BenchmarkMeta datasheet|❌ Need 8-section Gebru|
|P|Human evaluation materials|❌ Need full materials|
|Q|Self-audit and anticipated objections|✅ Complete|
|R|Practical integration and roadmap|✅ Complete|

### Formal Environment Count

|Type|Count|
|---|---|
|Axioms|4|
|Definitions|10|
|Propositions|8|
|Theorem|1|
|Corollary|1|
|Remarks|8|
|Observations|3|
|Examples|1|
|**Proofs**|**9**|

---

## 🎯 PRIORITY MATRIX: IF YOU HAVE LIMITED TIME

### 1 week before deadline:

1. ✅ Verify all numbers are real (Phase 0)
2. ✅ Create 4 figures
3. ✅ Fill App O + App P stubs
4. ✅ Run Elicit queries (Phase 4A–4B)
5. ✅ Compile and check page count

### 3 days before:

1. ✅ Run NotebookLM full audit (Phase 5)
2. ✅ Address top 5 weaknesses found
3. ✅ Final tone calibration pass
4. ✅ Verify all references resolve

### 1 day before:

1. ✅ One complete read-through
2. ✅ Remove any internal notes
3. ✅ Final compile
4. ✅ Prepare supplementary zip

---

## 🔑 WHAT WOULD FORCE A SKEPTICAL REVIEWER TO RAISE THEIR SCORE

Per the FAQ's simulated Reviewer #2, these changes convert "Reject" → "Borderline Accept":

1. ~~Remove religious framing from main text~~ → **Done in v5**: kernel described neutrally as "three independently-developed ethical traditions"
2. ~~Shorten Gödel chain in main text~~ → **Done in v5**: main text has 1-paragraph summary; full chain in Appendix A
3. Add fully human-labeled subset ≥3K questions → **Partially addressed** (N=500 human subset + r=0.89 agreement noted as limitation)
4. Add metric ablation study → **Partially addressed** (Goodhart + component ablation in text; full ablation left as future work)
5. ~~Remove normative license clause~~ → **Done in v5**: CC-BY-SA 4.0 standard license
6. ~~Tone down rhetorical metaphors~~ → **Done in v5**: trimmed throughout

**What would push to "Strong Accept":**

- Open-model replication (Phase 3, S2)
- Causal training experiment (Phase 3, S3)
- 3K+ human-annotated subset

---

С Богом! 🙏