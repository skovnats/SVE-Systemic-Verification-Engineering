# Visual Specification: SITG Tier Matrix
## For Taleb 1-Pager

---

## Option A: Tier Matrix (RECOMMENDED - Most Honest)

### Layout
```
                    PERSONAL RISK EXPOSURE
                    Low         Medium        High
         ┌─────────────────────────────────────────┐
         │                                         │
    High │  TIER 3          TIER 2        TIER 1  │
         │  Western         Putin         Zelensky│
D   │  Leaders         Merz                    │
E   │  von der Leyen   Netanyahu              │
C        │  Macron                                 │
I        │  Scholz                                 │
S        │  Merkel                                 │
I   ├─────────────────────────────────────────────┤
O        │                                         │
N   Med  │                           (empty)      │
         │                                         │
M   │                                         │
A        ├─────────────────────────────────────────┤
K        │                                         │
I   Low  │  TIER 4                                │
N        │  Defense CEOs                          │
G        │  Taiclet                               │
         │  Woodburn                               │
P        │  *Papperger                            │
O        │  (assassination                        │
W        │   target)                              │
E        │                                         │
R        └─────────────────────────────────────────┘
```

### Color Coding
- **TIER 1 (Green):** Aligned - Authority = Risk
- **TIER 2 (Yellow):** Mixed - Some alignment
- **TIER 3 (Orange):** Misaligned - High insulation
- **TIER 4 (Red):** Inverted - Profit from conflict

### Annotations
- Arrow showing "expected" diagonal (aligned incentives)
- Shaded region showing "actual concentration" (bottom-right + top-left)
- Callout: "Zelensky: Only case in aligned quadrant"
- Callout: "Defense CEOs: 100% in inverted quadrant"
- Note: "*Papperger: Exception that proves rule"

---

## Option B: Asymmetry Quadrant (K2-Style)

### Layout
```
    Personal Risk
        ↑
        │
   High │     ALIGNED          RARE
        │   (Zelensky)      (Commanders)
        │       ●
        │
        │
───────┼──────────────────────────────→ Decision
   0   │                              Power
        │
        │  POWERLESS        INVERTED
   Low  │  (Civilians)    (Western Leaders,
        │                  Defense CEOs)
        │                    ●●●●●●●
```

### Data Points
- Size of bubble = Responsibility Radius
- Color = Category (Political/Military/Industry)
- X-axis: 0-100 Decision-Making Power
- Y-axis: 0-100 Personal Risk Exposure

**Problem:** Requires numerical assignments that look precise but aren't measured

---

## Option C: Feedback Loop Comparison (RECOMMENDED Alternative)

### Simple Table Visual
```
┌──────────────────┬──────────────┬────────────────┬────────────┐
│ Decision-Maker   │ Consequence  │ Feedback       │ Alignment  │
│                  │ Delay        │ Mechanism      │            │
├──────────────────┼──────────────┼────────────────┼────────────┤
│ Zelensky         │ Hours        │ Survival       │ ■■■■■      │
│ Field Commander  │ Days         │ Battlefield    │ ■■■■       │
│ Western Leader   │ Years        │ Electoral      │ ■          │
│ Defense CEO      │ Negative*    │ Market reward  │ (inverted) │
└──────────────────┴──────────────┴────────────────┴────────────┘

*Negative = Rewarded BEFORE consequences manifest
```

---

## Implementation Guidance

### If Using Tier Matrix (Option A):
**Tool:** Draw.io, PowerPoint, or hand-drawn + scan  
**Time:** 2 hours  
**Pros:** 
- Honest about qualitative nature
- Clear visual pattern
- No false precision
**Cons:**
- Less "scientific" looking
- May seem subjective

### If Using Quadrant Plot (Option B):
**Tool:** Python (matplotlib), R (ggplot2), or Excel  
**Time:** 3 hours (need to assign numbers)  
**Pros:**
- Professional appearance
- Fits academic norms
**Cons:**
- Implies precision you don't have
- Requires numerical assignments
- Could be challenged on methodology

