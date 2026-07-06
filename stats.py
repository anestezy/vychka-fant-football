
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from db_connection import Database
from utils.formatting import format_stats_summary, POSITION_EMOJI
from datetime import datetime, timedelta, date
import logging

logger = logging.getLogger(__name__)
SELECTING_PERIOD, CUSTOM_START_DATE, CUSTOM_END_DATE = range(3)


async def show_stats_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    telegram_id = user.id
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )

    if not user_record:
        await update.message.reply_text("❌ Ты не зарегистрирован. Напиши /start")
        return ConversationHandler.END

    user_id = user_record[0]['id']
    team_record = Database.execute_query(
        "SELECT id, team_name FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        await update.message.reply_text("❌ Команда не найдена")
        return ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("📅 За день", callback_data='stats_day'),
            InlineKeyboardButton("📆 За неделю", callback_data='stats_week'),
        ],
        [
            InlineKeyboardButton("🗓 За месяц", callback_data='stats_month'),
            InlineKeyboardButton("🌍 За всё время", callback_data='stats_all'),
        ],
        [InlineKeyboardButton("✏️ Произвольный диапазон", callback_data='stats_custom')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📊 *Выбери период для просмотра статистики:*\n\n"
        "Будет показана статистика твоих игроков за выбранный период.",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    return SELECTING_PERIOD


async def stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    telegram_id = user.id
    data = query.data

    logger.info(f"🔍 stats_callback: {data}")
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )
    if not user_record:
        await query.edit_message_text("❌ Пользователь не найден")
        return ConversationHandler.END

    user_id = user_record[0]['id']
    if data == 'stats_day':
        start_date = datetime.now().date()
        end_date = datetime.now().date()
        period_label = "последний день"
        await _show_stats_result(query, user_id, start_date, end_date, period_label)
        return ConversationHandler.END

    elif data == 'stats_week':
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        period_label = "последнюю неделю"
        await _show_stats_result(query, user_id, start_date, end_date, period_label)
        return ConversationHandler.END

    elif data == 'stats_month':
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        period_label = "последний месяц"
        await _show_stats_result(query, user_id, start_date, end_date, period_label)
        return ConversationHandler.END

    elif data == 'stats_all':
        await _show_stats_result(query, user_id, None, None, "всё время")
        return ConversationHandler.END

    elif data == 'stats_custom':
        await query.edit_message_text(
            "📅 Введи *дату начала* в формате ГГГГ-ММ-ДД\n"
            "(например: 2024-01-01)\n\n"
            "Доступный диапазон: 2018-08-11 — 2026-05-17",
            parse_mode='Markdown'
        )
        return CUSTOM_START_DATE

    return ConversationHandler.END


async def get_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_text = update.message.text.strip()
    logger.info(f"🔍 get_start_date: {date_text}")

    try:
        start_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        if start_date > date.today():
            await update.message.reply_text(
                "❌ Дата в будущем! Введи прошедшую дату:\n"
                "(например: 2024-01-01)"
            )
            return CUSTOM_START_DATE

        context.user_data['start_date'] = start_date

        await update.message.reply_text(
            f"✅ Дата начала: *{start_date}*\n\n"
            "📅 Теперь введи *дату окончания* в формате ГГГГ-ММ-ДД\n"
            "(например: 2024-12-31)",
            parse_mode='Markdown'
        )
        return CUSTOM_END_DATE

    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты. Используй ГГГГ-ММ-ДД\n"
            "Попробуй ещё раз:"
        )
        return CUSTOM_START_DATE


