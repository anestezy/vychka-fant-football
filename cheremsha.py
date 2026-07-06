import os
import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

logger = logging.getLogger(__name__)


GIF_PATH = os.path.join(os.path.dirname(__file__), "cheremsha.mp4")

async def cheremsha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(GIF_PATH):
        logger.error(f"GIF-файл не найден: {GIF_PATH}")
        await update.message.reply_text("❌ Ошибка: файл с гифкой не найден на сервере.")
        return

    try:
        with open(GIF_PATH, "rb") as gif_file:
            await update.message.reply_animation(
                animation=gif_file,
                caption="🌿 Черемша заряжает! 💚"
            )
    except Exception as e:
        logger.error(f"Ошибка при отправке гифки: {e}")
        await update.message.reply_text("❌ Не удалось отправить гифку. Попробуй позже.")

def get_cheremsha_handler():
    return CommandHandler("cheremsha", cheremsha_command)