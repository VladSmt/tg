import logging
from telegram import Update, BotCommand
from telegram.ext import (
    CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
)
from datetime import datetime

from . import reminders, utils, config

logger = logging.getLogger(__name__)

DATE, TIME, TEXT, REPEAT = range(4)
temp_data = {}

async def set_commands(app):
    commands = [
        BotCommand("start", "Почати роботу з ботом"),
        BotCommand("addreminder", "Додати нове нагадування"),
        BotCommand("listreminders", "Показати твої нагадування"),
        BotCommand("cancel", "Скасувати поточну операцію"),
    ]
    await app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я бот-нагадувач.\n"
        "Команди:\n"
        "/addreminder - додати нагадування\n"
        "/listreminders - показати твої нагадування\n"
        "/cancel - скасувати поточну операцію"
    )
    logger.info(f"Користувач {update.effective_user.id} почав роботу з ботом")

async def addreminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    temp_data[chat_id] = {}
    await update.message.reply_text("Введи дату нагадування у форматі YYYY-MM-DD:")
    logger.info(f"Користувач {chat_id} почав додавати нагадування")
    return DATE

async def addreminder_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    date_text = update.message.text.strip()
    valid, msg = utils.validate_date(date_text)
    if not valid:
        await update.message.reply_text(msg)
        logger.debug(f"Користувач {chat_id} ввів неправильну дату: {date_text}")
        return DATE
    temp_data[chat_id]['date'] = date_text
    await update.message.reply_text("Введи час нагадування у форматі HH:MM (24-годинний):")
    logger.info(f"Користувач {chat_id} ввів дату: {date_text}")
    return TIME

async def addreminder_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    time_text = update.message.text.strip()
    valid, msg = utils.validate_time(time_text)
    if not valid:
        await update.message.reply_text(msg)
        logger.debug(f"Користувач {chat_id} ввів неправильний час: {time_text}")
        return TIME
    temp_data[chat_id]['time'] = time_text
    await update.message.reply_text("Введи текст нагадування:")
    logger.info(f"Користувач {chat_id} ввів час: {time_text}")
    return TEXT

async def addreminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    temp_data[chat_id]['text'] = text
    await update.message.reply_text(
        "Обери повторюваність нагадування:\n"
        "0 - Не повторювати\n"
        "1 - Щодня\n"
        "2 - Щотижня\n"
        "Введи цифру (0, 1 або 2):"
    )
    logger.info(f"Користувач {chat_id} ввів текст нагадування")
    return REPEAT

async def addreminder_repeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    repeat_input = update.message.text.strip()
    repeat_map = {'0': 'none', '1': 'daily', '2': 'weekly'}
    if repeat_input not in repeat_map:
        await update.message.reply_text("Невірний вибір. Введи 0, 1 або 2:")
        logger.debug(f"Користувач {chat_id} ввів неправильний варіант повторення: {repeat_input}")
        return REPEAT

    repeat = repeat_map[repeat_input]

    dt_str = f"{temp_data[chat_id]['date']} {temp_data[chat_id]['time']}"
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    if dt < datetime.now():
        await update.message.reply_text("Дата і час вже минули. Введи дату з майбутнім часом:")
        logger.debug(f"Користувач {chat_id} ввів минулу дату і час: {dt_str}")
        return DATE

    reminder = {
        "datetime": dt_str,
        "text": temp_data[chat_id]['text'],
        "repeat": repeat
    }
    reminders.add_reminder(chat_id, reminder)
    await update.message.reply_text(f"Нагадування додано з повторенням: {repeat}")
    logger.info(f"Користувач {chat_id} додав нагадування: {reminder}")
    temp_data.pop(chat_id, None)
    return ConversationHandler.END

async def listreminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_reminders = reminders.get_reminders(chat_id)
    if not user_reminders:
        await update.message.reply_text("У тебе немає збережених нагадувань.")
        logger.info(f"Користувач {chat_id} переглянув список нагадувань: пусто")
        return
    msg = "Твої нагадування:\n"
    for i, rem in enumerate(sorted(user_reminders, key=lambda x: x['datetime'])):
        msg += f"{i+1}. {rem['datetime']} - {rem['text']} (повторення: {rem.get('repeat','none')})\n"
    await update.message.reply_text(msg)
    logger.info(f"Користувач {chat_id} переглянув список нагадувань")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    temp_data.pop(chat_id, None)
    await update.message.reply_text("Операцію скасовано.")
    logger.info(f"Користувач {chat_id} скасував операцію")
    return ConversationHandler.END