async def get_end_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date_text = update.message.text.strip()
    logger.info(f"🔍 get_end_date: {date_text}")

    try:
        end_date = datetime.strptime(date_text, '%Y-%m-%d').date()
        start_date = context.user_data.get('start_date')

        if start_date > end_date:
            await update.message.reply_text(
                "❌ Дата начала позже даты окончания. Попробуй ещё раз:\n"
                "Введи дату начала (ГГГГ-ММ-ДД):"
            )
            context.user_data.clear()
            return CUSTOM_START_DATE
        if end_date > date.today():
            await update.message.reply_text(
                "❌ Дата окончания в будущем! Введи прошедшую дату."
            )
            return CUSTOM_END_DATE
        telegram_id = update.effective_user.id
        user_record = Database.execute_query(
            "SELECT id FROM users WHERE telegram_id = %s",
            params=(telegram_id,),
            fetch=True
        )
        user_id = user_record[0]['id']

        period_label = f"{start_date} — {end_date}"
        await _show_stats_result_message(update.message, user_id, start_date, end_date, period_label)

        context.user_data.clear()
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "❌ Неверный формат даты. Используй ГГГГ-ММ-ДД\n"
            "Попробуй ещё раз:"
        )
        return CUSTOM_END_DATE


async def _show_stats_result(query, user_id, start_date, end_date, period_label):
    stats = _calculate_stats(user_id, start_date, end_date)

    if stats['matches_played'] == 0:
        await query.edit_message_text(
            f"📊 Статистика за {period_label}\n\n"
            "⚠️ За этот период нет сыгранных матчей твоих игроков."
        )
        return

    message = _format_stats_message(stats, period_label)
    await query.edit_message_text(message, parse_mode='Markdown')


async def _show_stats_result_message(message, user_id, start_date, end_date, period_label):
    stats = _calculate_stats(user_id, start_date, end_date)

    if stats.get('error') == 'future_date':
        await message.reply_text(
            "❌ Выбранная дата в будущем! "
            "Игроки ещё не играли в эти даты.\n\n"
            "Попробуй выбрать период с прошедшими матчами."
        )
        return

    if stats['matches_played'] == 0:
        await message.reply_text(
            f"📊 Статистика за {period_label}\n\n"
            "⚠️ За этот период нет сыгранных матчей твоих игроков.\n\n"
            "💡 Возможные причины:\n"
            "• Выбран период до начала сезона\n"
            "• Выбран период в будущем\n"
            "• Твои игроки не играли в эти даты\n\n"
            "Попробуй другой период или команду /stats для выбора из готовых."
        )
        return
    if start_date and end_date:
        date_range = Database.execute_query(
            """
            SELECT 
                MIN(DATE(match_date)) as first_match,
                MAX(DATE(match_date)) as last_match
            FROM fixtures
            WHERE DATE(match_date) BETWEEN %s AND %s
            """,
            params=(start_date, end_date),
            fetch=True
        )

        if date_range and date_range[0]['first_match']:
            actual_first = date_range[0]['first_match']
            actual_last = date_range[0]['last_match']
            if actual_first != start_date or actual_last != end_date:
                await message.reply_text(
                    f"ℹ️ *Примечание:*\n"
                    f"Фактические матчи в базе за период: "
                    f"{actual_first.strftime('%d.%m.%Y')} — {actual_last.strftime('%d.%m.%Y')}\n\n"
                    f"Твой запрос: {start_date.strftime('%d.%m.%Y')} — {end_date.strftime('%d.%m.%Y')}\n",
                    parse_mode='Markdown'
                )
    msg = _format_stats_message(stats, period_label)
    await message.reply_text(msg, parse_mode='Markdown')


