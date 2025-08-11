import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def validate_date(date_text: str) -> (bool, str):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True, ""
    except ValueError:
        msg = "Невірний формат дати. Будь ласка, введи дату у форматі YYYY-MM-DD (наприклад, 2025-08-11)."
        logger.debug(f"Validation error for date '{date_text}': {msg}")
        return False, msg

def validate_time(time_text: str) -> (bool, str):
    try:
        datetime.strptime(time_text, "%H:%M")
        return True, ""
    except ValueError:
        msg = "Невірний формат часу. Будь ласка, введи час у форматі HH:MM (24-годинний, наприклад, 14:30)."
        logger.debug(f"Validation error for time '{time_text}': {msg}")
        return False, msg
