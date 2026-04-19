---
share_link: https://share.note.sx/hg7qrqa1#nqOhgFYc+kKsofRK4jrsFvbNyh1Di42fN8fm2XZGK3o
share_updated: 2026-02-13T10:47:32+01:00
---
# FINAL CHECKLIST (TIK / NeurIPS, ≤ ~500 €)

https://www.perplexity.ai/search/neurips-main-statia-shablon-ch-wPJuhZ8UTIS3CIDoViJMrw#0
## 0. Числа и факты

- [ ] Все числовые утверждения в абстракте и секциях 4–7 соответствуют реальным экспериментам.
- [ ] Исправить опечатку: вместо `p = -0.94` → `Spearman ρ = -0.94, p < .001` + 95% CI. *(Stanford AI Reviewer)*

---

## 1. Структура и очистка PDF

- [ ] Убрать `SVE License v1.3+` из титульной.
- [ ] Удалить все `TODO`, `Table ??`, пустые `Appendix )`.
- [ ] Убедиться, что:
  - [ ] Нумерация аппендиксов A, B, C, … без дублей (нет повторных заголовков вроде `C Alternative kernel comparison` / `D Alternative kernel comparison`).
  - [ ] Author Meta‑Checklist полностью отсутствует в PDF (остается только закомментированным в .tex).
- [ ] Проверить, что main text ≤ 9 страниц (до References).

---

## 2. Определения и метод (понятность / реплицируемость)

- [ ] В основном тексте (раздел 3.6) дать компактную, но **формально точную** спецификацию всех 7 TIK‑компонент:
  - [ ] Для каждого компонента: что считается входом (вопрос, список ответов, оценки судей), как считается числовое значение (формула или псевдоформула), как нормируется. *(Stanford AI Reviewer)*
  - [ ] Добавить одну ссылку на аппендикс с полными формулами (Appendix V), но сделать main‑body достаточным для понимания.
- [ ] В разделе про forbidden fruits/ontological holes явно описать критерий, по которому вопрос помечается как «плод» и как это реализовано в пайплайне (порог по aΦ, H/F‑флаг). *(Stanford AI Reviewer – “provably wrong”)*

---

## 3. Gödel‑часть и формальные претензии

- [ ] В интро / contributions:
  - [ ] Ослабить формулировки про «necessity argument» так, чтобы ясно: Gödel‑цепочка — **мотивация**, а не общезначимая теорема про все AI‑системы. *(Stanford AI Reviewer)*
- [ ] В начале Appendix A добавить явную фразу:
  - [ ] Что это «motivating formal argument under explicit assumptions», не формальное доказательство необходимости для всех реалистичных CogOS.
- [ ] В основном тексте оставить только 1 абзац о Gödel‑trolley и «do‑not‑do‑wrong», с прямой отсылкой в App A, без ощущения, что из этого «логически следует» весь TIK. *(Stanford AI Reviewer)*

---

## 4. Kernel и PCA (культурные оси)

- [ ] В описании ядра:
  - [ ] Заменить формулировки «culture-specific axes» на более нейтральное «high‑variance directions that partially correlate with language/corpus differences». *(Stanford AI Reviewer)*
  - [ ] Явно перенести сильное утверждение «orthogonal to culture» в раздел Limitations / Self‑audit как гипотезу, а не факт.
- [ ] В Sensitivity Appendix:
  - [ ] Ясно написать, что PCA‑удаление — эмпирический трюк, а не доказанное разделение «культура vs содержание».

---

## 5. LLM‑лейблы, круг и open‑модели

- [ ] В Limitations / Self‑audit:
  - [ ] Ещё раз явно назвать это «LLM‑assisted labeling» и подчеркнуть, что 91% — точность по отношению к pipeline, а не к «истинной» разметке. *(Stanford AI Reviewer)*
- [ ] Если позволяет время/бюджет: сделать **маленький open‑model ablation**:
  - [ ] Для 100–200 вопросов прогнать 3+1+1 или упрощённый judge‑pipeline через сильную открытую модель (Llama/Mixtral/DeepSeek).
  - [ ] Посчитать κ или ρ между GPT‑4‑версиями TIK и open‑model TIK.
  - [ ] Добавить 1–2 предложения: «On a 200‑question subset, open‑model judges agree with GPT‑4 labels at κ ≈ …». *(Stanford AI Reviewer)*  
  - Если не успеваешь — оставить это как явный пункт future work в Self‑audit.

---

## 6. Human‑grounded validation

- [ ] Уточнить в секции 7:
  - [ ] Размер и дизайн выборки (within/between), способ набора (Prolific + добровольцы).
  - [ ] Честно указать, что стиль/verbosity TIK‑ответов не контролировались строго, и добавить 1 предложение в Limitations: возможный вклад стиля в рост fairness/transparency. *(Stanford AI Reviewer)*
- [ ] Если возможно с текущим N:
  - [ ] Добавить 1–2 предложения о средней длине ответов (baseline vs TIK) — чтобы показать, что эффект не чисто из‑за «длиннее текста».

---

## 7. Related Work и сравнения

- [ ] Добавить 2–3 предложения в Related Work о:
  - [ ] МоРеBench / process‑level moral reasoning (и чем TIK отличается — фокус на вопросах, а не только на процессе). *(Stanford AI Reviewer)*
  - [ ] Работах по abstention / refusal (AbstainQA / multi‑LLM collaboration) и провести простую словесную связку с forbidden fruits.
- [ ] В Discussion явно отбить:
  - [ ] TIK можно комбинировать с rubric‑based eval (в духе MoReBench), а не противопоставлять.

---

## 8. Kernel diversity (минимально)

- [ ] В Kernel Appendix:
  - [ ] Чётко перечислить уже включённые традиции (Christ, Kant, Ubuntu, Buddhist, Rawlsian, Confucian и т.д.).
  - [ ] Добавить 1–2 предложения, что расширение на UDHR / Islamic / Indigenous этики — явная линия future work, и что текущий набор **не претендует** на полноту. *(Stanford AI Reviewer)*

---

## 9. Финальный проход

- [ ] Проверить, что все пункты с пометкой *(Stanford AI Reviewer)* адресованы явно в тексте (1–2 фразы/абзаца).
- [ ] Ещё раз прочитать абстракт, секции 1–3 и 7:
  - [ ] Нет ли «overclaim» без прямой ссылки на эксперимент или theorem.
- [ ] Скомпилировать финальный PDF и сохранить копию перед сабмитом.

