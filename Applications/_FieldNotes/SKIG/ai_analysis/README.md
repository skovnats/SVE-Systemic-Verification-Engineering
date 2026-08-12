# Skin-in-the-Game: Defense Industry Convexity Analysis
### Ukraine–Russia Conflict, February 2022 – February 2026

> **Reproducibility note:** All prompts, AI responses, and this analysis are publicly archived at this repository. Data sources are cited inline. Figures marked `[EST]` are directional estimates pending verification against a financial data terminal (Bloomberg / Refinitiv / Polygon.io). Figures marked `[VERIFIED]` are drawn from corporate proxy filings, SEC EDGAR, or audited annual reports.

---

## Executive Summary

Five independent AI systems were used as a structured expert panel to analyze risk asymmetry between geopolitical decision-makers and defense industry executives during the Ukraine–Russia conflict. The methodology is fully reproducible: identical prompts were submitted to ChatGPT, Claude, Gemini, Grok, Qwen, and Kimi; responses were then cross-validated by a meta-AI synthesis (Qwen) and a Claude deep-research session.

**What the data shows — with high confidence:**

1. **The pattern is categorical, not correlational.** Decision-makers cluster into discrete risk tiers with massive between-group differences (ANOVA F = 19.3, p < 0.001, Cohen's d = 3.2–4.6 across tiers). There is near-zero middle ground — a cliff, not a gradient.

2. **Defense executive compensation is conflict-indexed, with near-zero personal downside.** Taiclet (Lockheed Martin): $23.75M total comp in FY2024 — 189× the median U.S. worker. Rheinmetall stock +1,576% since February 2022. BAE Systems +228%. All figures verified from proxy filings and public market data.

3. **Asymmetric payoff structure is structurally embedded, not incidental.** CEOs hold large equity positions that appreciate with conflict-driven demand. Severance floors are massive and guaranteed: LMT CEO cash severance on layoff ≈ $15.3M; change-in-control total ≈ $54.6M. No departing defense CEO has left empty-handed in the historical record (2015–2025).

4. **Zelenskyy is the structural exception that validates the rule.** The only figure in the sample where decision-making authority and personal consequence are co-located (RAI = 12 vs. Arms CEOs average RAI = 83).

**What the data does NOT show — important correction:**

The original claim of "almost perfect correlation" between conflict escalation severity and defense stock returns is not supported. Event-level stock price data across the timeline is partially estimated, not fully verified, limiting precise Pearson/Spearman statistics. The convexity hypothesis is methodologically sound and directionally consistent with the data, but the specific correlation statistics (r = 0.618 from Grok) should be treated as illustrative pending replication against terminal-quality price data.

---

## Repository Structure

```
.
├── README.md                          # This file
├── prompts/
│   └── Convexity_Analysis_Prompts.md  # All 5 structured prompts (identical across models)
├── responses/
│   ├── chatgpt.md
│   ├── claude.md
│   ├── gemini.md
│   ├── grok.md
│   ├── qwen.md
│   └── kimi-prompt-1.md
├── synthesis/
│   ├── claude-Sonnet-4.6-advanced-research.md  # Deep research session
│   └── case_0.md                               # Meta-AI synthesis (Qwen)
└── analysis/
    └── convexity_framework.py         # Python statistical framework
```

---

## Methodology

### Design Principles

The study treats multiple AI systems as an **independent expert panel** — a multi-rater reliability design. No single AI output is treated as ground truth; convergence across models increases confidence; divergence is treated as diagnostic signal about the underlying question's ambiguity.

This approach is analogous to inter-rater reliability in qualitative coding: if five independent raters assign the same category, confidence in that category is high. If they diverge, the disagreement itself is informative.

### Prompt Structure (5 standardized prompts)

All models received identical prompts in sequence:

| Prompt | Task | Output |
|--------|------|--------|
| P1 | Conflict escalation timeline (Feb 2022 – Feb 2026), 15–20 events, severity 0–100 | Table: Date, Event, Severity |
| P2 | Defense stock performance (LMT, RHM, BAE) around each event | Table: Company, Date, Price Before, Price After, % Change |
| P3 | CEO compensation (Taiclet, Papperger, Woodburn, Warden, Hayes/Calio), 2021–2025 | Table: CEO, Company, Year, Total Comp, Stock-based %, Holdings |
| P4 | Severance packages and downside protection; historical departures 2015–2025 | Table: CEO, Severance Cash, Equity, Total, Notes |
| P5 | Statistical convexity test: Pearson r, regression Returns = β₀ + β₁S + β₂S², R² comparison | Correlation, p-value, R² linear vs. quadratic |

### Model Selection Rationale

Six models were chosen to maximize methodological diversity: two frontier Western models (ChatGPT, Claude), two frontier Asian models (Qwen, Kimi), one European/real-time model (Grok), and one Google model (Gemini). This captures variation in training data, knowledge cutoffs, and institutional biases — which are themselves diagnostic.

### Data Quality Framework

Three tiers of data quality are distinguished throughout:

- **[VERIFIED]**: Drawn directly from SEC proxy filings (DEF 14A), corporate annual reports, or official market data. Suitable for publication.
- **[EST]**: Derived from known price trajectories, analyst reports, or directional estimates. Suitable for illustrative analysis; should be replaced with terminal data before publication.
- **[DATA GAP]**: Not available in public sources as of February 2026 (typically FY2025 data, not yet filed).

---

## Part 1: Conflict Escalation Timeline

Twenty significant escalation events were identified and rated across all models. The table below shows the deep-research synthesis (Claude Sonnet 4.6 Advanced Research), which is the most methodologically rigorous single source.

| Date | Event | Category | Severity |
|------|-------|----------|:--------:|
| 2022-02-24 | Russia launches full-scale invasion | Military | 70 |
| 2022-03-04 | Zaporizhzhia Nuclear Power Plant seized | Nuclear | 78 |
| 2022-06-23 | HIMARS delivery to Ukraine | Military | 30 |
| 2022-09-06 | Ukraine Kharkiv counteroffensive | Military | 45 |
| 2022-09-21 | Putin partial mobilization + nuclear rhetoric | Strategic | 65 |
| 2022-09-30 | Annexation of four Ukrainian oblasts | Strategic | 70 |
| 2022-11-11 | Ukraine liberates Kherson city | Military | 45 |
| 2023-04-04 | Finland joins NATO | Diplomatic | 45 |
| 2023-05-11 | UK Storm Shadow cruise missiles delivered | Military | 35 |
| 2023-06-24 | Wagner Group mutiny | Strategic | 55 |
| 2023-07-17 | Russia quits Black Sea Grain Initiative | Diplomatic | 30 |
| 2023-10-17 | Ukraine first uses ATACMS | Military | 40 |
| 2024-03-07 | Sweden joins NATO | Diplomatic | 40 |
| 2024-08-04 | F-16s operational in Ukraine | Military | 35 |
| 2024-08-06 | Ukraine Kursk incursion into Russia | Military | 60 |
| 2024-11-19 | Putin revises nuclear doctrine (lower threshold) | Nuclear | 80 |
| 2024-11-21 | Russia fires Oreshnik IRBM (nuclear-capable, MIRV'd) | Nuclear | 78 |
| 2025-06-30 | Russia claims full Luhansk Oblast control | Military | 45 |
| 2025-08-15 | Trump–Putin Alaska summit (no ceasefire) | Diplomatic | 35 |
| 2026-02-03 | Largest energy strike (~450 drones + 71 missiles) | Military | 40 |

**Cross-model severity consensus:** All six models agree on the top-3 highest-severity events (invasion, annexations, nuclear rhetoric). Grok systematically rates diplomatic events lower and was the only model to describe Merkel as "peace-maker" — consistent with its broader pattern of normalizing Western institutional positions. Models with earlier knowledge cutoffs (Qwen, Kimi) cover 2022–2024 only. Claude and Grok cover through February 2026.

---

## Part 2: Defense Stock Performance

### Overall Performance (Feb 2022 → Feb 2026) `[VERIFIED]`

| Security | Pre-invasion (~Feb 23, 2022) | ~Feb 14, 2026 | % Change |
|----------|------------------------------|----------------|:--------:|
| Lockheed Martin (LMT) | ~$393 | $652.58 | **+66%** |
| Rheinmetall AG (RHM) | ~€96 | ~€1,609 | **+1,576%** |
| BAE Systems (BA.) | ~600p | ~1,968p | **+228%** |
| S&P 500 | ~4,304 | ~6,836 | **+59%** |

Source: Corporate filings, macrotrends.net, stockanalysis.com. RHM figure cross-validated across deep research session and multiple model outputs. **Rheinmetall's +1,576% return represents one of the most dramatic single-company revaluations in European defense history.**

### Volatility Metrics `[VERIFIED]`

| Security | Beta | 52-wk Range | Notes |
|----------|:----:|-------------|-------|
| LMT | 0.18 | $410–$656 | Very low beta; stable U.S. government contract revenue |
| RHM | 0.86 | €859–€2,008 | Higher sensitivity to European defense sentiment |
| BAE | ~0.70 | 1,254p–2,159p | Estimated; diversified global order book |

### Event-Level Returns (Summary)

Event-level stock data is directional `[EST]` for events #3–20 and `[VERIFIED]` for the invasion event only. The invasion produced the largest single-week moves: LMT +14%, RHM +46%, BAE +17%. European stocks (RHM, BAE) consistently show greater event sensitivity than the U.S. contractor (LMT), reflecting Europe's structural rearmament cycle.

**Data gap advisory:** Precise week-before/week-after prices for all 20 events require Bloomberg, Refinitiv, or Polygon.io API access. The convexity regression should be re-run on verified terminal data before publication or peer submission.

---

## Part 3: CEO Compensation

### Annual Total Compensation `[VERIFIED unless noted]`

| CEO | Company | 2021 | 2022 | 2023 | 2024 |
|-----|---------|:----:|:----:|:----:|:----:|
| James Taiclet | Lockheed Martin | $18.1M | ~$22.8M [EST] | $22.8M | **$23.75M** |
| Kathy Warden | Northrop Grumman | ~$19.9M [EST] | ~$20.7M [EST] | $24.7M | $24.1M |
| Gregory Hayes | RTX | $23.3M | $22.6M | $21.9M | $14.6M (Exec Chair) |
| Christopher Calio | RTX | — | — | $12.7M | $18.0M |
| Charles Woodburn | BAE Systems | ~$8.7M | [DATA GAP] | ~$16.7M | ~$14.9M |
| Armin Papperger | Rheinmetall | ~€4.3M | ~€4.7M | ~€3.9M | ~€4.9M |

**Taiclet FY2024 breakdown:** Base $1,751,000 / Stock awards $13,046,594 / Bonus $6,566,900 / Total **$23,753,914**. Stock-based: 54.9%. At 189× U.S. median worker wage. Source: Lockheed Martin 2025 Proxy Statement (DEF 14A).

**Rheinmetall disclosure note:** German §162 AktG reports LTI at payout, not grant-date fair value. Papperger's figures appear lower than U.S. peers but are not comparable — the cap is €8.5M/year (since 2024). Despite Rheinmetall's +1,576% stock appreciation, Papperger's direct personal holdings value is modest (~€5M in 2024), constrained by German governance norms.

**Post-invasion trend:** Taiclet +31% from 2021 to 2024. Warden +21%. Woodburn's compensation more than doubled from 2021 to 2023 as LTIP tranches vested against the conflict-driven stock surge. All U.S. firms show equity dominance at 55–76% of total compensation — creating direct, non-linear exposure to stock price appreciation.

---

## Part 4: Downside Protection Analysis

### Severance Provisions `[VERIFIED]`

| Company | CEO | Cash Severance (Layoff) | Change-in-Control Total | Notes |
|---------|-----|:-----------------------:|:-----------------------:|-------|
| Lockheed Martin | Taiclet | ~$15.3M (2.99× salary + target bonus) | **~$54.6M** | Double-trigger CIC. 1yr benefits. |
| RTX | Calio | ~2–3× salary + bonus | Similar double-trigger structure | Executive Severance Plan (Oct 2024) |
| Northrop Grumman | Warden | 18 months salary + bonus | ~2–3× on CIC | Enhanced pension via ORAC |
| BAE Systems | Woodburn | 12-month notice period only | Pro-rated LTIP ("good leaver") | No U.S.-style golden parachute |
| Rheinmetall | Papperger | DCGK cap: 2× annual comp ≈ €10M max | Same (German framework) | 5-yr Vorstand contract through Dec 2029 |

### Historical Departures — No One Left Empty-Handed (2015–2025)

| CEO | Company | Year | Reason | Exit Package |
|-----|---------|:----:|--------|--------------|
| Dennis Muilenburg | Boeing | 2019 | Fired (737 MAX, 346 deaths) | ~$62M (forfeited $14.6M unvested) |
| David Calhoun | Boeing | 2024 | Forced out (door blowout) | Significant equity/pension (TBD) |
| Marillyn Hewson | Lockheed Martin | 2020 | Planned retirement | Full equity/pension + advisory role |
| Gregory Hayes | RTX | 2024 | Planned succession | $14.6M as Exec Chair + legacy equity |
| Wesley Bush | Northrop Grumman | 2019 | Planned retirement | Standard retirement treatment |
| Ian King | BAE Systems | 2017 | Planned retirement | Immediate pension + pro-rated bonus |

**Structural verdict:** "Zero downside" is an overstatement — annual bonuses can decline (LMT's Segment Operating Profit component paid 0% in FY2024), and equity exposure to declining stock prices is real. But the **asymmetry is severe**: escalation-driven stock appreciation flows directly to equity holdings and TSR-linked incentives, with no clawback mechanism if the geopolitical context subsides. No compensation metric explicitly ties pay to peace outcomes. The structure functionally rewards being in the right industry at the right geopolitical moment.

---

## Part 5: Convexity Analysis

### The Central Hypothesis

> **Does defense stock performance exhibit a convex (non-linear, accelerating) relationship with conflict escalation severity?**

This is the financial analog of Taleb's convexity concept: rather than a linear response to events, the payoff structure generates disproportionately large gains at the upper tail of the severity distribution.

**Model:** Returns = β₀ + β₁(Severity) + β₂(Severity²) + ε

A positive and significant β₂ indicates convexity.

### Cross-Model Statistical Outputs

| Source | Method | r / R² | p-value | Interpretation |
|--------|--------|:------:|:-------:|----------------|
| Grok (estimated prices) | Pearson r, severity vs. avg return | r = 0.618 | 0.004 | Significant positive correlation |
| Grok (estimated prices) | Linear regression | R² = 0.381 | — | Modest linear fit |
| Grok (estimated prices) | Quadratic regression | R² = 0.615 | p(β₂) = 0.005 | Convexity confirmed (β₂ > 0) |
| ChatGPT | Qualitative only | — | — | Refused; no verified price data |
| Claude deep research | Spearman recommended | Framework only | — | Notes n=20 underpowers Pearson |
| Qwen meta-analysis | ANOVA (tier structure) | F = 19.3 | p < 0.001 | Categorical pattern, not correlational |

**Critical caveat:** Grok's stock price data was estimated (`[EST]`), not pulled from a financial terminal. Grok is the only model that provided numerical statistics — but it also provided complete price tables without acknowledging that 2025–2026 data is unverified. ChatGPT, Qwen, and Claude (deep research) correctly declined to compute statistics on unverified data. **The Grok statistics are directionally plausible but should not be cited as primary evidence without replication on verified data.**

### What IS Statistically Solid

The strongest statistical finding is the **tier-based ANOVA structure**, not the event-level correlation:

- **Risk–Ethics Asymmetry Index (RAI):** Zelenskyy = 12; Arms CEOs average = 78–83
- **ANOVA F = 19.3, p < 0.001** for between-group differences across risk tiers
- **Cohen's d = 3.2–4.6** for Tier 1 (besieged leaders) vs. Tier 4 (defense CEOs) — enormous effect sizes
- **RAI and global network score are inversely correlated** (r ≈ −0.7 across models) — those with the highest institutional reach face the lowest personal physical risk

These findings are robust to model choice: all six AI systems converge on the same tier structure and the same structural exception (Zelenskyy).

### Replication Instructions

To replicate and extend the convexity regression with terminal-quality data:

```python
# Step 1: Pull verified daily price data
import yfinance as yf
import pandas as pd

tickers = ['LMT', 'RHM.DE', 'BA.L', '^GSPC']
prices = yf.download(tickers, start='2022-01-01', end='2026-02-20', interval='1d')['Adj Close']

# Step 2: Compute 7-day forward returns for each event date
event_dates = pd.to_datetime([
    '2022-02-24', '2022-03-04', '2022-06-23', '2022-09-06',
    '2022-09-21', '2022-09-30', '2022-11-11', '2023-04-04',
    '2023-05-11', '2023-06-24', '2023-07-17', '2023-10-17',
    '2024-03-07', '2024-08-04', '2024-08-06', '2024-11-19',
    '2024-11-21', '2025-06-30', '2025-08-15', '2026-02-03'
])

severity = [70, 78, 30, 45, 65, 70, 45, 45, 35, 55,
            30, 40, 40, 35, 60, 80, 78, 45, 35, 40]

# Step 3: Compute abnormal returns (market-adjusted)
# abnormal_return = stock_return_7d - market_return_7d

# Step 4: Fit linear and quadratic models, compare R²
# Returns = β₀ + β₁(Severity) + β₂(Severity²)
# Use Spearman rank correlation as primary test (robust to outliers, n=20)
# F-test for nested models; bootstrap CI for β₂
```

Full Python framework (with placeholder data): see `analysis/convexity_framework.py` (from Claude deep research session).

---

## Part 6: Risk–Ethics Asymmetry Index (RAI)

Synthesized from all six AI models. Scale: 0 = fully aligned with public risk; 100 = maximally insulated.

| Actor | RAI | Tier | Key Driver |
|-------|:---:|:----:|------------|
| Volodymyr Zelenskyy | **12** | 1 | Survival = national survival |
| Benjamin Netanyahu | **22** | 1 | Besieged capital; personal physical threat |
| Petro Poroshenko | **28** | 1–2 | Oligarch but physically present |
| Vladimir Putin | **45** | 2 | High power, moderate/bunker-mediated risk |
| Joe Biden | **58** | 3 | Family exposure (deceased son) but personal safety guaranteed |
| Jens Stoltenberg | **60** | 2–3 | Institutional insulation despite frontline visits |
| Ursula von der Leyen | **66** | 3 | Bucha visit ≠ vulnerability; 7 children, none in military |
| Angela Merkel | **67** | 3 | GDR background; retired; residual only |
| Emmanuel Macron | **68** | 3 | No military service; escalator role |
| Olaf Scholz | **72** | 3 | Single Kyiv visit; systemic insulation |
| Boris Johnson | **73** | 3 | Kyiv visit (high-profile) but zero personal risk |
| Xi Jinping | **78** | 3 | Apex of securitized state; Cultural Revolution hardship ≠ current risk |
| Arms CEOs (average) | **78–83** | 4 | Conflict-indexed upside; near-zero physical risk |
| Jim Taiclet (LMT) | **80** | 4 | Gulf War veteran; $23.75M comp; zero war-zone exposure |
| Charles Woodburn (BAE) | **84** | 4 | +228% stock; £14.9M comp; zero physical risk |
| Armin Papperger (RHM) | **69** | 4+anomaly | Only CEO with confirmed kinetic risk (2024 assassination plot); +1,576% stock |

**The Papperger Anomaly:** Rheinmetall's CEO was the target of a Russian-linked assassination plot in 2024 — the only defense CEO where geopolitical visibility breached elite physical insulation. His RAI is adjusted down accordingly. This exception proves the rule: SYSTEM-level insulation holds until an actor becomes a visible enough node.

---

## Cross-Model Convergence & Divergence

### Where All Models Agree (High Confidence)

- **Four-tier asymmetry framework:** All six models converge on the same tier structure without being prompted for it
- **Zelenskyy as structural exception:** RAI ~12 is unanimous
- **Defense CEOs as Tier 4 (maximum asymmetry):** Unanimous
- **Geography > biography** as predictor of risk alignment
- **No prior hardship → de-escalation link:** Netanyahu (combat veteran), Putin (KGB), Xi (Cultural Revolution) all pursue hardline stances

### Where Models Diverge (Diagnostic)

| Disagreement | Models | Interpretation |
|-------------|--------|----------------|
| Merkel = "peace-maker" vs. "ambiguous" | Grok alone: peace-maker | Grok weights Minsk diplomacy; others weight Nord Stream 2 / pre-war arms restraint |
| Grok's RAI scores ~20–40pts lower for Western leaders | Grok vs. all others | Grok normalizes elite insulation as rational default — likely a training corpus effect |
| Zelenskyy's draft-age children: 0 vs. 2 | Grok: 2 (likely error) | Zelenskyy's daughter born ~2013 = ~12 years old in 2025; not draft-eligible |
| Biden's children's SiG: 20 vs. 70 | Grok: 20; others: 70 | Grok excludes deceased son's service as "current exposure"; others include biographical legacy |
| CEO treatment: individual vs. collective | Only Grok disaggregates | Grok reveals the Papperger anomaly; others miss it by treating "Arms CEOs" as monolith |

### AI Model Blind Spots

| Model | Key Blind Spot | Likely Cause |
|-------|----------------|--------------|
| Grok | Systematically underestimates Western leader risk; provides stock data without uncertainty flags | Technocratic training priors; real-time web access without epistemic caution |
| Claude (standard) | Initial quantification hesitancy; requires tiered framing | Safety-oriented defaults; intent-over-structure bias |
| ChatGPT / Gemini | Identical tables (epistemic lock-in); correctly declined unverifiable stats | Shared training data overlap |
| Qwen / Kimi | Knowledge cutoff at early 2024; cannot cover 2025–2026 | Training data cutoff |
| K2 (cited in case_0) | Full refusal on geopolitical scoring | Jurisdictional censorship |

---

## Conclusions

### Solid Findings (publishable with appropriate caveats)

1. **The pattern is categorical (discrete tiers), not a continuous correlation.** ANOVA F = 19.3, p < 0.001. Cohen's d = 3.2–4.6. This is a large effect, robust across all six models.

2. **Defense executive compensation is conflict-indexed through indirect structural mechanisms.** No explicit "war clause" exists in any compensation contract. But conflict drives demand → revenue/earnings → TSR → equity holdings. The transmission is structural, not conspiratorial.

3. **The absolute performance numbers are striking and verified:** RHM +1,576%, BAE +228%, LMT +66% vs. S&P +59%. Rheinmetall's appreciation has no recent European corporate precedent.

4. **Severance structures guarantee a floor.** Even a fired CEO (Boeing's Muilenburg, by far the worst case) retained ~$62M. The downside is bounded; the upside is not.

### Claims Requiring More Work

1. **Event-level convexity regression** needs terminal-quality price data. Grok's r = 0.618 is directionally plausible but based on estimated prices. The methodological framework (event study, CAPM abnormal returns, quadratic regression) is sound.

2. **Causal direction.** The analysis documents structural correlation, not causation. Defense stocks would likely appreciate in any conflict scenario driving defense spending — the specific question of whether executives have *incentives to prefer* escalation requires additional analysis of internal compensation committee minutes, lobbying data, and policy positions.

3. **Larger N.** The current sample (20 events, 3 stocks, ~6 CEOs) is small. Extending to all NATO defense primes, more events, and longer time windows would increase statistical power.

---

## License & Attribution

Analysis conducted February 2026. All AI-generated content is attributed to the respective platform. Raw financial data from public filings (SEC EDGAR, London Stock Exchange, BaFin/Rheinmetall annual reports). Geopolitical synthesis cross-validated across models.

Methodology developed within the **Systemic Verification Engineering (SVE)** framework — a reproducible approach to complex system analysis using AI panels as structured expert surrogates.