def _calculate_stats(user_id, start_date=None, end_date=None):

    today = date.today()

    if start_date and start_date > today:
        return {
            'total_points': 0, 'matches_played': 0, 'avg_points': 0,
            'best_player': None, 'goals': 0, 'assists': 0,
            'clean_sheets': 0, 'yellow_cards': 0, 'red_cards': 0,
            'saves': 0, 'error': 'future_date'
        }

    base_query = """
        SELECT 
            COALESCE(SUM(ps.fantasy_points), 0) as total_points,
            COUNT(DISTINCT ps.fixture_id) as matches_played,
            COALESCE(SUM(ps.goals), 0) as goals,
            COALESCE(SUM(ps.assists), 0) as assists,
            COALESCE(SUM(ps.clean_sheet), 0) as clean_sheets,
            COALESCE(SUM(ps.yellow_cards), 0) as yellow_cards,
            COALESCE(SUM(ps.red_cards), 0) as red_cards,
            COALESCE(SUM(ps.saves), 0) as saves
        FROM user_team_players utp
        JOIN player_stats ps ON utp.player_id = ps.player_id
        JOIN fixtures f ON ps.fixture_id = f.id
        JOIN user_teams ut ON utp.user_team_id = ut.id
        WHERE ut.user_id = %s
    """

    params = [user_id]

    if start_date and end_date:
        base_query += " AND DATE(f.match_date) BETWEEN %s AND %s"
        params.extend([start_date, end_date])

    summary = Database.execute_query(base_query, params=tuple(params), fetch=True)

    if not summary or summary[0]['matches_played'] == 0:
        return {
            'total_points': 0, 'matches_played': 0, 'avg_points': 0,
            'best_player': None, 'goals': 0, 'assists': 0,
            'clean_sheets': 0, 'yellow_cards': 0, 'red_cards': 0,
            'saves': 0,
        }

    stats = summary[0]
    avg_points = stats['total_points'] / stats['matches_played'] if stats['matches_played'] > 0 else 0
    best_player_query = """
        SELECT 
            rp.name, rp.position, rt.short_name as team_name,
            SUM(ps.fantasy_points) as total_pts
        FROM user_team_players utp
        JOIN player_stats ps ON utp.player_id = ps.player_id
        JOIN fixtures f ON ps.fixture_id = f.id
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        JOIN user_teams ut ON utp.user_team_id = ut.id
        WHERE ut.user_id = %s
    """

    best_params = [user_id]
    if start_date and end_date:
        best_player_query += " AND DATE(f.match_date) BETWEEN %s AND %s"
        best_params.extend([start_date, end_date])

    best_player_query += """
        GROUP BY rp.id, rp.name, rp.position, rt.short_name
        ORDER BY total_pts DESC LIMIT 1
    """

    best_player = Database.execute_query(best_player_query, params=tuple(best_params), fetch=True)

    best_player_name = None
    if best_player:
        bp = best_player[0]
        emoji = POSITION_EMOJI.get(bp['position'], '⚽')
        best_player_name = f"{emoji} {bp['name']} ({bp['team_name']}) — {bp['total_pts']} pts"

    return {
        'total_points': int(stats['total_points']),
        'matches_played': int(stats['matches_played']),
        'avg_points': avg_points,
        'best_player': best_player_name,
        'goals': int(stats['goals']),
        'assists': int(stats['assists']),
        'clean_sheets': int(stats['clean_sheets']),
        'yellow_cards': int(stats['yellow_cards']),
        'red_cards': int(stats['red_cards']),
        'saves': int(stats['saves']),
    }


def _format_stats_message(stats, period_label):
    lines = [
        f"📊 *Статистика за {period_label}*\n",
        "═" * 35,
        "",
        f"⭐ *Всего очков:* {stats['total_points']}",
        f"🎮 *Матчей сыграно:* {stats['matches_played']}",
        f"📈 *Среднее за матч:* {stats['avg_points']:.1f}",
        "",
        "═" * 35,
        "📋 *Детальная статистика:*\n",
        f"⚽ Голы: {stats['goals']}",
        f"🎯 Ассисты: {stats['assists']}",
        f"🧤 Сухие матчи: {stats['clean_sheets']}",
        f"🟡 Жёлтые карточки: {stats['yellow_cards']}",
        f"🔴 Красные карточки: {stats['red_cards']}",
        f"🧤 Сейвы (вратари): {stats['saves']}",
    ]

    if stats['best_player']:
        lines.append(f"\n🏆 *Лучший игрок:* {stats['best_player']}")

    return "\n".join(lines)


async def cancel_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🚫 Выбор статистики отменён.")
    return ConversationHandler.END


def get_stats_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('stats', show_stats_menu)],
        states={
            SELECTING_PERIOD: [
                CallbackQueryHandler(stats_callback, pattern='^stats_')
            ],
            CUSTOM_START_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_start_date)
            ],
            CUSTOM_END_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_end_date)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_stats)],
    )