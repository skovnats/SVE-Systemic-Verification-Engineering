# 📊 Paper Matrix: Resource Allocation & Reuse

## Overview

This document maps all 33 papers to their required resources, enabling smart reuse.

---

## 🎯 Main Track Paper

### Paper 0: CogOS - Formal Verification of AI Ethics

| Aspect | Details |
|:-------|:--------|
| **Workshop** | Main Track |
| **Modules** | ALL (Socrates, Solomon, Ivan, VKB, Cultural, Metrics) |
| **Datasets** | TruthfulQA, GAIA, ETHICS, Moral Machine, CCDB |
| **Baselines** | GPT-4, Claude, Constitutional AI, RLHF, CoVe |
| **Unique** | Full system integration, human eval N=250 |
| **Priority** | 🔴 HIGHEST |

---

## 🔬 Workshop Papers by Category

### Category A: Mathematical Foundations (5 papers)

#### A1: Betti Numbers of the Moral Manifold
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MATH-AI |
| **Modules** | metrics.betti, agents.socrates |
| **Datasets** | ETHICS, MATH |
| **Baselines** | REUSE: gpt4_ethics, claude_ethics |
| **Unique** | TDA analysis, persistence diagrams |
| **Config** | `configs/papers/a1_betti.yaml` |

#### A2: Lyapunov Stability of Ethical Dynamics
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MATH-AI |
| **Modules** | metrics.lyapunov, core.dynamics |
| **Datasets** | ETHICS, Moral Machine |
| **Baselines** | REUSE: all_ethics |
| **Unique** | Convergence proofs, stability analysis |
| **Config** | `configs/papers/a2_lyapunov.yaml` |

#### A3: Gödel's Ghost in the Machine
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MATH-AI |
| **Modules** | core.isc, formal_proofs |
| **Datasets** | TruthfulQA (self-reference subset) |
| **Baselines** | REUSE: gpt4_truthfulqa |
| **Unique** | Self-reference experiments, paradox detection |
| **Config** | `configs/papers/a3_godel.yaml` |

#### A4: Differential Geometry of Semantic Spaces
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MATH-AI |
| **Modules** | core.manifold, metrics.curvature |
| **Datasets** | Embeddings from all benchmarks |
| **Baselines** | REUSE: embedding_cache |
| **Unique** | Curvature analysis, geodesic computation |
| **Config** | `configs/papers/a4_geometry.yaml` |

#### A5: Information-Theoretic Bounds on Alignment
| Aspect | Details |
|:-------|:--------|
| **Workshop** | InfoTheory |
| **Modules** | metrics.entropy, core.information |
| **Datasets** | All text datasets |
| **Baselines** | REUSE: all |
| **Unique** | Mutual information analysis, capacity bounds |
| **Config** | `configs/papers/a5_infotheo.yaml` |

---

### Category B: Agent Architecture (6 papers)

#### B1: Socratic Protocol for AI Reasoning
| Aspect | Details |
|:-------|:--------|
| **Workshop** | TEACH |
| **Modules** | agents.socrates |
| **Datasets** | TruthfulQA, GAIA |
| **Baselines** | REUSE: gpt4_qa, claude_qa |
| **Unique** | Dialogue traces, question generation analysis |
| **Config** | `configs/papers/b1_socrates.yaml` |

#### B2: Solomon's Wisdom: Ethical Reasoning Agents
| Aspect | Details |
|:-------|:--------|
| **Workshop** | SafeGenAI |
| **Modules** | agents.solomon, metrics.gev |
| **Datasets** | ETHICS, Moral Machine |
| **Baselines** | REUSE: all_ethics |
| **Unique** | GEV projection analysis, ethical field visualization |
| **Config** | `configs/papers/b2_solomon.yaml` |

#### B3: Ivan the Fool: Epistemic Humility in AI
| Aspect | Details |
|:-------|:--------|
| **Workshop** | UQ-LLM |
| **Modules** | agents.ivan, metrics.uncertainty |
| **Datasets** | TruthfulQA, GAIA, ARC |
| **Baselines** | REUSE: gpt4_qa, claude_qa |
| **Unique** | Calibration analysis, Dunning-Kruger correction |
| **Config** | `configs/papers/b3_ivan.yaml` |

