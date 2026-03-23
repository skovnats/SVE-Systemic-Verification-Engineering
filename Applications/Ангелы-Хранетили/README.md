# 🛡️ (возможно) Angels Guardian / Ангелы-Хранители / Schutzengel
## (возможно) **«Цифровой бронежилет для эпохи дронов»**  ДЛЯ СПАСЕНИЯ ЖИЗНЕЙ | Проект в открытом доступе для всех без исключения

### --НЕ ВАНДЕРВАФЕН-- -- все расчёты приблизительные и нужно всё "подкручивать" исходя из обратной свзи реальности

> **Автономная система защиты пехоты от FPV-дронов**  
> **Autonomous infantry protection system against FPV drones**  
> **Autonomes Infanterie-Schutzsystem gegen FPV-Drohnen**

>«Вера без дел мертва». (Иакова 2:20) <br>
>«Свет, который прячут под спудом, гаснет. Свет, который ставят на виду, освещает всех.»

---

## 📌 О проекте / About / Über das Projekt

| 🇷🇺 Русский | 🇬🇧 English | 🇩🇪 Deutsch |
|-------------|--------------|--------------|
| Рой 3+1 БПЛА создаёт «цифровой купол» над подразделением. Обнаружение угроз за 300+ м, оповещение за ≤1.5 сек. Без GPS. Без облака. | 3+1 UAV swarm creates a "digital dome" over the unit. Threat detection at 300+ m, alert in ≤1.5 sec. No GPS. No cloud. | 3+1 UAV-Schwarm erzeugt eine "digitale Kuppel" über der Einheit. Bedrohungserkennung bei 300+ m, Alarm in ≤1.5 Sek. Kein GPS. Kein Cloud. |

**Это не оружие. Это щит.** / **Not a weapon. A shield.** / **Keine Waffe. Ein Schild.**

---

## 🎯 Ключевые метрики / Key Metrics / Kennzahlen

```
┌─────────────────────────────────────────────────────────┐
│  📡 Дальность обнаружения / Detection Range             │
│     300 м (оптика) / 150 м (термал)                     │
│                                                         │
│  ⚡ Время оповещения / Alert Time                       │
│     ≤1.5 сек → ≤0.8 сек (Фаза 3)                        │
│                                                         │
│  🎯 Точность «свой-чужой» / Friend-or-Foe Accuracy     │
│     ≥95%                                                │
│                                                         │
│  🔋 Автономность / Battery Life                         │
│     ≥20 мин без GPS                                     │
│                                                         │
│  💰 Стоимость комплекта / Unit Cost                     │
│     ≤$6 500 (3+1 дроны)                                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Архитектура / Architecture / Architektur

```
                    ┌─────────────┐
                    │   «ОКО»     │  ← Командир роя / Swarm Leader
                    │  60–100 м   │     Höhe: 60–100 m
                    └──────┬──────┘
                           │ UWB + 60 GHz Mesh
          ┌────────────────┼────────────────┐
          │                │                │
    ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
    │ Страж-1   │    │ Страж-2   │    │ Страж-3   │
    │ (фронт)   │    │ (фланг)   │    │ (фланг)   │
    │ 10–30 м   │    │ 10–30 м   │    │ 10–30 м   │
    └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Отряд      │  ← UWB-маяки на бойцах
                    │  3–5 чел.   │     UWB-Tags an Soldaten
                    └─────────────┘
```

### 📦 Стек / Tech Stack / Technik-Stack

| Компонент | Component | Komponente |
|-----------|-----------|------------|
| **Вычислитель** | Orange Pi 5 Plus (RK3588) | RK3588 NPU |
| **Полётный контроллер** | Pixhawk 6X | PX4 Autopilot |
| **ИИ-детекция** | YOLOv11n + ByteTrack | Edge AI |
| **Навигация** | UWB (Pozyx) + VIO | GPS-denied |
| **Связь** | 60 GHz Mesh + LoRa (резерв) | EW-resistant |
| **Камеры** | Arducam IMX477 (GS) + FLIR Lepton | Optic + Thermal |

---

## 📅 Дорожная карта / Roadmap / Zeitplan

```
Фаза 0 ──► Фаза 1 ──► Фаза 2 ──► Фаза 3 ──► Фаза 4
2 нед.     6 нед.     6 нед.     6 нед.     6 нед.
 │          │          │          │          │
 ▼          ▼          ▼          ▼          ▼
Команда    MVP       Swarm     Фронт     Серия
Датасет    «Око»     3+1       5 компл.  100+
```

**Подробнее / Details / Details:** [`Angel Guardian Roadmap.pdf`](./Angel_Guardian_Roadmap.pdf)

---

## 📚 Документация / Documentation / Dokumentation

| Файл / File | Описание / Description |
|-------------|------------------------|
| [`Ангелы Хранители.md`](./Ангелы_Хранители.md) | Концепция, BOM, схемы / Concept, BOM, diagrams |
| [`Angel Guardian Roadmap.pdf`](./Angel_Guardian_Roadmap.pdf) | 6-месячный план, бюджет, риски / 6-month plan, budget, risks |

---

## ⚠️ Дисклеймер / Disclaimer

> **🇷🇺** Проект открыт только для спасения жизней.  
> **🇬🇧** Open-source for saving lives only. 


---

## 📞 Контакты / Contacts / Kontakte

Это подарок Человечеству -- обратная связь не предусмотрена. 

Проект выложен в свободный доступ как концепция и набор идей. Авторы приветствуют создание форков и независимое развитие.

---

## 📜 Лицензия / License / Lizenz

**Для Спасение жизней во Имя Бога -- (возможно) Иисуса Христа**

При необходимости может быть активирована SVE v1.3+ License для защиты от захвата и использования для вреда/избирательного-асимитричного использования. 

---

<br>

<div align="center">

---

### 🕊️

## **ТОЛЬКО для спасения Жизни во Имя Божье**
## **ONLY for saving Lives in the Name of God**
## **NUR zur Rettung von Leben im Namen Gottes**

### ✝️ Иисуса Христа / Jesus Christ / Jesu Christi

> *«Нет больше той любви, как если кто положит душу свою за друзей своих»*  
> *«Greater love has no one than this: to lay down one's life for one's friends»*  
> *«Größere Liebe hat niemand als die: sein Leben hinzugeben für seine Freunde»*

**— Иоанна 15:13 / John 15:13 / Johannes 15,13**

---

</div>


![](KOVnatsky_3.png)
Артём (Коваль) Ковнацкий <br>