"""
email_scheduler.py
==================
Запланированная отправка писем через Gmail (2 аккаунта, BCC, +1 с аппендиксом).

Зависимости: только стандартная библиотека Python 3.8+

Заполни ACCOUNTS, MAIN_RECIPIENTS, BCC_RECIPIENTS, SPECIAL_RECIPIENT
Убедись что в Gmail включены App Passwords (не обычный пароль)
python email_scheduler.py — скрипт сам уснёт до TARGET_TIME
"""

import smtplib
import ssl
import time
import logging
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────
#  КОНФИГУРАЦИЯ — заполните перед запуском
# ─────────────────────────────────────────────

ACCOUNTS = [
    {"email": "account1@gmail.com", "password": "app_password_1"},
    {"email": "account2@gmail.com", "password": "app_password_2"},
]

# Обычные получатели (видят друг друга в поле «Кому»)
MAIN_RECIPIENTS: list[str] = [
    "recipient1@mail.com",
    "recipient2@mail.com",
    # ... до 48 адресов
]

# Скрытая копия — не видна остальным получателям
BCC_RECIPIENTS: list[str] = [
    # "hidden@mail.com",
]

# +1 получатель со спец. аппендиксом (None — не отправлять)
SPECIAL_RECIPIENT: Optional[str] = "special@mail.com"
SPECIAL_APPENDIX: str = "\n\n---\nP.S. Это письмо содержит дополнение специально для вас."

SUBJECT = "Тема письма"
BODY = """\
Текст вашего сообщения.

Он может быть многострочным.
"""

# Время отправки — локальное время машины (ГГГГ-ММ-ДД ЧЧ:ММ:СС)
TARGET_TIME = "2026-06-06 22:22:00"

# Задержка между письмами в секундах (защита от спам-фильтров)
DELAY_BETWEEN_SENDS: float = 3.0

# Количество попыток при ошибке
MAX_RETRIES: int = 3
RETRY_BACKOFF: float = 5.0  # секунд между попытками (удваивается)

# ─────────────────────────────────────────────
#  ЛОГИРОВАНИЕ
# ─────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("email_scheduler.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  СТРУКТУРА ЗАДАЧИ
# ─────────────────────────────────────────────

@dataclass
class SendTask:
    """Одна задача отправки: от кого, кому, содержание."""
    sender_email: str
    sender_password: str
    to: str
    subject: str
    body: str
    is_bcc: bool = False          # скрытая копия
    has_appendix: bool = False    # +1 письмо с аппендиксом

    def label(self) -> str:
        tag = "[BCC]" if self.is_bcc else ("[+1]" if self.has_appendix else "")
        return f"{tag} {self.to} ← {self.sender_email}"


# ─────────────────────────────────────────────
#  ПОСТРОЕНИЕ MIME-СООБЩЕНИЯ
# ─────────────────────────────────────────────