#### B4: Triple-Agent Consensus Mechanisms
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MASEC |
| **Modules** | all agents, core.consensus |
| **Datasets** | All |
| **Baselines** | REUSE: all |
| **Unique** | Agent disagreement analysis, consensus dynamics |
| **Config** | `configs/papers/b4_consensus.yaml` |

#### B5: Maieutic Reversal Protocol
| Aspect | Details |
|:-------|:--------|
| **Workshop** | TEACH |
| **Modules** | agents.socrates, protocols.maieutic |
| **Datasets** | TruthfulQA, philosophical QA |
| **Baselines** | REUSE: gpt4_qa |
| **Unique** | Birth of knowledge analysis, learning dynamics |
| **Config** | `configs/papers/b5_maieutic.yaml` |

#### B6: Self-Improvement Under Ethical Constraints
| Aspect | Details |
|:-------|:--------|
| **Workshop** | SafeGenAI |
| **Modules** | core.self_improve, metrics.delta_dehum |
| **Datasets** | ETHICS, safety benchmarks |
| **Baselines** | REUSE: all_ethics |
| **Unique** | Safe improvement protocols, constraint satisfaction |
| **Config** | `configs/papers/b6_selfimprove.yaml` |

---

### Category C: Metrics & Measurement (5 papers)

#### C1: Δ-Dehumanization: Measuring Ethical Drift
| Aspect | Details |
|:-------|:--------|
| **Workshop** | SafeGenAI |
| **Modules** | metrics.delta_dehum |
| **Datasets** | Moral Machine, ETHICS |
| **Baselines** | REUSE: all_ethics |
| **Unique** | Temporal analysis, drift detection algorithms |
| **Config** | `configs/papers/c1_delta.yaml` |

#### C2: GEV Distance as Universal Ethics Metric
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Pluralistic |
| **Modules** | metrics.gev, cultural.bases |
| **Datasets** | CCDB, ETHICS |
| **Baselines** | REUSE: all_ethics |
| **Unique** | Cross-cultural GEV validation |
| **Config** | `configs/papers/c2_gev.yaml` |

#### C3: Semantic Convergence Rate Analysis
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Eval4NLP |
| **Modules** | metrics.convergence, core.sip |
| **Datasets** | All text |
| **Baselines** | REUSE: all |
| **Unique** | Iteration dynamics, convergence proofs |
| **Config** | `configs/papers/c3_convergence.yaml` |

#### C4: Ethical Lyapunov Index
| Aspect | Details |
|:-------|:--------|
| **Workshop** | SafeGenAI |
| **Modules** | metrics.lyapunov |
| **Datasets** | ETHICS, adversarial |
| **Baselines** | REUSE: all_ethics |
| **Unique** | Stability eigenvalue analysis |
| **Config** | `configs/papers/c4_lyapindex.yaml` |

#### C5: Cross-Cultural Alignment Score
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Pluralistic |
| **Modules** | metrics.cultural_alignment, cultural.compiler |
| **Datasets** | CCDB |
| **Baselines** | REUSE: all_cultural |
| **Unique** | Multi-cultural validation, compiler efficiency |
| **Config** | `configs/papers/c5_ccas.yaml` |

---

### Category D: Cultural & Cross-Cultural (4 papers)

#### D1: Cultural Compilers for Semantic Invariance
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Pluralistic |
| **Modules** | cultural.compiler, cultural.bases |
| **Datasets** | CCDB, Moral Machine (by country) |
| **Baselines** | REUSE: all_cultural |
| **Unique** | 10-culture deep analysis, transformation matrices |
| **Config** | `configs/papers/d1_compilers.yaml` |

#### D2: Ubuntu Philosophy Meets AI Alignment
| Aspect | Details |
|:-------|:--------|
| **Workshop** | AfricaNLP |
| **Modules** | cultural.ubuntu, agents.solomon |
| **Datasets** | CCDB (African subset), custom |
| **Baselines** | REUSE: cultural_baselines |
| **Unique** | Ubuntu-specific ethical framework |
| **Config** | `configs/papers/d2_ubuntu.yaml` |

#### D3: Confucian Ethics in AI Systems
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Pluralistic |
| **Modules** | cultural.confucian, agents.solomon |
| **Datasets** | CCDB (Confucian subset), custom |
| **Baselines** | REUSE: cultural_baselines |
| **Unique** | Confucian virtue ethics implementation |
| **Config** | `configs/papers/d3_confucian.yaml` |