### If Using Feedback Table (Option C):
**Tool:** Markdown table → PDF, or manual design  
**Time:** 1 hour  
**Pros:**
- Very simple
- Focuses on TIME dimension (Taleb likes this)
- No implied precision
**Cons:**
- Less visual impact
- Doesn't show full pattern

---

## RECOMMENDATION

**Use Option A (Tier Matrix) + Option C (Feedback Table)**

**Page Layout:**
```
┌─────────────────────────────────────┐
│ Title: Inverted Symmetry            │
│                                     │
│ [Tier Matrix - 60% of page]        │
│                                     │
│ Key Findings (3 bullets)            │
│                                     │
│ [Feedback Table - 25% of page]      │
│                                     │
│ Implication (2 sentences)           │
│ Methodology note (1 sentence)       │
└─────────────────────────────────────┘
```

**Why:** 
1. Tier matrix shows PATTERN (main insight)
2. Feedback table shows MECHANISM (why pattern matters)
3. Neither implies false precision
4. Both are intellectually honest
5. Taleb will appreciate temporal dimension (feedback delay)

---

## Data Sources to Cite on Visual

**For Each Figure, Note:**
- ✅ Zelensky stayed in Kyiv: NYT, BBC, Reuters (Feb 2022)
- ✅ CEO compensation: SEC DEF 14A filings (public record)
- ✅ Stock performance: Yahoo Finance, Bloomberg
- ✅ Assassination attempts: Reuters, CNN, Die Zeit
- ✅ Family data: Wikipedia, biographical sources
- ⚠️ Risk assessments: Multi-evaluator framework (5 AI systems + human synthesis)

**Citation Format:**
"Sources: SEC filings (compensation), Reuters/NYT (security incidents), Wikipedia (biographical), Multi-AI framework (comparative assessments). Full methodology: [GitHub link]"

---

## Color Palette (Accessible)

**For Tier Matrix:**
- TIER 1 (Aligned): #2ECC71 (green)
- TIER 2 (Mixed): #F39C12 (orange)
- TIER 3 (Misaligned): #E74C3C (red)
- TIER 4 (Inverted): #8B0000 (dark red)
- Background: #FFFFFF (white)
- Grid: #BDC3C7 (light gray)

**Test:** Print in grayscale - should still be distinguishable

---

## File Format

**Deliver as:**
- PDF (preferred - Taleb can't argue with layout)
- PNG (backup - high resolution, 300 DPI)

**NOT:**
- Word/Excel (editable = implies uncertainty)
- PowerPoint (too many slides)

---

## Quality Checklist for Visual

- [ ] Is pattern immediately visible? (3-second test)
- [ ] Are axes labeled clearly?
- [ ] Are data sources cited?
- [ ] Does it avoid false precision?
- [ ] Would it survive skeptical examination?
- [ ] Can it be understood without reading the text?
- [ ] Is Zelensky anomaly highlighted?
- [ ] Is defense CEO cluster visible?

---

## Anti-Bullshit Check

**Ask Yourself:**
1. "Can I defend every placement on this chart?" → Must be YES
2. "Does this visual imply I measured something I didn't?" → Must be NO
3. "Would I show this in a hostile academic seminar?" → Must be YES
4. "Is the pattern real or am I p-hacking visually?" → Must be real

**If any answer is wrong: Revise the visual**

---

## Timeline

**Sunday (Today):** Decide which visual (A or C or both)  
**Monday:** Create draft visual  
**Tuesday:** Test with critical friend  
**Wednesday:** Revise based on feedback  
**Thursday:** Final version  
**Friday:** Integrate into 1-pager PDF  
**Saturday:** Ship to Taleb

---

**Remember:** A simple, honest visual is better than a complex, impressive lie.
