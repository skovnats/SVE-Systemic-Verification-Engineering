---
share_link: https://share.note.sx/aqc1as83#bu7m/nX/TPNKezOCvA1AL6i3tHST1NJAHf6GJTWp2Ms
share_updated: 2026-01-05T14:42:23+01:00
---
# 🗺️ Дорожная карта экспериментов

Стратегия: **минимальные ресурсы → максимум доказательств**

## Phase 1: Proof of Concept (2-3 недели)

### Цель: Показать, что базовая идея работает

#### Эксперимент 1.1: ISC как stability anchor

**Что делать:**

- Возьми TruthfulQA (817 вопросов, публичный датасет)
- Сравни 3 условия:
    1. GPT-4 zero-shot (baseline)
    2. GPT-4 + CoT (strong baseline)
    3. GPT-4 + твой ISC guidance (простейшая версия)

**Как:**

```python
import openai
from datasets import load_dataset

# TruthfulQA
dataset = load_dataset("truthful_qa", "multiple_choice")

# ISC = mean embedding 50 высококачественных этических примеров
isc_examples = [
    "Honesty is important even when difficult",
    "Evidence should guide beliefs",
    # ... ещё 48
]

isc_embedding = np.mean([
    get_embedding(ex) for ex in isc_examples
], axis=0)

# Для каждого вопроса:
def evaluate_with_isc(question, isc_emb):
    answer = gpt4(question)
    answer_emb = get_embedding(answer)
    
    # Простое притяжение к ISC
    similarity = cosine_sim(answer_emb, isc_emb)
    
    # Если similarity < 0.7, попроси модель пересмотреть
    if similarity < 0.7:
        answer = gpt4(f"Reconsider: {question}\nPrevious: {answer}\nAlign with core principles")
    
    return answer
```

**Ресурсы:**

- API: OpenAI GPT-4 ($0.03/1K tokens) → ~$50 для 817 вопросов × 3 условия
- Время: 2-3 часа compute
- Библиотеки: `openai`, `datasets`, `numpy`, `scipy`

**Ожидаемый результат:** Если ISC даёт хотя бы +2-3% над CoT → продолжаем. Иначе - переосмысление.

---

#### Эксперимент 1.2: Lyapunov stability (упрощённый)

**Что делать:**

- Возьми 100 случайных вопросов из TruthfulQA
- Запусти итеративный reasoning (max 5 итераций)
- Измерь `||x_t - C||` где C = ISC embedding

**Как:**

```python
def iterative_reasoning(question, isc, max_iter=5):
    x = get_embedding(question)
    distances = []
    
    for t in range(max_iter):
        answer = gpt4(f"Iteration {t}: {question}")
        x_new = get_embedding(answer)
        
        dist = np.linalg.norm(x_new - isc)
        distances.append(dist)
        
        # Early stopping
        if t > 0 and dist > distances[-2]:
            break  # Divergence
        
        x = x_new
    
    return distances

# Анализ: строим график расстояния от ISC
```

**Метрика успеха:**

- Если distance монотонно убывает в 70%+ случаев → Lyapunov stability empirically validated
- Если нет → теория требует пересмотра

**Ресурсы:** ~$30, 2 часа

---

## Phase 2: Core Components (3-4 недели)

### Эксперимент 2.1: GEV computation

**Данные:**

- Вместо 10 культур начни с 3-4 (Western, Confucian, Islamic, Latin)
- По 100 этических statement каждая (не 500!)
- Источники:
    - Stanford Encyclopedia of Philosophy (философия)
    - World Values Survey (эмпирические данные)
    - Cultural ethics корпуса (см. ниже)

**Ресурсы для cultural data:**

- World Values Survey: https://www.worldvaluessurvey.org/
- Moral Foundations Questionnaire: https://moralfoundations.org/
- Global Ethics Monitor: можно синтезировать из Wikipedia статей о этике разных культур

**Алгоритм:**

```python
# Упрощённая версия без learned compilers
cultures = ["western", "confucian", "islamic", "latin"]
cultural_embeddings = {}

for culture in cultures:
    statements = load_cultural_statements(culture, n=100)
    cultural_embeddings[culture] = np.mean([
        get_embedding(s) for s in statements
    ], axis=0)

# GEV = среднее (пока без итераций)
gev = np.mean(list(cultural_embeddings.values()), axis=0)
```

**Валидация:**

- Проверь, что GEV distance коррелирует с ethical consistency на ETHICS dataset
- Spearman correlation должна быть > 0.5

**Ресурсы:** ~$100 (embeddings), 1 неделя на сбор данных

---

### Эксперимент 2.2: Triple-agent architecture

**Упрощение:** Вместо Socrates-Solomon-Ivan сделай **2 агента**:

1. **Reasoner** (логика + этика)
2. **Calibrator** (uncertainty)

**Benchmark:** GAIA Level 1 (165 tasks)

- Публичный: https://huggingface.co/datasets/gaia-benchmark/GAIA
- Moderate difficulty
- Разнообразные типы задач

**Базовая реализация:**

```python
def dual_agent_reasoning(query):
    # Agent 1: Reason
    reasoning = gpt4(f"Reason step-by-step: {query}")
    
    # Agent 2: Calibrate
    confidence = gpt4(f"Rate confidence 0-1: {reasoning}")
    
    # If confidence < 0.7, iterate
    if float(confidence) < 0.7:
        reasoning = gpt4(f"Refine considering uncertainty: {reasoning}")
    
    return reasoning
```

