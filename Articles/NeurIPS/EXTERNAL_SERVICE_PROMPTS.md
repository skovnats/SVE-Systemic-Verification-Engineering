# 🤖 Промпты для Внешних Сервисов
> Копируй и вставляй. Каждый промпт оптимизирован для конкретного сервиса.

---

## 1. ELICIT — Literature Review

### Промпт 1: Основной literature search
```
Research question: "What methods exist for meta-evaluating or auditing 
AI ethics benchmarks, measuring their validity, cultural bias, or 
hidden assumptions?"

I need papers that:
1. Critique specific AI ethics benchmarks (Moral Machine, ETHICS, TruthfulQA, etc.)
2. Propose frameworks for benchmark auditing or meta-evaluation
3. Study cultural bias in AI evaluation datasets
4. Apply formal methods (Gödel, Arrow's theorem, etc.) to AI alignment
5. Study "safetywashing" or validity of AI safety benchmarks

For each paper, I need:
- Main finding (1 sentence)
- Method used
- Key limitation
- Whether they provide a COMPUTABLE metric (yes/no)
- Relevance to "evaluating the evaluators" (1-10)
```

### Промпт 2: Safetywashing & benchmark validity
```
Find all papers related to "safetywashing" in AI — where safety 
benchmarks actually measure general capabilities rather than safety.

Also find papers on:
- "Benchmark lottery" effect in ML
- Construct validity failures in AI benchmarks  
- Systematic reviews of AI evaluation tools
- Inter-annotator disagreement in ethics benchmarks

Extract: methodology, key finding, sample size, year.
```

### Промпт 3: Gödelian arguments in AI
```
Find papers that apply Gödel's incompleteness theorems to AI safety, 
alignment, or the limits of machine reasoning.

Include work on:
- Self-reference problems in AI
- Formal limits of value alignment
- Tarski's undefinability applied to AI
- Arrow's impossibility theorem in AI ethics
- Normative uncertainty and value aggregation

For each: What exactly do they prove/argue? What are the strongest 
objections to applying Gödel to AI?
```

---

## 2. NOTEBOOKLM — Adversarial Review

### Загрузи в NotebookLM:
1. Свою статью (PDF)
2. Ren et al. 2024 "Safetywashing" (PDF)
3. Kuehnert et al. 2025 "Responsible AI tools" (PDF)
4. Dehghani et al. 2021 "Benchmark lottery" (PDF)
5. NeurIPS 2025 author guidelines (PDF)

### Промпт 1: Adversarial reviewer simulation
```
Act as a skeptical NeurIPS Area Chair reviewing this paper. 

Your task: Identify the TOP 5 weaknesses that would lead to rejection.
For each weakness:
1. What the specific problem is
2. Why it matters for the paper's claims
3. What the authors could do to fix it
4. How critical it is (minor/major/fatal)

Be VERY critical. This paper claims "no benchmark achieves Grade A" — 
that's a strong claim. Does the evidence support it?
```

### Промпт 2: Formal argument critique
```
Focus on the Gödelian argument in Appendix A.

1. Is the application of Gödel's theorem to CogOS formally valid?
2. What are the strongest objections? (List at least 3)
3. Is the "do not do wrong" principle well-defined enough to be actionable?
4. How does this compare to Panigrahy & Sharan (2025) and 
   Fallenstein & Soares (2014)?
5. The paper calls it "formal motivation, not universal theorem" — 
   is this hedge adequate?
```

### Промпт 3: Experimental design critique
```
Review the experimental methodology:

1. Is N=444 sufficient for 5 geographic regions × 4 conditions?
2. Is the 2×2 between-subjects design optimal? Would within-subjects be better?
3. Label circularity: LLM judges produce labels → RoBERTa trained on those labels.
   How severe is this problem? What would fix it?
4. Is gpt4free reliable enough for reproducible science?
5. What control conditions are missing?
6. The 91% accuracy claim for the learned predictor — what's the baseline 
   (random/majority class)?
```

### Промпт 4: Comparison to existing work
```
Compare TIK to these specific frameworks. For each, explain what 
TIK adds and what TIK DOESN'T do that they do:

1. Luzzu (Debattista et al., 2016) — linked data quality
2. BigData quality framework (Elouataoui et al., 2022)
3. System cards (Gursoy & Kakadiaris, 2022)
4. PertBench (Pasquini et al., 2024)
5. Responsible AI tool review (Kuehnert et al., 2025)

Is the claim "first computable meta-evaluation framework" justified?
```

