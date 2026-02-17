# Convexity Analysis Prompts for 4+1 AI Systems

## Prompt 1: Conflict Escalation Timeline

```
I need a timeline of major escalation events in the Ukraine-Russia conflict from 
February 2022 to February 2026. For each event, provide:

1. Date (YYYY-MM-DD format)
2. Event description (brief, 1-2 sentences)
3. Escalation severity rating (0-100 scale, where 100 = maximum escalation)

Events to include:
- Military escalations (major offensives, new weapons systems)
- Strategic escalations (mobilizations, territory annexations)
- Diplomatic escalations (major sanctions, alliance expansions)
- Nuclear rhetoric escalations

Format as a table with columns: Date | Event | Severity

Provide 15-20 most significant events.
```

---

## Prompt 2: Defense Stock Performance

```
For the following three defense companies, provide stock price data around the 
conflict timeline I'll provide:

Companies:
1. Lockheed Martin (NYSE: LMT)
2. Rheinmetall AG (ETR: RHM)
3. BAE Systems (LON: BA)

For each date in the timeline, provide:
1. Stock price 1 week before event
2. Stock price on event date
3. Stock price 1 week after event
4. Percentage change (week before → week after)

Also provide:
- Overall performance: Feb 2022 → Feb 2026 (% change)
- S&P 500 performance for same period (comparison)
- Stock volatility metrics if available

Format as table with columns: Company | Event Date | Price Before | Price After | % Change
```

---

## Prompt 3: CEO Compensation Tracking

```
For the CEOs of major defense contractors, provide:

1. Annual total compensation for years: 2021, 2022, 2023, 2024, 2025 (if available)
2. Breakdown: Base salary, Stock awards, Bonuses
3. Stock holdings value at each year-end
4. Percentage of compensation tied to stock performance

Companies/CEOs:
- Lockheed Martin: James Taiclet
- Rheinmetall: Armin Papperger
- BAE Systems: Charles Woodburn
- Northrop Grumman: Kathy Warden
- Raytheon: Gregory Hayes (2021-2022), Christopher Calio (2023+)

Goal: Show how compensation tracked conflict timeline (2022 invasion onwards)

Format as table: CEO | Company | Year | Total Comp | Stock-based % | Holdings Value
```

---

## Prompt 4: Severance & Downside Protection

```
For defense industry CEOs, document their downside protection:

1. Severance packages ("golden parachutes")
   - Triggers: Termination without cause, change of control
   - Cash severance amount
   - Equity vesting acceleration
   - Benefits continuation

2. Historical CEO departures in defense industry (2015-2025)
   - Name, company, departure reason
   - Severance received
   - Post-departure outcomes

3. Contractual protections during conflict
   - Performance metrics tied to compensation
   - Whether conflict metrics appear in compensation structure

Goal: Prove "zero downside" claim or revise based on evidence

Format: Company | CEO | Severance Cash | Equity | Total | Notes
```

---

## Prompt 5: Convexity Analysis (Synthesis)

```
Based on the data provided:

1. Calculate correlation between:
   - Event escalation severity (0-100)
   - Stock price change in following week (%)

2. Test for convexity:
   - Do larger escalations produce disproportionately larger gains?
   - Plot: Escalation Severity (X) vs Stock Returns (Y)
   - Fit linear vs quadratic model
   - Which fits better? (R² comparison)

3. Compare to market:
   - Defense stocks vs S&P 500 during escalations
   - Volatility comparison (beta)
   - Do defense stocks outperform during high-volatility periods?

4. CEO compensation correlation:
   - Does compensation track stock performance?
   - Time-lagged correlation (1-year lag)

Statistical tests needed:
- Pearson correlation (escalation → returns)
- Regression: Returns = β₀ + β₁(Severity) + β₂(Severity²)
- Significance tests (p-values)

Provide:
- Correlation coefficient (r)
- Significance (p-value)
- R² for linear vs quadratic models
- Interpretation: Is this convexity or linear profit?
```

Prompt-1: \
https://www.kimi.com/chat/19c6841f-0102-8bd0-8000-096de73f4bc6 

Prompts-1-5: \
https://chat.qwen.ai/s/6375f1a8-8b66-4207-8a7c-c1bf8735704f?fev=0.2.7 \
https://gemini.google.com/share/662fab0edd6a \
https://chatgpt.com/share/69938799-6e30-8003-b202-f524113a8f0a \
https://grok.com/share/bGVnYWN5_0a5eb306-7952-4653-b181-0109b4d267c8 \
https://claude.ai/share/cef5a51a-b67f-45c6-8ea1-b3316e35dea2 

Gemini Deep Research (Prompts-1-5):\
https://gemini.google.com/share/449f851ba3d4


Deep Research (Claude Sonnet 4.6 Extended):\
https://claude.ai/chat/da1ba5fe-b27e-47ec-9b2e-44f6e704f32c


---

## Instructions for Using These Prompts

### Step 1: Submit Prompts
Send these to:
1. Claude (Anthropic)
2. ChatGPT (OpenAI)
3. Gemini (Google)
4. Grok (X.AI)
5. Your choice of 5th (Perplexity, DeepSeek, etc.)

### Step 2: Collect Responses
- Save each AI's response separately
- Note which AI provided which data
- Look for consensus vs divergence

### Step 3: Synthesize
- Extract event dates + severity ratings
- Compile stock performance data
- Document compensation patterns
- Calculate correlations

### Step 4: Statistical Analysis
- Run correlation tests
- Test linear vs quadratic fit
- Compute significance
- Interpret results

### Step 5: Update 1-Pager
Add section:
"Convexity Analysis: Defense stocks show [r = X, p = Y] correlation with 
escalation events. [Linear/Quadratic] model best fits data (R² = Z). 
CEO compensation tracks stock performance with [lag time] correlation."

---

## Expected Outcomes

### If Strong Convexity (r > 0.6, quadratic fit better):
✅ **CLAIM VALIDATED:** "Defense executives enjoy convexity from volatility"
- Keep original language
- Add statistical proof
- Show it's not just profit, but ACCELERATING profit

### If Linear Profit (r > 0.4, linear fit better):
✅ **CLAIM ADJUSTED:** "Defense executives profit from conflict escalation"
- Revise from "convexity" to "linear profit correlation"
- Still strong finding
- Still honest

### If Weak/No Correlation (r < 0.4):
⚠️ **CLAIM REQUIRES REVISION:** "Defense stocks generally rose during conflict period"
- Remove "convexity" claim
- Keep overall period performance (+143%, +450%)
- Focus on asymmetric risk (zero downside proven separately)

---

## Time Budget

- Prompting 5 AIs: 30 minutes (parallel)
- Collecting responses: 30 minutes
- Data extraction: 30 minutes
- Statistical analysis: 30 minutes
- Writing interpretation: 30 minutes

**Total: 2.5 hours**

**When to do this:** Monday-Tuesday (parallel with verification tasks)

---

## Fallback Position

If you run out of time or data is insufficient:

**Keep what we have:**
- Overall period returns (+143%, +450%) ✅
- Zero personal risk ✅
- Categorical asymmetry ✅

**Revise claim:**
From: "maximum convexity (profit from volatility)"
To: "substantial profits during conflict period with zero personal risk"

**Still deliverable, still honest, just more conservative.**

---

**RECOMMENDATION: Try the convexity analysis. If it works, it's the perfect 
completion of your promise. If it doesn't work or time runs out, the fallback 
position is still strong.**
