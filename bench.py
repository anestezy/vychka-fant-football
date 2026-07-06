
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db_connection import Database
from utils.formatting import POSITION_EMOJI
import logging

logger = logging.getLogger(__name__)


async def show_sitting(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    telegram_id = user.id

    logger.info(f"🔍 show_sitting вызван для user_id={telegram_id}")
    user_record = Database.execute_query(
        "SELECT id FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )

    if not user_record:
        if update.message:
            await update.message.reply_text("❌ Ты не зарегистрирован. Напиши /start")
        return

    user_id = user_record[0]['id']
    team_record = Database.execute_query(
        "SELECT id FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        if update.message:
            await update.message.reply_text("❌ Команда не найдена")
        return

    team_id = team_record[0]['id']
    bench_players = Database.execute_query(
        """
        SELECT 
            utp.id as utp_id,
            rp.id as player_id,
            rp.name,
            rp.position,
            rp.price,
            rp.total_points,
            rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = %s AND utp.is_starting = 0
        ORDER BY 
            CASE rp.position 
                WHEN 'GK' THEN 1 
                WHEN 'DF' THEN 2 
                WHEN 'MF' THEN 3 
                WHEN 'FW' THEN 4 
            END,
            rp.total_points DESC
        """,
        params=(team_id,),
        fetch=True
    )

    if not bench_players:
        if update.message:
            await update.message.reply_text(
                "🪑 *Скамейка пуста!*\n\n"
                "У тебя нет игроков на скамейке запасных.",
                parse_mode='Markdown'
            )
        return
    lines = [
        "🪑 *Игроки на скамейке*\n",
        "Кого бы ты хотел выпустить в поле?\n",
        "═" * 35,
    ]

    keyboard = []
    for p in bench_players:
        emoji = POSITION_EMOJI.get(p['position'], '⚽')
        line = f"{emoji} *{p['name']}* ({p['team_name']}) — {p['price']}M | ⭐{p['total_points']}"
        lines.append(line)

        keyboard.append([
            InlineKeyboardButton(
                f"🔄 Выпустить: {p['name']}",
                callback_data=f'bench_out_{p["utp_id"]}_{p["player_id"]}'
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='bench_back')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    message = "\n".join(lines)

    if update.message:
        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


async def bench_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logger.info(f"🔍 bench_callback вызван!")
    logger.info(f"🔍 data: {query.data}")

    user = update.effective_user
    data = query.data
    if data == 'bench_back':
        logger.info("🔍 Переход назад к составу")
        await query.message.delete()
        from unittest.mock import MagicMock
        fake_update = MagicMock()
        fake_update.message = query.message
        fake_update.effective_user = user
        from handlers.team import show_team
        await show_team(fake_update, context)
        return
    if data.startswith('bench_out_'):
        parts = data.replace('bench_out_', '').split('_')
        utp_id = int(parts[0])
        player_id = int(parts[1])

        logger.info(f"🔍 Выбор игрока со скамейки: utp_id={utp_id}, player_id={player_id}")
        player = Database.execute_query(
            "SELECT name, position FROM real_players WHERE id = %s",
            params=(player_id,),
            fetch=True
        )

        if not player:
            await query.edit_message_text("❌ Ошибка: игрок не найден")
            return

        player_name = player[0]['name']
        context.user_data['bench_player_utp_id'] = utp_id
        context.user_data['bench_player_name'] = player_name
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
        starting_players = Database.execute_query(
            """
            SELECT 
                utp.id as utp_id,
                rp.id as player_id,
                rp.name,
                rp.position,
                rp.price,
                rp.total_points,
                rt.short_name as team_name
            FROM user_team_players utp
            JOIN real_players rp ON utp.player_id = rp.id
            JOIN real_teams rt ON rp.current_team_id = rt.id
            WHERE utp.user_team_id = %s AND utp.is_starting = 1
            ORDER BY 
                CASE rp.position 
                    WHEN 'GK' THEN 1 
                    WHEN 'DF' THEN 2 
                    WHEN 'MF' THEN 3 
                    WHEN 'FW' THEN 4 
                END,
                rp.total_points DESC
            """,
            params=(team_id,),
            fetch=True
        )

        if not starting_players:
            await query.edit_message_text("❌ Ошибка: нет игроков в старте")
            return
        lines = [
            f"✅ *{player_name}* будет выпущен на поле!\n",
            "═" * 35,
            "🔄 *Кого посадить на скамейку?*\n",
            "Выбери одного из основных игроков:\n",
        ]

        keyboard = []
        for p in starting_players:
            emoji = POSITION_EMOJI.get(p['position'], '⚽')
            line = f"{emoji} *{p['name']}* ({p['team_name']}) — {p['price']}M | ⭐{p['total_points']}"
            lines.append(line)

            keyboard.append([
                InlineKeyboardButton(
                    f"🪑 Посадить: {p['name']}",
                    callback_data=f'bench_in_{p["utp_id"]}_{p["player_id"]}'
                )
            ])

        keyboard.append([
            InlineKeyboardButton("⬅️ Отмена", callback_data='bench_back')
        ])

        reply_markup = InlineKeyboardMarkup(keyboard)
        message = "\n".join(lines)

        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return
    if data.startswith('bench_in_'):
        parts = data.replace('bench_in_', '').split('_')
        starting_utp_id = int(parts[0])
        starting_player_id = int(parts[1])

        logger.info(f"🔍 Подтверждение замены: starting_utp_id={starting_utp_id}")
        player = Database.execute_query(
            "SELECT name FROM real_players WHERE id = %s",
            params=(starting_player_id,),
            fetch=True
        )

        if not player:
            await query.edit_message_text("❌ Ошибка: игрок не найден")
            return

        starting_player_name = player[0]['name']
        bench_player_name = context.user_data.get('bench_player_name', 'Игрок')
        bench_utp_id = context.user_data.get('bench_player_utp_id')

        if not bench_utp_id:
            await query.edit_message_text("❌ Ошибка: данные не сохранены. Начни заново.")
            return
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

        try:
            Database.execute_query(
                "UPDATE user_team_players SET is_starting = 1 WHERE id = %s",
                params=(bench_utp_id,)
            )
            Database.execute_query(
                "UPDATE user_team_players SET is_starting = 0 WHERE id = %s",
                params=(starting_utp_id,)
            )
            Database.execute_query(
                """UPDATE user_team_players 
                   SET is_captain = 0, is_vice_captain = 0 
                   WHERE id = %s AND (is_captain = 1 OR is_vice_captain = 1)""",
                params=(starting_utp_id,)
            )
            context.user_data.clear()

            await query.edit_message_text(
                f"✅ *Замена выполнена!*\n\n"
                f"🔄 *{bench_player_name}* вышел в стартовый состав\n"
                f"🪑 *{starting_player_name}* сел на скамейку\n\n"
                f"Состав команды обновлён!",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 К составу", callback_data='bench_back')
                ]])
            )

        except Exception as e:
            logger.error(f"❌ Ошибка при замене: {e}")
            await query.edit_message_text(f"❌ Ошибка при замене: {e}")