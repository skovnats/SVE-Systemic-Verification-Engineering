# **δ-Dashboard v0**: минимальный, чтобы уже работал, логировался и порождал Field Notes.

---

## 1) Что такое δ-Dashboard v0

**Один индекс δ(t)** + **10 прокси-метрик** + **лог вмешательств** + **post-audit**.

Цель: не “доказать THE SYSTEM”, а **замерять деградацию/улучшение** после конкретных изменений.

---

## 2) Метрики v0 (как считать)

### δ-метрики (6)

1. **Recourse Rate (RR)**
   `RR = appeals_with_clear_path / total_decisions`

2. **Explanation Debt (ED)**
   `ED = decisions_without_explanation / total_decisions`

3. **Override Friction (OF)**
   `OF = median(minutes_to_human_override)` *(или steps_to_override)*

4. **Objectification Language Index (OLI)**
   `OLI = objectifying_terms / total_terms` *(на корпусе тикетов/писем/политик)*

5. **Moral Disengagement Marker Rate (MDM)**
   `MDM = disengagement_markers / total_sentences`

6. **Harm Externalization Ratio (HER)**
   `HER = decisions_without_stakeholder_review / total_decisions`

### “Экономика внимания” (4)

7. **Attention Gini (AG)** — Джини по распределению показов/внимания

8. **Interrupt Rate (IR)**
   `IR = interruptions_per_hour` *(уведомления/переключения/встречи)*

9. **Goal Drift Index (GDI)**
   `GDI = 1 - (planned_tasks_completed / planned_tasks_total)` *(или план/факт времени)*

10. **Truth-Contact Ratio (TCR)**
    `TCR = grounded_items / total_items` *(доля материалов/решений с проверяемыми источниками/логами)*

---

## 3) Как собрать данные без “большой науки”

**Минимум источников:**

* решения/тикеты (Jira/GitHub issues/таблица решений)
* коммуникации (Slack/email/документы — хотя бы выборка)
* календарь/уведомления (ручной лог или трекер)
* контент/ссылки (VKB entries)

**Сбор v0** = руками + полуавтомат:

* тексты → простые словари маркеров (OLI/MDM)
* решения → чекбоксы “есть объяснение / есть recourse / есть stakeholder review”
* override → время/шаги

---

## 4) Как свести всё в δ-score (простая нормализация)

Для каждой метрики делай **0..1** (хуже = ближе к 1):

* где “больше = хуже” (ED, OF, OLI, MDM, HER, IR, GDI):
  `m_norm = clip((m - target)/(max - target), 0, 1)`

* где “больше = лучше” (RR, TCR):
  `m_norm = 1 - clip((m - min)/(target - min), 0, 1)`

**δ(t) = mean(m_norm across selected metrics)**
(в v0 без весов; веса можно добавить позже через XI.b)

---

## 5) Формат данных (CSV) — чтобы не ломаться

### `delta_metrics.csv`

Колонки:

* `date`
* `project`
* `RR, ED, OF, OLI, MDM, HER, AG, IR, GDI, TCR`
* `delta_score`
* `notes_link` (Field Note / VKB ссылкой)

### `interventions.csv`

* `date`
* `project`
* `intervention_id`
* `description`
* `expected_direction` (e.g., ED↓, RR↑)
* `field_note_link`

---

## 6) Визуализация v0 (2 графика достаточно)

1. **Линия δ(t)** по неделям
2. **Радар/бар** по метрикам текущей недели (где хуже всего)

---

## 7) Репо-структура (рекомендую)

```
Applications/
  delta_dashboard/
    data/
      delta_metrics.csv
      interventions.csv
    dictionaries/
      objectification_terms.txt
      moral_disengagement_markers.txt
    scripts/
      compute_delta.py
      update_week.py
    reports/
      WEEK_YYYY-WW.md
```

---

## 8) Мини-скрипт расчёта δ (Python, v0)

```python
import pandas as pd
import numpy as np

TARGETS = {
    "RR": ("higher_better", 0.70, 0.00, 1.00),
    "ED": ("lower_better", 0.20, 0.00, 1.00),
    "OF": ("lower_better", 30.0, 0.0, 240.0),  # minutes
    "OLI": ("lower_better", 0.02, 0.00, 0.20),
    "MDM": ("lower_better", 0.02, 0.00, 0.20),
    "HER": ("lower_better", 0.20, 0.00, 1.00),
    "AG": ("lower_better", 0.35, 0.00, 0.80),
    "IR": ("lower_better", 6.0, 0.0, 30.0),
    "GDI": ("lower_better", 0.30, 0.00, 1.00),
    "TCR": ("higher_better", 0.60, 0.00, 1.00),
}

def norm(value, mode, target, vmin, vmax):
    value = float(value)
    if mode == "lower_better":
        # below target is good
        return np.clip((value - target) / (vmax - target), 0, 1)
    else:
        # above target is good
        return 1 - np.clip((value - vmin) / (target - vmin), 0, 1)

df = pd.read_csv("Applications/delta_dashboard/data/delta_metrics.csv")
metric_cols = list(TARGETS.keys())

normed = []
for col in metric_cols:
    mode, target, vmin, vmax = TARGETS[col]
    normed.append(df[col].apply(lambda x: norm(x, mode, target, vmin, vmax)))

df["delta_score"] = pd.concat(normed, axis=1).mean(axis=1)
df.to_csv("Applications/delta_dashboard/data/delta_metrics.csv", index=False)
print("Updated delta_score for", len(df), "rows")
```

---

## 9) Как это превращается в Field Note

Каждую неделю/месяц:

* фиксируешь δ(t0)
* делаешь **одно вмешательство**
* фиксируешь δ(t1)
* пишешь Field Note: *что сделали → что вышло → что изменили*

---