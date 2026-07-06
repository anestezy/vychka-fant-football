
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from telegram import Update
from telegram.ext import ContextTypes
from db_connection import Database
from utils.scoring import calculate_team_points_with_bonuses
from utils.formatting import format_leaderboard, POSITION_EMOJI
from config import CURRENT_SEASON


async def show_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
        "SELECT id, gameweek, season FROM user_teams WHERE user_id = %s",
        params=(user_id,),
        fetch=True
    )

    if not team_record:
        await update.message.reply_text("❌ Команда не найдена")
        return

    team = team_record[0]
    team_id = team['id']
    gameweek = team['gameweek']
    season = team['season']
    if context.args and len(context.args) > 0:
        try:
            arg = context.args[0]
            if arg.startswith('gw='):
                gameweek = int(arg.replace('gw=', ''))
            else:
                gameweek = int(arg)
        except ValueError:
            await update.message.reply_text(
                "⚠️ Неверный формат. Используй: /leaderboard gw=5"
            )
            return
    players_stats = Database.execute_query(
        """
        SELECT 
            utp.id as utp_id,
            utp.is_captain,
            utp.is_vice_captain,
            rp.id as player_id,
            rp.name,
            rp.position,
            COALESCE(SUM(ps.fantasy_points), 0) as fantasy_points,
            COALESCE(SUM(ps.minutes_played), 0) as minutes_played
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        LEFT JOIN player_stats ps ON rp.id = ps.player_id 
            AND ps.gameweek = %s 
            AND ps.season = %s
        WHERE utp.user_team_id = %s
        GROUP BY utp.id, rp.id, rp.name, rp.position, utp.is_captain, utp.is_vice_captain
        ORDER BY fantasy_points DESC
        """,
        params=(gameweek, season, team_id),
        fetch=True
    )

    if not players_stats:
        await update.message.reply_text(
            f"⚠️ В команде нет игроков для GW{gameweek}. "
            "Используй /shop чтобы набрать состав!"
        )
        return
    team_players_data = []
    for p in players_stats:
        team_players_data.append({
            'player_id': p['player_id'],
            'player_name': p['name'],
            'position': p['position'],
            'fantasy_points': p['fantasy_points'],
            'is_captain': bool(p['is_captain']),
            'is_vice_captain': bool(p['is_vice_captain']),
            'minutes_played': p['minutes_played']
        })
    result = calculate_team_points_with_bonuses(team_players_data)

    total_points = result['total_points']
    player_rankings = result['player_rankings']
    bonus_details = result['bonus_details']
    lines = [
        f"🏆 *Leaderboard Gameweek {gameweek}* ({season})\n",
        "═" * 40,
    ]
    for player in player_rankings:
        rank = player['rank']
        name = player['player_name']
        position = player['position']
        base = player['base_points']
        bonus = player['bonus']
        final = player['final_points']
        is_captain = player['is_captain']
        is_vice = player['is_vice_captain']
        if rank == 1:
            rank_emoji = "🥇"
        elif rank == 2:
            rank_emoji = "🥈"
        elif rank == 3:
            rank_emoji = "🥉"
        else:
            rank_emoji = f"{rank}."
        captain_mark = " 👑" if is_captain else ""
        vice_mark = " 🅥" if is_vice else ""
        bonus_text = f" +{bonus} bonus" if bonus > 0 else ""
        captain_multiplier = " ×2" if (is_captain or is_vice) and final > 0 else ""

        line = (
            f"{rank_emoji} {name}{captain_mark}{vice_mark} — "
            f"{base} pts{bonus_text}{captain_multiplier} = {final} pts"
        )
        lines.append(line)

    lines.append("\n" + "═" * 40)
    lines.append(f"\n💰 *Ваши очки за GW{gameweek}: {total_points} pts*")
    if bonus_details:
        lines.append("\n🎁 *Бонусы топ-3:*")
        for player_id, bonus_info in bonus_details.items():
            rank = bonus_info['rank']
            bonus = bonus_info['bonus']
            name = bonus_info['player_name']
            lines.append(f"  {rank}. {name}: +{bonus}")

    message = "\n".join(lines)
    if len(message) > 4000:
        message = message[:3950] + "\n\n... (сообщение обрезано)"

    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )


async def update_leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

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

    await update.message.reply_text(
        "🔄 Пересчёт очков...\n\n"
        "Бонусы топ-3 автоматически применяются при просмотре /leaderboard"
    )
    await show_leaderboard(update, context)