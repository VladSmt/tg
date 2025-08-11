import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

from .config import DATA_FILE

logger = logging.getLogger(__name__)

def load_data():
    path = Path(DATA_FILE)
    if not path.exists():
        path.parent.mkdir(exist_ok=True, parents=True)
        path.write_text("{}")
        logger.info(f"Створено новий файл даних {DATA_FILE}")
    try:
        data = json.loads(path.read_text())
        return data
    except Exception as e:
        logger.error(f"Помилка при завантаженні даних з {DATA_FILE}: {e}")
        return {}

def save_data(data):
    try:
        Path(DATA_FILE).write_text(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info("Дані успішно збережено")
    except Exception as e:
        logger.error(f"Помилка при збереженні даних: {e}")

def add_reminder(user_id: int, reminder: dict):
    data = load_data()
    user_str = str(user_id)
    if user_str not in data:
        data[user_str] = []
    data[user_str].append(reminder)
    save_data(data)
    logger.info(f"Додано нагадування для користувача {user_id}: {reminder}")

def get_reminders(user_id: int):
    data = load_data()
    return data.get(str(user_id), [])

def remove_reminder(user_id: int, index: int):
    data = load_data()
    user_str = str(user_id)
    if user_str in data and 0 <= index < len(data[user_str]):
        removed = data[user_str].pop(index)
        save_data(data)
        logger.info(f"Видалено нагадування для користувача {user_id}: {removed}")

async def check_and_send_reminders(app):
    data = load_data()
    now = datetime.now()
    updated = False

    for user_str, reminders_list in data.items():
        chat_id = int(user_str)
        to_remove = []
        for rem in reminders_list:
            try:
                rem_dt = datetime.strptime(rem['datetime'], "%Y-%m-%d %H:%M")
            except Exception as e:
                logger.warning(f"Невірний формат дати в нагадуванні користувача {chat_id}: {rem} ({e})")
                continue

            if rem_dt <= now:
                try:
                    await app.bot.send_message(chat_id, f"⏰ Нагадування:\n{rem['text']}")
                    repeat = rem.get('repeat', 'none')
                    if repeat == 'daily':
                        rem['datetime'] = (rem_dt + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
                    elif repeat == 'weekly':
                        rem['datetime'] = (rem_dt + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M")
                    else:
                        to_remove.append(rem)
                    updated = True
                    logger.info(f"Надіслано нагадування користувачу {chat_id}: {rem['text']}")
                except Exception as e:
                    logger.warning(f"Не вдалося надіслати нагадування користувачу {chat_id}: {e}")

        for rem in to_remove:
            reminders_list.remove(rem)

    if updated:
        save_data(data)