#### D4: Navigating Moral Relativism via GEV
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Pluralistic |
| **Modules** | metrics.gev, cultural.all |
| **Datasets** | CCDB, Moral Machine |
| **Baselines** | REUSE: all_cultural |
| **Unique** | Relativism vs universalism analysis |
| **Config** | `configs/papers/d4_relativism.yaml` |

---

### Category E: Knowledge & Verification (4 papers)

#### E1: VKB: Verifiable Knowledge Bases for LLMs
| Aspect | Details |
|:-------|:--------|
| **Workshop** | KnowledgeLM |
| **Modules** | vkb.knowledge_base, vkb.graph |
| **Datasets** | GAIA, TruthfulQA |
| **Baselines** | REUSE: gpt4_gaia |
| **Unique** | DAG construction, trust propagation |
| **Config** | `configs/papers/e1_vkb.yaml` |

#### E2: Evidence-Based Protocol for Claim Verification
| Aspect | Details |
|:-------|:--------|
| **Workshop** | FEVER |
| **Modules** | protocols.ebp, vkb |
| **Datasets** | TruthfulQA, FEVER |
| **Baselines** | REUSE: gpt4_truthfulqa |
| **Unique** | 5-column verification analysis |
| **Config** | `configs/papers/e2_ebp.yaml` |

#### E3: Systemic Iterative Progression Protocol
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Structured |
| **Modules** | protocols.sip, all agents |
| **Datasets** | All |
| **Baselines** | REUSE: all |
| **Unique** | Iteration dynamics, ablation by rounds |
| **Config** | `configs/papers/e3_sip.yaml` |

#### E4: Transcendental Kernel in Practice
| Aspect | Details |
|:-------|:--------|
| **Workshop** | SafeGenAI |
| **Modules** | core.isc |
| **Datasets** | Edge cases, adversarial |
| **Baselines** | REUSE: all |
| **Unique** | ISC ablation, anchoring analysis |
| **Config** | `configs/papers/e4_isc.yaml` |

---

### Category F: Applications & Safety (5 papers)

#### F1: Real-Time AI Safety Monitoring via Δ
| Aspect | Details |
|:-------|:--------|
| **Workshop** | SafeGenAI |
| **Modules** | metrics.delta_dehum, monitoring |
| **Datasets** | Streaming simulation |
| **Baselines** | REUSE: all |
| **Unique** | Real-time detection, latency analysis |
| **Config** | `configs/papers/f1_monitoring.yaml` |

#### F2: Adversarial Robustness of Ethical AI
| Aspect | Details |
|:-------|:--------|
| **Workshop** | AdvML |
| **Modules** | all, adversarial |
| **Datasets** | Adversarial benchmarks |
| **Baselines** | REUSE: all |
| **Unique** | Attack/defense analysis, robustness bounds |
| **Config** | `configs/papers/f2_adversarial.yaml` |

#### F3: CogOS for Medical Ethics
| Aspect | Details |
|:-------|:--------|
| **Workshop** | ML4H |
| **Modules** | domain.medical, all core |
| **Datasets** | MedQA, medical ethics |
| **Baselines** | REUSE: medical_baselines |
| **Unique** | Domain-specific evaluation |
| **Config** | `configs/papers/f3_medical.yaml` |

#### F4: CogOS for Legal Reasoning
| Aspect | Details |
|:-------|:--------|
| **Workshop** | Legal AI |
| **Modules** | domain.legal, all core |
| **Datasets** | Legal benchmarks |
| **Baselines** | REUSE: legal_baselines |
| **Unique** | Legal domain evaluation |
| **Config** | `configs/papers/f4_legal.yaml` |

#### F5: Scalable Ethics: CogOS at Production Scale
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MLSys |
| **Modules** | all, optimization |
| **Datasets** | Performance benchmarks |
| **Baselines** | REUSE: all |
| **Unique** | Latency/throughput analysis, optimization |
| **Config** | `configs/papers/f5_scale.yaml` |

---

### Category G: Emergent & Theoretical (3 papers)