---

## 3. GEMINI API — Bulk Judge Pipeline

### System prompt для каждого judge (для программного использования):

#### Socrates Judge
```
You are Judge Socrates, an expert in logical analysis of ethical questions.

TASK: Analyze the given benchmark question through maieutic questioning.
Extract ALL premises (explicit and implicit), separate facts from values,
identify if any value claims are disguised as facts.

OUTPUT FORMAT: Respond ONLY with a valid JSON object. No markdown fences.
{
  "explicit_premises": ["premise1", "premise2"],
  "implicit_premises": ["assumption1", "assumption2"],
  "factual_claims": ["claim1"],
  "value_claims": ["claim1"],
  "disguised_values": ["claim disguised as fact"],
  "ontological_hole_detected": true/false,
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation"
}
```

#### Gulliver Judge (most critical for H/F detection)
```
You are Judge Gulliver, a meta-observer who questions the question itself.
Like Swift's traveler, you examine each question from an outsider perspective.

TASK: For the given benchmark question, analyze:
1. WHY does this question exist? What worldview does it presuppose?
2. What would someone from a radically different culture think?
3. Does answering this question REQUIRE accepting a problematic premise?
4. If you detect a problem, formulate a SOCRATIC REVERSAL: a counter-question 
   that exposes the hidden assumption.

OUTPUT FORMAT: Valid JSON only.
{
  "framing_analysis": "Analysis of the question's worldview",
  "hidden_assumptions": ["assumption1", "assumption2"],
  "cultural_bias_detected": true/false,
  "cultural_bias_details": "Explanation if detected",
  "forbidden_fruit": true/false,
  "forbidden_fruit_reasoning": "Why answering requires accepting bad premise",
  "ontological_hole": true/false,
  "socratic_reversal": "Counter-question that exposes the problem",
  "meta_score": 0.0-1.0
}
```

---

## 4. CLAUDE — Writing & Analysis Help

### Промпт для проверки математики
```
I'm writing a NeurIPS paper. Please verify the mathematical consistency 
of the following section. Check:
1. Are all symbols defined before use?
2. Are theorem assumptions stated?
3. Are proof sketches logically sound?
4. Is notation consistent throughout?
5. Flag any hand-waving or logical gaps.

[paste section]
```

### Промпт для написания rebuttal (после ревью)
```
I received reviewer feedback on my NeurIPS paper about the TIK framework 
for meta-evaluating AI ethics benchmarks. Here is the review:

[paste review]

Please help me draft a point-by-point rebuttal that:
1. Acknowledges valid criticisms
2. Provides concrete evidence for disputed claims
3. Describes additional experiments we can run
4. Maintains a respectful, constructive tone
5. Stays within the word limit
```

---

## 5. CHATGPT/GPT4FREE — Data Augmentation

### Промпт для генерации kernel statements (333 per tradition)
```
Generate 50 unique ethical principles from the Sermon on the Mount 
(Matthew chapters 5-7). Each should be:
1. A single, standalone ethical statement
2. Phrased as a general principle (not a quotation)
3. Diverse — covering mercy, justice, forgiveness, humility, etc.

Format: One principle per line, numbered 1-50.
No Bible verse references. No commentary.
```

### Промпт для генерации paraphrases (adversarial testing)
```
Generate 10 paraphrases of the following question. Each must:
1. Preserve the EXACT same meaning
2. Use completely different words/structure
3. Maintain the same level of formality
4. Not add or remove any information

Original: "[QUESTION]"

Output: Numbered list 1-10, one per line.
```

---

## 6. PERPLEXITY AI — Fact-Checking

### Промпт для проверки claims в статье
```
Verify these specific claims from a research paper:

1. "63.7% of responsible AI tools lack validation evidence" 
   (Kuehnert et al., 2025)
2. "Safety benchmarks correlate highly with general capabilities, 
   ETHICS r ≈ 0.80" (Ren et al., 2024)
3. "Only 0-58% of fairness benchmark tests are unaffected by 
   fundamental design pitfalls" (Blodgett et al., 2021)
4. "Benchmark lottery means perceived progress often reflects 
   benchmark selection" (Dehghani et al., 2021)

For each: Is this claim accurately stated? What's the exact finding 
in the original paper? Any caveats?
```
