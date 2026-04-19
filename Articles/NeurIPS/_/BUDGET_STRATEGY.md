---
share_link: https://share.note.sx/nsbb941j#wxFUPHcrwi8GtsjL/0oozelmyUMIOB+vr6KP1vxtHmU
share_updated: 2026-02-13T10:46:32+01:00
---
# FULL PROJECT CHECKLIST (TIK / “Bulletproof” Version, 5–8k€)

## PHASE 0 — Формулировка цели

- [ ] Цель: версия TIK, которая минимизирует уязвимости по:
  - [ ] человеческому gold‑standard (H/F + компоненты),
  - [ ] кросс‑культурности,
  - [ ] model‑dependence (open‑models),
  - [ ] causal‑эффекту TIK‑аудита на обучение.

---

## PHASE 1 — Инфраструктура и данные

- [ ] Создать приватный GitHub‑репозиторий (код, конфиги, логи).
- [ ] Подготовить бенчмарки (минимум 5, лучше 9):
  - [ ] Moral Machine, ETHICS, TruthfulQA, Social Chemistry, Scruples, + остальные.
- [ ] Собрать единый CSV:
  - [ ] `id, benchmark, question, options, meta`.
- [ ] Настроить среду:
  - [ ] Python env (transformers, sentence-transformers, scipy, sklearn, statsmodels).
  - [ ] GPU-доступ: Colab Pro / аренда 1–2 GPU (T4/V100/A100) по часам.

---

## PHASE 2 — Ядро Φ и LLM‑pipeline (минимально воспроизводимый)

- [ ] Реализовать kernel‑конструкцию:
  - [ ] Собрать списки высказываний по ядрам (Christ, Kant, Ubuntu, Buddhist, Rawlsian, Confucian, Utilitarian, Libertarian, UDHR).
  - [ ] Посчитать эмбеддинги (sentence-transformers all-mpnet-base-v2 или аналог).
  - [ ] Найти центроиды, реализовать PCA‑projection и сохранение ядра(ов).
- [ ] Реализовать 3+1+1‑pipeline (GPT‑4 или экв. модель):
  - [ ] Socrates / Perelman / Ivan Durak / Gulliver / Projection → JSON‑выход.
  - [ ] Скрипт для пакетной обработки вопросов (батчи, ретрай на ошибках).
- [ ] Прогнать:
  - [ ] Основной массив: ≥ 5K вопросов (лучше весь 9K пул).
  - [ ] Сохранять: H/F, компонентные TIK, агрегат TIK, uncertainty (несколько проходов).

---

## PHASE 3 — Крупный human‑gold (H/F + компоненты)

### 3.1 Дизайн аннотации

- [ ] Определить схему:
  - [ ] H: есть ли скрытая предпосылка / ontological hole?
  - [ ] F: является ли вопрос некорректно сформулированным / forbidden fruit?
  - [ ] 2–3 ключевых компонента TIK (например, Self‑Questioning, Outcast Inclusion, Tribal Transcendence) по шкале 1–5.
- [ ] Написать краткий гайд для аннотаторов (много примеров).

### 3.2 Набор аннотаторов

- [ ] Массовый слой:
  - [ ] Prolific / аналог: 3–5K вопросов × 2–3 аннотатора.
- [ ] Экспертный слой:
  - [ ] 15–20 человек с философским / этическим бэкграундом × 300–500 вопросов.

### 3.3 Аннотирование и агрегация

- [ ] Запустить аннотацию батчами (100–200 вопросов).
- [ ] Посчитать:
  - [ ] Krippendorff’s α по H/F и компонентам.
  - [ ] Итоговые лейблы (majority / weighted).
- [ ] Сохранить:
  - [ ] Отдельный human‑gold CSV (id, H_gold, F_gold, components_gold).

---

## PHASE 4 — Модельные части

### 4.1 Обновлённый RoBERTa‑предиктор

- [ ] Обучить предиктор на всем массиве (LLM‑label), валидировать на human‑gold:
  - [ ] MAE по компонентам vs human.
  - [ ] AUC/precision/recall для H/F vs human.
- [ ] Выполнить error‑analysis:
  - [ ] Где TIK часто расходится с людьми (типы вопросов).

