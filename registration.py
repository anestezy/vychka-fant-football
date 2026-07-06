
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from db_connection import Database
from config import VALID_FORMATIONS, CURRENT_SEASON
NAME, TEAM_NAME, FORMATION = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing_user = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(user.id,),
        fetch=True
    )

    if existing_user:
        await update.message.reply_text(
            f"👋 Ты уже зарегистрирован!\n\n"
            f"Используй команды:\n"
            f"/team — мой состав\n"
            f"/shop — магазин игроков\n"
            f"/help — помощь"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "⚽ Добро пожаловать в Fantasy Football Bot!\n\n"
        "Давай зарегистрируемся.\n\n"
        "Как тебя зовут?"
    )

    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()

    if len(name) < 2:
        await update.message.reply_text("Имя слишком короткое. Минимум 2 символа:")
        return NAME

    context.user_data['first_name'] = name

    await update.message.reply_text(
        "Отлично! Теперь придумай название для своей команды\n"
        "(например: 'FC Champions', 'Dream Team'):"
    )
    return TEAM_NAME


async def get_team_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    team_name = update.message.text.strip()

    if len(team_name) < 3:
        await update.message.reply_text("Название слишком короткое. Минимум 3 символа:")
        return TEAM_NAME

    if len(team_name) > 50:
        await update.message.reply_text("Название слишком длинное. Максимум 50 символов:")
        return TEAM_NAME

    context.user_data['team_name'] = team_name
    keyboard = [
        ['3-4-3', '4-3-3'],
        ['4-4-2', '3-5-2'],
        ['5-3-2', '4-5-1']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "Выбери стартовую схему команды:",
        reply_markup=reply_markup
    )
    return FORMATION


async def get_formation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    formation = update.message.text.strip()

    if formation not in VALID_FORMATIONS:
        await update.message.reply_text(
            "Неверная схема. Выбери из списка:",
            reply_markup=ReplyKeyboardMarkup(
                [['3-4-3', '4-3-3'], ['4-4-2', '3-5-2'], ['5-3-2', '4-5-1']],
                one_time_keyboard=True, resize_keyboard=True
            )
        )
        return FORMATION

    user = update.effective_user
    telegram_id = user.id
    try:
        Database.execute_query(
            """INSERT INTO users (telegram_id, username, first_name, budget, total_points)
               VALUES (%s, %s, %s, 100.00, 0)""",
            params=(telegram_id, user.username or '', context.user_data['first_name'])
        )
        user_record = Database.execute_query(
            "SELECT id FROM users WHERE telegram_id = %s",
            params=(telegram_id,),
            fetch=True
        )
        user_id = user_record[0]['id']
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка регистрации: {e}")
        return ConversationHandler.END
    try:
        Database.execute_query(
            """INSERT INTO user_teams (user_id, team_name, gameweek, season, formation)
               VALUES (%s, %s, 1, %s, %s)""",
            params=(user_id, context.user_data['team_name'], CURRENT_SEASON, formation)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка создания команды: {e}")
        return ConversationHandler.END
    await update.message.reply_text(
        f"✅ Регистрация завершена!\n\n"
        f"👤 Имя: {context.user_data['first_name']}\n"
        f"⚽ Команда: {context.user_data['team_name']}\n"
        f"📐 Схема: {formation}\n"
        f"💰 Бюджет: 100.00 млн\n\n"
        "Теперь собери свой состав командой /shop",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Регистрация отменена. Напиши /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def get_registration_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            TEAM_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_team_name)],
            FORMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_formation)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )