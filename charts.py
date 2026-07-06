
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db_connection import Database
import os


async def show_charts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    telegram_id = user.id
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )

    if not user_record:
        await update.message.reply_text("❌ Ты не зарегистрирован. Напиши /start")
        return

    user_id = user_record[0]['id']
    team_record = Database.execute_query(
        "SELECT id FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        await update.message.reply_text("❌ Команда не найдена")
        return
    keyboard = [

        [InlineKeyboardButton("🥧 Распределение по позициям", callback_data='chart_positions')],
        [InlineKeyboardButton("🏆 Топ игроков", callback_data='chart_top')],

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📊 *Выбери тип графика:*\n\n"
        "Будет сгенерировано изображение с визуализацией данных твоей команды.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def charts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    telegram_id = user.id
    data = query.data
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )
    if not user_record:
        await query.edit_message_text("❌ Пользователь не найден")
        return

    user_id = user_record[0]['id']
    from utils.charts import (
        create_points_over_time_chart,
        create_position_distribution_chart,
        create_top_players_chart,

    )

    filepath = None
    caption = ""



    if data == 'chart_positions':
        await query.edit_message_text("🥧 Генерирую диаграмму распределения...")
        filepath = create_position_distribution_chart(user_id)
        caption = "🥧 Распределение игроков по позициям"

    elif data == 'chart_top':
        await query.edit_message_text("🏆 Генерирую график топ игроков...")
        filepath = create_top_players_chart(user_id, top_n=5)
        caption = "🏆 Топ-5 игроков по очкам"



    if filepath and os.path.exists(filepath):
        with open(filepath, 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode='Markdown'
            )
        await query.message.delete()
        try:
            os.remove(filepath)
        except:
            pass
    else:
        await query.edit_message_text(
            "❌ Не удалось сгенерировать график. "
            "Возможно, недостаточно данных."
        )