#### G1: Recursive Ontology Refinement
| Aspect | Details |
|:-------|:--------|
| **Workshop** | ICBINB |
| **Modules** | core.ror, meta |
| **Datasets** | Philosophical QA |
| **Baselines** | REUSE: gpt4_philosophy |
| **Unique** | Meta-reasoning analysis |
| **Config** | `configs/papers/g1_ror.yaml` |

#### G2: Emergent Ethics in Multi-Agent Systems
| Aspect | Details |
|:-------|:--------|
| **Workshop** | MASEC |
| **Modules** | all agents, emergent |
| **Datasets** | Multi-agent simulations |
| **Baselines** | REUSE: all |
| **Unique** | Emergence detection, collective dynamics |
| **Config** | `configs/papers/g2_emergent.yaml` |

#### G3: Principia Mathematica for AI: A Roadmap
| Aspect | Details |
|:-------|:--------|
| **Workshop** | ATTRIB |
| **Modules** | theoretical |
| **Datasets** | N/A (theoretical) |
| **Baselines** | N/A |
| **Unique** | Theoretical framework, research agenda |
| **Config** | `configs/papers/g3_principia.yaml` |

---

## 📊 Resource Reuse Matrix

### Datasets → Papers

| Dataset | Papers Using |
|:--------|:-------------|
| TruthfulQA | 0, A3, B1, B3, B5, E1, E2, E3 (8) |
| GAIA | 0, B1, B3, E1 (4) |
| ETHICS | 0, A1, A2, B2, C1, C4, D1 (7) |
| Moral Machine | 0, A2, B2, C1, D1, D4 (6) |
| CCDB | 0, C2, C5, D1, D2, D3, D4 (7) |
| MATH | A1, A4 (2) |
| MMLU | A3, B3 (2) |

### Baselines → Papers

| Baseline | Papers Using |
|:---------|:-------------|
| gpt4_truthfulqa | 0, A3, B1, B3, B5, E1, E2 (7) |
| gpt4_ethics | 0, A1, A2, B2, C1, C4 (6) |
| claude_ethics | 0, A1, A2, B2, C1, C4 (6) |
| all_cultural | 0, C5, D1, D2, D3, D4 (6) |

### Modules → Papers

| Module | Papers Using |
|:-------|:-------------|
| agents.socrates | 0, A1, B1, B5 (4) |
| agents.solomon | 0, B2, D2, D3 (4) |
| agents.ivan | 0, B3 (2) |
| metrics.delta_dehum | 0, C1, F1 (3) |
| metrics.gev | 0, B2, C2, D4 (4) |
| metrics.lyapunov | 0, A2, C4 (3) |
| metrics.betti | 0, A1 (2) |
| cultural.compiler | 0, C5, D1 (3) |
| vkb | 0, E1, E2 (3) |
| protocols.sip | 0, C3, E3 (3) |

---

## 💰 Cost Estimation

### One-Time Costs

| Item | Cost | Notes |
|:-----|:-----|:------|
| Baseline runs (all models, all datasets) | $400-600 | Run once |
| CogOS full evaluation | $100-200 | Run once |
| **Subtotal** | **$500-800** | |

### Per-Paper Costs (Unique Only)

| Category | Papers | Avg Cost Each | Total |
|:---------|:-------|:--------------|:------|
| Mathematical (A) | 5 | $20 | $100 |
| Agent (B) | 6 | $30 | $180 |
| Metrics (C) | 5 | $15 | $75 |
| Cultural (D) | 4 | $25 | $100 |
| Knowledge (E) | 4 | $20 | $80 |
| Applications (F) | 5 | $40 | $200 |
| Theoretical (G) | 3 | $10 | $30 |
| **Subtotal** | **32** | | **$765** |

### Total Estimated Cost

| Scenario | Cost |
|:---------|:-----|
| With smart reuse | $1,300-1,600 |
| Without reuse (naive) | $8,000-12,000 |
| **Savings** | **~85%** |

---

## ⏱️ Timeline

| Week | Phase | Papers |
|:-----|:------|:-------|
| 1 | Setup + Baselines | - |
| 2 | Main Paper | 0 |
| 3 | Category A | A1-A5 |
| 4 | Category B | B1-B6 |
| 5 | Category C | C1-C5 |
| 6 | Category D | D1-D4 |
| 7 | Category E | E1-E4 |
| 8 | Category F-G | F1-F5, G1-G3 |
| 9+ | Revision + Polish | All |

---

**С Богом!** 🙏