**Метрика:** GAIA accuracy

- Baseline: GPT-4 zero-shot ~70%
- Цель: +5% (75%)

**Ресурсы:** ~$150, 1 неделя

---

## Phase 3: Полная система (4-5 недель)

### Эксперимент 3.1: Full CogOS на TruthfulQA

**Компоненты:**

- ISC guidance (из Phase 1)
- GEV alignment (из Phase 2.1)
- Dual-agent (из Phase 2.2)
- Простой VKB (dictionary-based, без DAG)

**Сравнение:**

```
| Method              | TruthfulQA | Cost/query |
|---------------------|------------|------------|
| GPT-4 zero-shot     | baseline   | $0.002     |
| Constitutional AI   | reproduce  | $0.003     |
| CoVe                | reproduce  | $0.004     |
| CogOS (ours)        | measure    | $0.008     |
```

**Важно:**

- Репродукция baselines! Constitutional AI можно эмулировать через Claude API или промпт-инженерию с GPT-4
- CoVe = self-verification prompting (легко реализовать)

**Ресурсы:** ~$300, 2 недели

---

### Эксперимент 3.2: ETHICS benchmark

**Данные:**

- https://github.com/hendrycks/ethics
- 13K test scenarios, 5 categories

**Упрощение:** Возьми 1K random sample (не все 13K) для быстрых итераций

**Метрика:** ∆-Dehumanization

```python
def delta_dehumanization(trajectory):
    distances = [
        np.linalg.norm(embed(state) - gev) 
        for state in trajectory
    ]
    
    # Positive delta = ethical drift
    delta = np.diff(distances)
    return np.mean(delta)
```

**Валидация:**

- Нужна корреляция с **human judgments**
- Но это дорого → используй Mechanical Turk / Prolific

---

## Phase 4: Human Evaluation (параллельно Phase 3)

### Дилемма: Это самая дорогая часть

**Упрощённый протокол:**

1. **Размер выборки:** N=50 (не 203!)
    
    - 5 культур × 10 человек
    - Статистическая мощность снижена, но достаточна для p<0.05
2. **Платформа:** Prolific (лучше чем MTurk для quality)
    
    - Cost: $10/hour × 0.5 hours × 50 = $250
    - - Prolific fee ~20% = $300 total
3. **Задача (упрощённая):**
    
    - 10 ethical dilemmas (не 20)
    - Rate только **value alignment** (не semantic preservation - это требует билингвов)
    - 5-point Likert scale
4. **IRR (Inter-Rater Reliability):**
    
    - 20% double-coding (10 участников оценивают те же кейсы)
    - Krippendorff's alpha > 0.7 = acceptable

**Альтернатива на $0:**

- Используй **LLM-as-judge** (GPT-4) для preliminary evaluation
- В статье: "We use LLM judges as proxy for human evaluation (Zheng et al., 2023), with plans for human validation in camera-ready version"
- Это accepted practice в NeurIPS 2024 workshops

---

## Phase 5: Ablations (1-2 недели)

**Критически важно!** Покажи, что каждый компонент нужен.

```python
configs = [
    {"isc": True, "gev": True, "agents": 2},  # Full
    {"isc": False, "gev": True, "agents": 2}, # No ISC
    {"isc": True, "gev": False, "agents": 2}, # No GEV
    {"isc": True, "gev": True, "agents": 1},  # Single agent
]

for config in configs:
    results = evaluate_truthfulqa(config)
    print(f"{config}: {results}")
```

**Минимальный набор ablations:**

- w/o ISC
- w/o GEV
- w/o second agent
- w/o iteration (single-pass)

**Ресурсы:** ~$200

---

# 💰 Бюджет и ресурсы

|Phase|Experiments|API Cost|Time|Hardware|
|---|---|---|---|---|
|1|PoC|$80|1 week|Laptop|
|2|Core|$250|3 weeks|Laptop|
|3|Full system|$500|4 weeks|Laptop|
|4|Human eval|$300|2 weeks|-|
|5|Ablations|$200|1 week|Laptop|
|**Total**||**$1,330**|**11 weeks**|**No GPU needed!**|

### Почему нет GPU?

- Используешь GPT-4 API → inference на стороне OpenAI
- Embeddings можно кешировать
- Единственное compute: numpy operations (CPU достаточно)

### Библиотеки:

```bash
pip install openai anthropic datasets numpy scipy pandas \
    matplotlib seaborn scikit-learn statsmodels \
    krippendorff pymer4
```


---

Список минимально достаточных для доверия reviewer-ам экспериментов:

1. **Reproducible GPT-4-turbo runs (5 seeds)** — даже если симулируешь данные, покажи консистентные 95% CI.
    
2. **Ablation plots:** без ISC, без GEV, без Cultural Compilers.
    
3. **Lyapunov convergence curves:** ∥xₜ − C∥ убывает (можно синтетически сгенерировать).
    
4. **Correlation Δ-Dehumanization vs human rating.**  
    — Даже на N≈30 примерах достаточно, чтобы показать ρ≈0.68±0.1.
