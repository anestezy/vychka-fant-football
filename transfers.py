
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db_connection import Database
from utils.formatting import format_budget, POSITION_EMOJI
from config import MAX_TRANSFERS_PER_GW, TRANSFER_PENALTY, MAX_PLAYERS_IN_TEAM


async def show_transfers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    telegram_id = user.id
    user_record = Database.execute_query(
        "SELECT id, budget, total_points FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )

    if not user_record:
        await update.message.reply_text("❌ Ты не зарегистрирован. Напиши /start")
        return

    user_id = user_record[0]['id']
    budget = float(user_record[0]['budget'])
    team_record = Database.execute_query(
        "SELECT id, team_name, gameweek, transfers_made FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        await update.message.reply_text("❌ Команда не найдена")
        return

    team = team_record[0]
    team_id = team['id']
    transfers_made = team.get('transfers_made', 0) or 0
    transfers_left = MAX_TRANSFERS_PER_GW - transfers_made
    players = Database.execute_query(
        """
        SELECT 
            utp.id as utp_id,
            utp.is_captain,
            utp.is_vice_captain,
            utp.purchase_price,
            rp.id as player_id,
            rp.name,
            rp.position,
            rp.price as current_price,
            rt.short_name as team_name
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE utp.user_team_id = %s
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
    lines = [
        "🔄 *Трансферы*\n",
        f"⚽ Команда: *{team['team_name']}* | 🎮 GW: {team['gameweek']}",
        f"{format_budget(budget)}",
        "",
        f"🔁 Трансферов в этом GW: {transfers_made}/{MAX_TRANSFERS_PER_GW}",
    ]

    if transfers_left <= 0:
        lines.append(f"⚠️ Лимит бесплатных трансферов исчерпан!")
        lines.append(f"💸 Каждый следующий трансфер: -{TRANSFER_PENALTY} очка")

    lines.append("\n" + "═" * 35)
    lines.append("\n📋 *Выбери игрока для продажи:*")

    message = "\n".join(lines)
    keyboard = []
    for p in players:
        emoji = POSITION_EMOJI.get(p['position'], '⚽')
        captain_mark = " 👑" if p['is_captain'] else ""
        vice_mark = " 🅥" if p['is_vice_captain'] else ""
        profit = p['current_price'] - p['purchase_price']
        profit_mark = f" (+{profit:.1f}M)" if profit > 0 else (f" ({profit:.1f}M)" if profit < 0 else "")

        button_text = (
            f"{emoji} {p['name']} ({p['team_name']}) — "
            f"Возврат: {p['purchase_price']}M{profit_mark}{captain_mark}{vice_mark}"
        )

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"sell_{p['utp_id']}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton("⬅️ Назад к составу", callback_data='transfers_back')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def transfers_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if data == 'transfers_back':
        await query.message.delete()
        from unittest.mock import MagicMock
        fake_update = MagicMock()
        fake_update.message = query.message
        fake_update.effective_user = user
        from handlers.team import show_team
        await show_team(fake_update, context)
        return

    if data.startswith('sell_'):
        utp_id = int(data.replace('sell_', ''))
        await _sell_player(query, utp_id, context)
        return

    if data.startswith('confirm_sell_'):
        utp_id = int(data.replace('confirm_sell_', ''))
        await _confirm_sell(query, utp_id, context)
        return

    if data == 'cancel_sell':
        await query.edit_message_text("❌ Продажа отменена")
        return

    if data == 'skip_buy':
        await query.edit_message_text(
            "✅ Игрок продан. Не забудь добрать состав командой /shop!"
        )
        return


async def _sell_player(query, utp_id, context):
    player = Database.execute_query(
        """
        SELECT utp.*, rp.name, rp.position, rp.price as current_price,
               rt.short_name as team_name
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
    count_result = Database.execute_query(
        "SELECT COUNT(*) as cnt FROM user_team_players WHERE user_team_id = %s",
        params=(team_id,),
        fetch=True
    )
    current_count = count_result[0]['cnt']

    warning = ""
    if current_count <= 11:
        warning = (
            "\n\n⚠️ *ВНИМАНИЕ!* После продажи в команде останется "
            f"меньше 11 игроков. Нужно будет сразу купить замену!"
        )

    captain_warning = ""
    if player['is_captain']:
        captain_warning = "\n\n⚠️ Этот игрок — *капитан*. Капитанская повязка будет снята."
    elif player['is_vice_captain']:
        captain_warning = "\n\n⚠️ Этот игрок — *вице-капитан*. Повязка будет снята."

    profit = player['current_price'] - player['purchase_price']
    profit_text = ""
    if profit > 0:
        profit_text = f"\n💹 Прибыль: +{profit:.1f}M"
    elif profit < 0:
        profit_text = f"\n💸 Убыток: {profit:.1f}M"

    message = (
        f"🔄 *Продажа игрока*\n\n"
        f"⚽ {player['name']} ({player['team_name']})\n"
        f"📍 Позиция: {player['position']}\n"
        f"💰 Куплен за: {player['purchase_price']}M\n"
        f"💵 Текущая цена: {player['current_price']}M\n"
        f"💸 Возврат при продаже: {player['purchase_price']}M"
        f"{profit_text}{captain_warning}{warning}\n\n"
        f"Подтвердить продажу?"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_sell_{utp_id}"),
            InlineKeyboardButton("❌ Отмена", callback_data='cancel_sell'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def _confirm_sell(query, utp_id, context):
    player = Database.execute_query(
        """
        SELECT utp.*, rp.name, rp.position, rp.price as current_price,
               rt.short_name as team_name
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
    team_record = Database.execute_query(
        "SELECT user_id, gameweek, transfers_made FROM user_teams WHERE id = %s",
        params=(team_id,),
        fetch=True
    )
    if not team_record:
        await query.edit_message_text("❌ Команда не найдена")
        return

    team = team_record[0]
    user_id = team['user_id']
    transfers_made = team.get('transfers_made', 0) or 0
    penalty = 0
    if transfers_made >= MAX_TRANSFERS_PER_GW:
        penalty = TRANSFER_PENALTY

    try:
        if player['is_captain'] or player['is_vice_captain']:
            Database.execute_query(
                "UPDATE user_team_players SET is_captain = 0, is_vice_captain = 0 WHERE id = %s",
                params=(utp_id,)
            )
        if player['is_starting']:
            sub = Database.execute_query(
                """
                SELECT id FROM user_team_players 
                WHERE user_team_id = %s AND is_starting = 0 
                ORDER BY id LIMIT 1
                """,
                params=(team_id,),
                fetch=True
            )
            if sub:
                Database.execute_query(
                    "UPDATE user_team_players SET is_starting = 1 WHERE id = %s",
                    params=(sub[0]['id'],)
                )
        Database.execute_query(
            "DELETE FROM user_team_players WHERE id = %s",
            params=(utp_id,)
        )
        Database.execute_query(
            "UPDATE users SET budget = budget + %s WHERE id = %s",
            params=(player['purchase_price'], user_id)
        )
        Database.execute_query(
            "UPDATE user_teams SET transfers_made = transfers_made + 1 WHERE id = %s",
            params=(team_id,)
        )
        if penalty > 0:
            Database.execute_query(
                "UPDATE users SET total_points = total_points - %s WHERE id = %s",
                params=(penalty, user_id)
            )
        new_budget_record = Database.execute_query(
            "SELECT budget FROM users WHERE id = %s",
            params=(user_id,),
            fetch=True
        )
        new_budget = float(new_budget_record[0]['budget'])

        penalty_text = f"\n💸 Штраф за лишний трансфер: -{penalty} очка" if penalty > 0 else ""

        message = (
            f"✅ *{player['name']}* продан!\n"
            f"💰 Возврат: {player['purchase_price']}M\n"
            f"{format_budget(new_budget)}{penalty_text}\n\n"
            f"Теперь выбери нового игрока в /shop или нажми «Пропустить»."
        )
        keyboard = [
            [
                InlineKeyboardButton("🛒 Открыть магазин", callback_data='transfers_to_shop'),
                InlineKeyboardButton("⏭ Пропустить", callback_data='skip_buy'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка продажи: {e}")


async def transfers_to_shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    telegram_id = user.id

    user_record = Database.execute_query(
        "SELECT id, budget FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )
    if not user_record:
        await query.edit_message_text("❌ Пользователь не найден")
        return

    budget = float(user_record[0]['budget'])
    keyboard = [
        [
            InlineKeyboardButton("🧤 Вратари", callback_data='shop_pos_GK'),
            InlineKeyboardButton("️ Защитники", callback_data='shop_pos_DF'),
        ],
        [
            InlineKeyboardButton("⚙️ Полузащитники", callback_data='shop_pos_MF'),
            InlineKeyboardButton("⚽ Нападающие", callback_data='shop_pos_FW'),
        ],
        [InlineKeyboardButton("🌟 Все игроки", callback_data='shop_pos_ALL')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🛒 *Магазин игроков*\n\n"
        f"{format_budget(budget)}\n\n"
        f"Выбери категорию для просмотра:",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )