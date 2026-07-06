
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from db_connection import Database
from utils.formatting import format_budget, format_player_card
from config import POSITION_EMOJI, MAX_PLAYERS_IN_TEAM, MAX_STARTING_PLAYERS


async def show_team(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
    total_points = user_record[0]['total_points']
    team_record = Database.execute_query(
        "SELECT id, team_name, formation, gameweek, season FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        await update.message.reply_text("❌ Команда не найдена. Обратись к администратору.")
        return

    team = team_record[0]
    players = Database.execute_query(
        """
        SELECT 
            utp.id as utp_id,
            utp.is_captain,
            utp.is_vice_captain,
            utp.is_starting,
            utp.purchase_price,
            rp.id as player_id,
            rp.name,
            rp.position,
            rp.total_points,
            rp.price,
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
            utp.is_starting DESC,
            rp.total_points DESC
        """,
        params=(team['id'],),
        fetch=True
    )
    players_count = len(players)
    starting_count = sum(1 for p in players if p['is_starting'])

    lines = [
        f"⚽ *{team['team_name']}*",
        f"📐 Схема: {team['formation']} | 🎮 GW: {team['gameweek']} ({team['season']})",
        f"👥 Игроков: {players_count}/{MAX_PLAYERS_IN_TEAM} (стартовых: {starting_count}/{MAX_STARTING_PLAYERS})",
        f"⭐ Всего очков: {total_points}",
        format_budget(budget),
        "",
        "═" * 35,
    ]

    if not players:
        lines.append("\n⚠️ Состав пустой. Используй /shop чтобы набрать игроков!")
    else:
        current_position = None
        for p in players:
            if p['position'] != current_position:
                current_position = p['position']
                emoji = POSITION_EMOJI.get(current_position, '⚽')
                position_names = {'GK': 'Вратари', 'DF': 'Защитники', 'MF': 'Полузащитники', 'FW': 'Нападающие'}
                lines.append(f"\n{emoji} *{position_names.get(current_position, current_position)}:*")

            captain_mark = " 👑" if p['is_captain'] else ""
            vice_mark = " 🅥" if p['is_vice_captain'] else ""
            sub_mark = "" if p['is_starting'] else " 🪑"

            line = (
                f"  • {p['name']} ({p['team_name']}) — "
                f"{p['price']}M | ⭐{p['total_points']}{captain_mark}{vice_mark}{sub_mark}"
            )
            lines.append(line)

    message = "\n".join(lines)
    keyboard = [
        [
            InlineKeyboardButton("🛒 Магазин", callback_data='go_shop'),
            InlineKeyboardButton("🔄 Трансферы", callback_data='go_transfers'),
        ],
        [
            InlineKeyboardButton("👑 Назначить капитана", callback_data='go_captain'),
            InlineKeyboardButton("🪑 Скамейка", callback_data='go_sitting'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    telegram_id = user.id
    user_record = Database.execute_query(
        "SELECT id, budget FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )

    if not user_record:
        if update.message:
            await update.message.reply_text("❌ Ты не зарегистрирован. Напиши /start")
        return

    budget = float(user_record[0]['budget'])
    keyboard = [
        [
            InlineKeyboardButton("🧤 Вратари", callback_data='shop_pos_GK_1'),
            InlineKeyboardButton("️ Защитники", callback_data='shop_pos_DF_1'),
        ],
        [
            InlineKeyboardButton("⚙️ Полузащитники", callback_data='shop_pos_MF_1'),
            InlineKeyboardButton("⚽ Нападающие", callback_data='shop_pos_FW_1'),
        ],
        [InlineKeyboardButton("🌟 Все игроки", callback_data='shop_pos_ALL_1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            f"🛒 *Магазин игроков*\n\n"
            f"{format_budget(budget)}\n\n"
            f"Выбери категорию для просмотра:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


async def shop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = update.effective_user
    telegram_id = user.id
    data = query.data
    user_record = Database.execute_query(
        "SELECT id, budget FROM users WHERE telegram_id = %s",
        params=(telegram_id,),
        fetch=True
    )
    if not user_record:
        await query.edit_message_text("❌ Пользователь не найден")
        return

    user_id = user_record[0]['id']
    budget = float(user_record[0]['budget'])
    if data == 'go_shop':
        await query.message.delete()
        from unittest.mock import MagicMock
        fake_update = MagicMock()
        fake_update.message = query.message
        fake_update.effective_user = user
        await show_shop(fake_update, context)
        return

    if data == 'go_team':
        await query.message.delete()
        from unittest.mock import MagicMock
        fake_update = MagicMock()
        fake_update.message = query.message
        fake_update.effective_user = user
        from handlers.team import show_team
        await show_team(fake_update, context)
        return

    if data == 'shop_back_categories':
        keyboard = [
            [
                InlineKeyboardButton("🧤 Вратари", callback_data='shop_pos_GK_1'),
                InlineKeyboardButton("️ Защитники", callback_data='shop_pos_DF_1'),
            ],
            [
                InlineKeyboardButton("⚙️ Полузащитники", callback_data='shop_pos_MF_1'),
                InlineKeyboardButton("⚽ Нападающие", callback_data='shop_pos_FW_1'),
            ],
            [InlineKeyboardButton("🌟 Все игроки", callback_data='shop_pos_ALL_1')],
            [InlineKeyboardButton("🏠 К составу", callback_data='go_team')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🛒 *Магазин игроков*\n\n"
            f"{format_budget(budget)}\n\n"
            f"Выбери категорию для просмотра:",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return

    if data == 'shop_current':
        return
    if data.startswith('buy_'):
        player_id = int(data.replace('buy_', ''))
        await _buy_player(query, user_id, player_id, budget, context)
        return
    if data.startswith('shop_pos_'):
        parts = data.replace('shop_pos_', '').split('_')
        position = parts[0]
        page = int(parts[1]) if len(parts) > 1 else 1

        await _show_players_by_position(query, user_id, budget, position, page, context)
        return

    await query.edit_message_text("❓ Неизвестное действие")


async def _show_players_by_position(query, user_id, budget, position, page, context):
    PLAYERS_PER_PAGE = 20
    if position == 'ALL':
        all_players = Database.execute_query(
            """
            SELECT rp.id, rp.name, rp.position, rp.price, rp.total_points, rp.form,
                   rt.short_name as team_name
            FROM real_players rp
            JOIN real_teams rt ON rp.current_team_id = rt.id
            ORDER BY rp.total_points DESC
            """,
            fetch=True
        )
        title = "🌟 Все игроки"
    else:
        all_players = Database.execute_query(
            """
            SELECT rp.id, rp.name, rp.position, rp.price, rp.total_points, rp.form,
                   rt.short_name as team_name
            FROM real_players rp
            JOIN real_teams rt ON rp.current_team_id = rt.id
            WHERE rp.position = %s
            ORDER BY rp.total_points DESC
            """,
            params=(position,),
            fetch=True
        )
        position_names = {'GK': '🧤 Вратари', 'DF': '️ Защитники',
                          'MF': '⚙️ Полузащитники', 'FW': '⚽ Нападающие'}
        title = f"{position_names.get(position, position)}"
    total_pages = (len(all_players) + PLAYERS_PER_PAGE - 1) // PLAYERS_PER_PAGE
    start_idx = (page - 1) * PLAYERS_PER_PAGE
    end_idx = start_idx + PLAYERS_PER_PAGE
    players = all_players[start_idx:end_idx]

    if not players:
        await query.edit_message_text("⚠️ Игроки не найдены")
        return

    lines = [f"*{title} (Стр. {page}/{total_pages})*\n", f"{format_budget(budget)}\n", "═" * 35]

    keyboard = []
    for p in players:
        emoji = POSITION_EMOJI.get(p['position'], '⚽')
        can_buy = budget >= float(p['price'])
        price_mark = "✅" if can_buy else "❌"

        line = (
            f"{emoji} *{p['name']}* ({p['team_name']}) — "
            f"{p['price']}M | ⭐{p['total_points']} {price_mark}"
        )
        lines.append(line)

        if can_buy:
            keyboard.append([
                InlineKeyboardButton(
                    f"Купить: {p['name']}",
                    callback_data=f"buy_{p['id']}"
                )
            ])
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f'shop_pos_{position}_{page - 1}'))

    nav_buttons.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data='shop_current'))

    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Вперёд ➡️", callback_data=f'shop_pos_{position}_{page + 1}'))

    keyboard.append(nav_buttons)
    keyboard.append([
        InlineKeyboardButton("🔙 Назад к категориям", callback_data='shop_back_categories'),
        InlineKeyboardButton("🏠 К составу", callback_data='go_team')
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = "\n".join(lines)

    if len(message) > 4000:
        message = message[:3950] + "\n\n... (список обрезан)"

    await query.edit_message_text(
        message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )


async def _buy_player(query, user_id, player_id, budget, context):
    player = Database.execute_query(
        "SELECT id, name, position, price FROM real_players WHERE id = %s",
        params=(player_id,),
        fetch=True
    )

    if not player:
        await query.edit_message_text("❌ Игрок не найден")
        return

    player = player[0]
    player_price = float(player['price'])
    if float(budget) < player_price:
        await query.edit_message_text(
            f"💸 Недостаточно денег!\n"
            f"Цена: {player_price}M | У тебя: {budget:.2f}M"
        )
        return
    team = Database.execute_query(
        "SELECT id FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team:
        await query.edit_message_text("❌ Команда не найдена")
        return

    team_id = team[0]['id']
    current_count = Database.execute_query(
        "SELECT COUNT(*) as cnt FROM user_team_players WHERE user_team_id = %s",
        params=(team_id,),
        fetch=True
    )

    if current_count[0]['cnt'] >= MAX_PLAYERS_IN_TEAM:
        await query.edit_message_text(
            f"⚠️ Лимит игроков ({MAX_PLAYERS_IN_TEAM})! "
            "Продай кого-нибудь через /transfers"
        )
        return
    already_has = Database.execute_query(
        "SELECT id FROM user_team_players WHERE user_team_id = %s AND player_id = %s",
        params=(team_id, player_id),
        fetch=True
    )

    if already_has:
        await query.edit_message_text(f"⚠️ {player['name']} уже в твоей команде!")
        return

    try:
        starting_count = Database.execute_query(
            "SELECT COUNT(*) as cnt FROM user_team_players WHERE user_team_id = %s AND is_starting = 1",
            params=(team_id,),
            fetch=True
        )[0]['cnt']
        is_starting = 1 if starting_count < MAX_STARTING_PLAYERS else 0
        Database.execute_query(
            """
            INSERT INTO user_team_players 
            (user_team_id, player_id, is_starting, is_captain, is_vice_captain, purchase_price)
            VALUES (%s, %s, %s, 0, 0, %s)
            """,
            params=(team_id, player_id, is_starting, player_price)
        )
        Database.execute_query(
            "UPDATE users SET budget = budget - %s WHERE id = %s",
            params=(player_price, user_id)
        )

        new_budget = float(budget) - player_price
        role = "стартовый" if is_starting else "скамейка"
        keyboard = [
            [InlineKeyboardButton("🔙 Продолжить покупки", callback_data='shop_back_categories')],
            [InlineKeyboardButton("🏠 К составу", callback_data='go_team')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"✅ *{player['name']}* куплен!\n"
            f"💰 Цена: {player_price}M\n"
            f"👤 Роль: {role}\n\n"
            f"{format_budget(new_budget)}",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    except Exception as e:
        await query.edit_message_text(f"❌ Ошибка покупки: {e}")