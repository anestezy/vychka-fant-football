
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db_connection import Database
import logging

logger = logging.getLogger(__name__)


async def show_captain_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

    team_id = team_record[0]['id']
    players = Database.execute_query(
        """
        SELECT 
            utp.id as utp_id,
            utp.is_captain,
            utp.is_vice_captain,
            rp.id as player_id,
            rp.name,
            rp.position,
            rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = %s AND utp.is_captain = 0
        ORDER BY rp.total_points DESC
        """,
        params=(team_id,),
        fetch=True
    )

    if not players:
        await update.message.reply_text(
            "⚠️ В команде нет игроков для выбора капитана. Используй /shop чтобы набрать состав!"
        )
        return
    current_captain_record = Database.execute_query(
        """
        SELECT rp.name, rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = %s AND utp.is_captain = 1
        """,
        params=(team_id,),
        fetch=True
    )

    current_captain = current_captain_record[0] if current_captain_record else None
    current_vice_record = Database.execute_query(
        """
        SELECT rp.name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        WHERE utp.user_team_id = %s AND utp.is_vice_captain = 1
        """,
        params=(team_id,),
        fetch=True
    )
    current_vice = current_vice_record[0]['name'] if current_vice_record else None
    lines = [
        "👑 *Назначение капитана и вице-капитана*\n",
        "═" * 35,
    ]

    if current_captain:
        lines.append(f"👑 Капитан: *{current_captain['name']}* ({current_captain['team_name']}) (очки ×2)")
    else:
        lines.append("👑 Капитан: _не выбран_")

    if current_vice:
        lines.append(f"🅥 Вице-капитан: *{current_vice}* (запасной)")
    else:
        lines.append("🅥 Вице-капитан: _не выбран_")

    lines.append("\n" + "═" * 35)
    lines.append("\n📋 *Выбери нового капитана:*")

    message = "\n".join(lines)
    captain_keyboard = []
    for p in players:
        emoji = "⚽"
        button_text = f"{emoji} {p['name']} ({p['team_name']})"
        captain_keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"set_captain_{p['utp_id']}"
            )
        ])
    captain_keyboard.append([
        InlineKeyboardButton("🅥 Выбрать вице-капитана", callback_data='show_vice_menu')
    ])

    captain_keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='captain_back')
    ])

    reply_markup = InlineKeyboardMarkup(captain_keyboard)

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def captain_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    data = query.data

    logger.info(f"captain_callback получил data: '{data}'")
    print(f"captain_callback получил data: '{data}'")

    if data == 'captain_back':
        logger.info("Переход к составу")
        await query.message.delete()
        from unittest.mock import MagicMock
        fake_update = MagicMock()
        fake_update.message = query.message
        fake_update.effective_user = user
        from handlers.team import show_team
        await show_team(fake_update, context)
        return

    if data == 'change_captain':
        logger.info("Смена капитана")
        await query.message.delete()
        from unittest.mock import MagicMock
        fake_update = MagicMock()
        fake_update.message = query.message
        fake_update.effective_user = user
        await show_captain_menu(fake_update, context)
        return

    if data.startswith('set_captain_'):
        utp_id = int(data.replace('set_captain_', ''))
        logger.info(f"Назначение капитана: utp_id={utp_id}")
        await _set_captain(query, utp_id)
        return

    if data.startswith('set_vice_'):
        utp_id = int(data.replace('set_vice_', ''))
        logger.info(f"Назначение вице-капитана: utp_id={utp_id}")
        await _set_vice_captain(query, utp_id)
        return

    if data == 'show_vice_menu':
        logger.info("Показ меню вице-капитана")
        await _show_vice_menu(query, context)
        return

    logger.warning(f"Неизвестный callback_data: '{data}'")