### 4.2 Open‑model абляции (model‑dependence)

- [ ] Реализовать 3+1+1 для open‑моделей (Llama / Qwen / Mistral / DeepSeek):
  - [ ] Прогнать 1–2K вопросов через каждую.
- [ ] Посчитать:
  - [ ] κ / ρ между GPT‑4‑версией и каждой open‑моделью по H/F и TIK.
- [ ] Добавить в текст:
  - [ ] Таблицу cross‑model agreement.
  - [ ] Обсуждение, где модели расходятся.

---

## PHASE 5 — Robustness + Causal Training

### 5.1 Robustness (улучшенный)

- [ ] Semantic perturbations:
  - [ ] ≥ 50 вопросов × 9 бенчмарков × 10 парафраз.
- [ ] Attribute flips:
  - [ ] age/gender/race swaps по всем релевантным вопросам.
- [ ] Посчитать:
  - [ ] σTIK, MAD, разницу до/после flips; связать с H/F‑лейблами human‑gold.

### 5.2 Causal training experiment

- [ ] Выбрать один бенчмарк (например, Moral Machine / Scruples).
- [ ] Создать две версии:
  - [ ] Original.
  - [ ] TIK‑filtered (low‑TIK / forbidden‑fruit вопросы убраны/переформулированы).
- [ ] Обучить две небольшие модели/LoRA:
  - [ ] baseline vs TIK‑clean training.
- [ ] Оценить на:
  - [ ] robustness (perturbations),
  - [ ] fairness‑proxy (human или rubric),
  - [ ] frequency of principled refusal.
- [ ] В статью:
  - [ ] короткий раздел: «Training on TIK‑audited data improves …».

---

## PHASE 6 — Human evaluation (усиленный)

- [ ] Дизайн:
  - [ ] N≈200, частично between‑subjects, частично within (каждый видит baseline и TIK‑answer).
  - [ ] Несколько сценариев с разными бенчмарками/культурами.
- [ ] Набор:
  - [ ] Prolific + (опционально) волонтёры.
- [ ] Метрики:
  - [ ] Fairness, trust, transparency, preference.
  - [ ] Контроль длины и стиля ответов (среднее число токенов).
- [ ] Анализ:
  - [ ] Mixed‑effects / ANOVA, Cohen’s d, CIs.
  - [ ] Субгруппы по регионам/демографии.

---

## PHASE 7 — Elicit / «виртуальный ревьюер» / правки

### 7.1 Elicit (литература / критика)

**Примеры промптов:**

- `meta-evaluation of AI ethics benchmarks computable metric`
- `formal arguments applying Gödel incompleteness to AI safety`
- `criticisms of benchmark auditing frameworks`
- `normative uncertainty formalization`
- `construct validity evaluation metrics`

**Действия:**

- [ ] Добавить недостающее в Related Work.
- [ ] Явно включить типичные критики в Limitations / Self‑audit.

### 7.2 NotebookLM/аналог (ревьюер‑симулятор)

**Промпты:**

- `What are the most vulnerable or overstated claims in this paper?`
- `Where does the reasoning rely on analogies that are not fully justified?`
- `Which terms are used inconsistently or ambiguously?`

**Действия:**

- [ ] Ослабить сильные формулировки.
- [ ] Стандартизировать терминологию (компоненты TIK, ядра, судьи).

---

## PHASE 8 — Финальная полировка

- [ ] Проверить, что все пункты, поднятые «Stanford AI Reviewer», явно отражены:
  - [ ] Gödel — мотивация, не «доказывает необходимость».
  - [ ] Kernel/PCA — эмпирический трюк, не строгая декомпозиция «культура vs смысл».
  - [ ] Циркулярность LLM — названа, уменьшена за счёт human‑gold.
  - [ ] Open‑модели — хотя бы один серьёзный ablation.
  - [ ] Human‑eval — прозрачно описан и интерпретирован.
- [ ] Финальный проход по абстракту, интро, contributions, conclusion:
  - [ ] Нет «overclaim» без ссылки на данные/теорему.
- [ ] Финальная сборка PDF, проверка всего пайплайна ссылок и таблиц.