def build_message(task: SendTask) -> MIMEMultipart:
    """
    Создаёт правильное MIME-письмо с поддержкой UTF-8.
    Аналогия: это как сложить конверт с правильными штампами —
    без них почта не доставит даже правильный текст.
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = task.sender_email
    msg["Subject"] = str(Header(task.subject, "utf-8"))
    msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    if task.is_bcc:
        # BCC: поле «Кому» намеренно пустое — получатель не светится
        msg["To"] = "undisclosed-recipients:;"
    else:
        msg["To"] = task.to

    full_body = task.body
    if task.has_appendix:
        full_body += SPECIAL_APPENDIX

    msg.attach(MIMEText(full_body, "plain", "utf-8"))
    return msg


# ─────────────────────────────────────────────
#  ОТПРАВКА С RETRY
# ─────────────────────────────────────────────

def send_with_retry(task: SendTask) -> bool:
    """
    Отправляет письмо с экспоненциальным backoff при ошибках.
    Возвращает True при успехе.
    """
    context = ssl.create_default_context()
    wait = RETRY_BACKOFF

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            msg = build_message(task)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(task.sender_email, task.sender_password)
                server.sendmail(task.sender_email, [task.to], msg.as_bytes())
            log.info("✓ Отправлено: %s", task.label())
            return True

        except smtplib.SMTPAuthenticationError:
            log.error("✗ Ошибка авторизации для %s — пропускаю.", task.sender_email)
            return False  # retry не поможет

        except Exception as exc:
            if attempt < MAX_RETRIES:
                log.warning(
                    "  Попытка %d/%d не удалась (%s). Жду %.0f с...",
                    attempt, MAX_RETRIES, exc, wait
                )
                time.sleep(wait)
                wait *= 2  # exponential backoff
            else:
                log.error("✗ Не удалось отправить %s после %d попыток: %s",
                          task.label(), MAX_RETRIES, exc)
    return False


# ─────────────────────────────────────────────
#  ПОСТРОЕНИЕ ОЧЕРЕДИ ЗАДАЧ
# ─────────────────────────────────────────────

def build_task_queue() -> list[SendTask]:
    """
    Собирает все задачи отправки:
      - MAIN_RECIPIENTS     → обычные письма, аккаунты чередуются
      - BCC_RECIPIENTS      → письма в скрытой копии
      - SPECIAL_RECIPIENT   → +1 письмо с аппендиксом
    """
    tasks: list[SendTask] = []
    n_accounts = len(ACCOUNTS)

    for i, recipient in enumerate(MAIN_RECIPIENTS):
        acc = ACCOUNTS[i % n_accounts]
        tasks.append(SendTask(
            sender_email=acc["email"],
            sender_password=acc["password"],
            to=recipient,
            subject=SUBJECT,
            body=BODY,
        ))

    for i, recipient in enumerate(BCC_RECIPIENTS):
        acc = ACCOUNTS[i % n_accounts]
        tasks.append(SendTask(
            sender_email=acc["email"],
            sender_password=acc["password"],
            to=recipient,
            subject=SUBJECT,
            body=BODY,
            is_bcc=True,
        ))

    if SPECIAL_RECIPIENT:
        acc = ACCOUNTS[len(tasks) % n_accounts]
        tasks.append(SendTask(
            sender_email=acc["email"],
            sender_password=acc["password"],
            to=SPECIAL_RECIPIENT,
            subject=SUBJECT,
            body=BODY,
            has_appendix=True,
        ))

    return tasks


# ─────────────────────────────────────────────
#  УМНЫЙ ПЛАНИРОВЩИК
# ─────────────────────────────────────────────

def smart_sleep_until(target: datetime) -> None:
    """
    Спит до целевого времени одним большим sleep вместо цикла с опросом.
    Аналогия: будильник vs человек, который проверяет часы каждые 10 секунд.
    """
    remaining = (target - datetime.now()).total_seconds()
    if remaining <= 0:
        return

    # Долгий сон — просыпаемся за 60 с, чтобы уточнить
    if remaining > 70:
        log.info("Следующая проверка через %.0f мин (в %s).",
                 (remaining - 60) / 60, target.strftime("%H:%M:%S"))
        time.sleep(remaining - 60)

    # Финальное ожидание с точностью до секунды
    remaining = (target - datetime.now()).total_seconds()
    if remaining > 0:
        log.info("Осталось %.1f с. Готовлюсь...", remaining)
        time.sleep(max(remaining, 0))


def run_scheduler() -> None:
    target = datetime.strptime(TARGET_TIME, "%Y-%m-%d %H:%M:%S")
    tasks = build_task_queue()

    log.info("Задач в очереди: %d  (MAIN=%d, BCC=%d, +1=%s)",
             len(tasks), len(MAIN_RECIPIENTS), len(BCC_RECIPIENTS),
             "да" if SPECIAL_RECIPIENT else "нет")
    log.info("Время запуска:   %s", target.strftime("%Y-%m-%d %H:%M:%S"))

    if datetime.now() < target:
        smart_sleep_until(target)

    log.info("══ Начинаю отправку ══")
    sent, failed = 0, 0

    for task in tasks:
        ok = send_with_retry(task)
        if ok:
            sent += 1
        else:
            failed += 1
        time.sleep(DELAY_BETWEEN_SENDS)

    log.info("══ Готово: %d отправлено, %d ошибок ══", sent, failed)


# ─────────────────────────────────────────────
#  ТОЧКА ВХОДА
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run_scheduler()