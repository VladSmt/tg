import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
)

from . import handlers, reminders

from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def scheduler_job(app):
    await reminders.check_and_send_reminders(app)

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.info("Стартує бот-нагадувач")

    app = ApplicationBuilder().token(handlers.config.TOKEN).build()

    await handlers.set_commands(app)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addreminder', handlers.addreminder_start)],
        states={
            handlers.DATE: [MessageHandler(~filters.COMMAND & filters.TEXT, handlers.addreminder_date)],
            handlers.TIME: [MessageHandler(~filters.COMMAND & filters.TEXT, handlers.addreminder_time)],
            handlers.TEXT: [MessageHandler(~filters.COMMAND & filters.TEXT, handlers.addreminder_text)],
            handlers.REPEAT: [MessageHandler(~filters.COMMAND & filters.TEXT, handlers.addreminder_repeat)],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
    )

    app.add_handler(CommandHandler('start', handlers.start))
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('listreminders', handlers.listreminders))
    app.add_handler(CommandHandler('cancel', handlers.cancel))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(scheduler_job, "interval", minutes=1, args=(app,))
    scheduler.start()

    logger.info("Бот запущений та чекає повідомлень...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
