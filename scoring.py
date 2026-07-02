
from config import (
    FPL_GOAL_POINTS, FPL_ASSIST_POINTS, FPL_CLEAN_SHEET_GK_DF,
    FPL_CLEAN_SHEET_MF, FPL_SAVE_POINTS, FPL_GOALS_CONCEDED_PENALTY,
    FPL_YELLOW_CARD_PENALTY, FPL_RED_CARD_PENALTY,
    FPL_MINUTES_60_PLUS, FPL_MINUTES_LESS_60,
    CAPTAIN_MULTIPLIER, VICE_CAPTAIN_MULTIPLIER,
    BONUS_REWARDS
)


def calculate_fpl_points(position, minutes, goals, assists, clean_sheet,
                         goals_conceded, saves, yellow_cards, red_cards):

    points = 0

    if minutes >= 60:
        points += FPL_MINUTES_60_PLUS
    elif minutes > 0:
        points += FPL_MINUTES_LESS_60

    points += goals * FPL_GOAL_POINTS.get(position, 4)

    points += assists * FPL_ASSIST_POINTS

    if clean_sheet and minutes >= 60:
        if position in ['GK', 'DF']:
            points += FPL_CLEAN_SHEET_GK_DF
        elif position == 'MF':
            points += FPL_CLEAN_SHEET_MF

    if position == 'GK':
        points += saves // FPL_SAVE_POINTS

    if position in ['GK', 'DF'] and minutes >= 60:
        points -= (goals_conceded // FPL_GOALS_CONCEDED_PENALTY)

    points -= yellow_cards * FPL_YELLOW_CARD_PENALTY
    points -= red_cards * FPL_RED_CARD_PENALTY

    return max(0, points)


def apply_captain_multiplier(points, is_captain=False, is_vice_captain=False):

    if is_captain:
        return points * CAPTAIN_MULTIPLIER
    elif is_vice_captain:
        return points * VICE_CAPTAIN_MULTIPLIER
    return points


def calculate_team_points_with_bonuses(team_players_stats):

    sorted_players = sorted(
        team_players_stats,
        key=lambda x: x.get('fantasy_points', 0),
        reverse=True
    )

    bonus_details = {}
    for rank, player in enumerate(sorted_players[:3], start=1):
        bonus = BONUS_REWARDS.get(rank, 0)
        bonus_details[player['player_id']] = {
            'rank': rank,
            'bonus': bonus,
            'player_name': player['player_name']
        }

    total_points = 0
    player_rankings = []

    for rank, player in enumerate(sorted_players, start=1):
        base_points = player.get('fantasy_points', 0)
        player_id = player['player_id']

        bonus = bonus_details.get(player_id, {}).get('bonus', 0)
        points_with_bonus = base_points + bonus

        is_captain = player.get('is_captain', False)
        is_vice_captain = player.get('is_vice_captain', False)

        if is_captain and player.get('minutes_played', 0) == 0:
            is_captain = False
            for other in sorted_players:
                if other.get('is_vice_captain') and other.get('minutes_played', 0) > 0:
                    other['is_captain'] = True
                    break

        final_points = apply_captain_multiplier(
            points_with_bonus, is_captain, is_vice_captain
        )

        total_points += final_points

        player_rankings.append({
            'rank': rank,
            'player_id': player_id,
            'player_name': player['player_name'],
            'position': player['position'],
            'base_points': base_points,
            'bonus': bonus,
            'points_with_bonus': points_with_bonus,
            'is_captain': is_captain,
            'is_vice_captain': is_vice_captain,
            'final_points': final_points
        })

    return {
        'total_points': total_points,
        'player_rankings': player_rankings,
        'bonus_details': bonus_details
    }


def calculate_player_gameweek_points(player_id, gameweek, season='2025/2026'):

    from db_connection import Database

    query = """
        SELECT ps.*, rp.name, rp.position, rp.current_team_id, rt.short_name as team_name
        FROM player_stats ps
        JOIN real_players rp ON ps.player_id = rp.id
        JOIN real_teams rt ON rp.current_team_id = rt.id
        WHERE ps.player_id = %s AND ps.gameweek = %s AND ps.season = %s
    """

    result = Database.execute_query(
        query,
        params=(player_id, gameweek, season),
        fetch=True
    )

    if result:
        return result[0]
    return None