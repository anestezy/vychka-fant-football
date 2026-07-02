
from config import POSITION_EMOJI


def format_player_card(player, show_price=True, show_points=True):

    emoji = POSITION_EMOJI.get(player['position'], '⚽')
    team = player.get('team_name', player.get('short_name', '???'))

    parts = [f"{emoji} {player['name']} ({team})"]

    if show_price:
        price = player.get('price', 0)
        parts.append(f"💰 {price:.1f}M")

    if show_points:
        points = player.get('total_points', 0)
        parts.append(f"⭐ {points} pts")

    form = player.get('form', 0)
    if form:
        parts.append(f" {form}")

    return " | ".join(parts)


def format_team_lineup(team_players, team_name="Моя команда"):

    lines = [f"⚽ {team_name}\n"]

    gk = [p for p in team_players if p['position'] == 'GK']
    df = [p for p in team_players if p['position'] == 'DF']
    mf = [p for p in team_players if p['position'] == 'MF']
    fw = [p for p in team_players if p['position'] == 'FW']
    sub = [p for p in team_players if p['position'] == 'SUB']

    if gk:
        lines.append("🧤 Вратарь:")
        for p in gk:
            lines.append(format_player_lineup(p))

    if df:
        lines.append("\n️ Защитники:")
        for p in df:
            lines.append(format_player_lineup(p))

    if mf:
        lines.append("\n⚙️ Полузащитники:")
        for p in mf:
            lines.append(format_player_lineup(p))

    if fw:
        lines.append("\n⚽ Нападающие:")
        for p in fw:
            lines.append(format_player_lineup(p))

    if sub:
        lines.append("\n🪑 Скамейка:")
        for p in sub:
            lines.append(format_player_lineup(p, is_sub=True))

    return "\n".join(lines)


def format_player_lineup(player, is_sub=False):
    emoji = POSITION_EMOJI.get(player['position'], '⚽')
    captain_mark = " 👑" if player.get('is_captain') else ""
    vice_captain_mark = " 🅥" if player.get('is_vice_captain') else ""
    team = player.get('team_name', player.get('short_name', '???'))
    points = player.get('fantasy_points', 0)

    prefix = "  " if is_sub else ""
    return f"{prefix}{emoji} {player['player_name']} ({team}){captain_mark}{vice_captain_mark} - {points} pts"


def format_leaderboard(players_with_bonuses, gameweek, season):

    lines = [
        f"🏆 Leaderboard Gameweek {gameweek} ({season})\n",
        "═" * 40
    ]

    for player in players_with_bonuses:
        rank = player['rank']
        name = player['player_name']
        position = player['position']
        base = player['base_points']
        bonus = player['bonus']
        final = player['final_points']
        is_captain = player['is_captain']
        is_vice = player['is_vice_captain']

        if rank == 1:
            rank_emoji = ""
        elif rank == 2:
            rank_emoji = "🥈"
        elif rank == 3:
            rank_emoji = "🥉"
        else:
            rank_emoji = f"{rank}."

        captain_mark = " 👑" if is_captain else ""
        vice_mark = " 🅥" if is_vice else ""

        bonus_text = f" +{bonus} bonus" if bonus > 0 else ""

        line = f"{rank_emoji} {name}{captain_mark}{vice_mark} - {base} pts{bonus_text} = {final} pts"
        lines.append(line)

    return "\n".join(lines)


def format_stats_summary(stats, period_label):

    lines = [
        f"📊 Статистика за {period_label}\n",
        f"⭐ Всего очков: {stats['total_points']}",
        f"🎮 Матчей сыграно: {stats['matches_played']}",
        f"📈 Среднее за матч: {stats['avg_points']:.1f}",
    ]

    if stats.get('best_player'):
        lines.append(f" Лучший игрок: {stats['best_player']}")

    return "\n".join(lines)


def truncate_message(text, max_length=4096):

    if len(text) <= max_length:
        return text

    return text[:max_length - 50] + "\n\n... (сообщение обрезано)"


def format_budget(budget, max_budget=100.00):
    spent = max_budget - budget
    percentage = (budget / max_budget) * 100

    if percentage > 50:
        emoji = "💚"
    elif percentage > 20:
        emoji = "💛"
    else:
        emoji = "❤️"

    return f"{emoji} Бюджет: {budget:.2f}M / {max_budget:.2f}M (потрачено: {spent:.2f}M)"