async def _set_captain(query, utp_id):
    player = Database.execute_query(
        """
        SELECT utp.*, rp.name, rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.id = %s
        """,
        params=(utp_id,),
        fetch=True
    )

    if not player:
        await query.edit_message_text("❌ Игрок не найден")
        return

    player = player[0]
    team_id = player['user_team_id']

    try:
        Database.execute_query(
            "UPDATE user_team_players SET is_captain = 0 WHERE user_team_id = %s",
            params=(team_id,)
        )
        if player['is_vice_captain']:
            Database.execute_query(
                "UPDATE user_team_players SET is_vice_captain = 0 WHERE id = %s",
                params=(utp_id,)
            )
        Database.execute_query(
            "UPDATE user_team_players SET is_captain = 1 WHERE id = %s",
            params=(utp_id,)
        )
        keyboard = [
            [InlineKeyboardButton("🅥 Выбрать вице-капитана", callback_data='show_vice_menu')],
            [InlineKeyboardButton("👑 Сменить капитана", callback_data='change_captain')],
            [InlineKeyboardButton("⬅️ Назад", callback_data='captain_back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"✅ *{player['name']}* ({player['team_name']}) назначен капитаном!\n\n"
            f"👑 Его очки будут удвоены в следующем геймвике.\n\n"
            f"Нажми «Выбрать вице-капитана» чтобы назначить запасного капитана.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка назначения: {e}")


async def _set_vice_captain(query, utp_id):
    try:
        player = Database.execute_query(
            """
            SELECT utp.*, rp.name, rt.short_name as team_name
            FROM user_team_players utp
            JOIN real_players rp ON utp.player_id = rp.id
            JOIN real_teams rt ON rp.current_team_id = rt.id
            WHERE utp.id = %s
            """,
            params=(utp_id,),
            fetch=True
        )

        if not player:
            await query.edit_message_text("❌ Игрок не найден")
            return

        player = player[0]
        team_id = player['user_team_id']
        if player['is_captain']:
            await query.answer("⚠️ Этот игрок уже капитан!", show_alert=True)
            return
        Database.execute_query(
            "UPDATE user_team_players SET is_vice_captain = 0 WHERE user_team_id = %s",
            params=(team_id,)
        )
        Database.execute_query(
            "UPDATE user_team_players SET is_vice_captain = 1 WHERE id = %s",
            params=(utp_id,)
        )
        keyboard = [
            [InlineKeyboardButton("👑 Сменить капитана", callback_data='change_captain')],
            [InlineKeyboardButton("⬅️ Назад к составу", callback_data='captain_back')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"✅ *{player['name']}* ({player['team_name']}) назначен вице-капитаном!\n\n"
            f"🅥 Если капитан не сыграет (0 минут), очки вице-капитана будут удвоены.",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        await query.answer(f"❌ Ошибка: {e}", show_alert=True)


async def _show_vice_menu(query, context):
    """Показать меню выбора вице-капитана"""
    user = query.from_user
    telegram_id = user.id
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )
    user_id = user_record[0]['id']

    team_record = Database.execute_query(
        "SELECT id FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )
    team_id = team_record[0]['id']
    players = Database.execute_query(
        """
        SELECT 
            utp.id as utp_id,
            utp.is_vice_captain,
            rp.name,
            rp.position,
            rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = %s AND utp.is_captain = 0
        ORDER BY rp.total_points DESC
        """,
        params=(team_id,),
        fetch=True
    )

    lines = [
        "🅥 *Выбери вице-капитана*\n",
        "Если капитан не сыграет (0 минут), очки вице-капитана будут удвоены.",
        "\n" + "═" * 35,
    ]

    keyboard = []
    for p in players:
        emoji = "🅥" if p['is_vice_captain'] else "⚽"
        vice_mark = " (вице)" if p['is_vice_captain'] else ""
        button_text = f"{emoji} {p['name']} ({p['team_name']}){vice_mark}"

        print(f"Создаю кнопку: {button_text} с callback_data=set_vice_{p['utp_id']}")

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"set_vice_{p['utp_id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='captain_back')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "\n".join(lines),
        parse_mode='Markdown',
        reply_markup=reply_markup
    )