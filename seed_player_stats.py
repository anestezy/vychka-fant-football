"""
Загрузка тестовой статистики игроков за матчи
"""
from db_connection import Database
import random

random.seed(42)  # Для воспроизводимости


def generate_player_stats():
    """
    Генерируем статистику для 50 матчей
    Каждый матч: 22 игрока (11 основных + запасные)
    """

    # Получаем всех игроков
    players = Database.execute_query(
        "SELECT id, position, current_team_id FROM real_players", fetch=True
    )

    # Получаем все матчи
    fixtures = Database.execute_query(
        "SELECT id, matchday, season, home_team_id, away_team_id, status FROM fixtures",
        fetch=True
    )

    stats = []
    stat_id = 1

    for fixture in fixtures:
        if fixture['status'] != 'FINISHED':
            continue  # Пропускаем незавершённые матчи

        match_id = fixture['id']
        gw = fixture['matchday']
        season = fixture['season']
        home_id = fixture['home_team_id']
        away_id = fixture['away_team_id']

        # Игроки домашней и гостевой команды
        home_players = [p for p in players if p['current_team_id'] == home_id][:16]
        away_players = [p for p in players if p['current_team_id'] == away_id][:16]

        match_players = home_players + away_players

        for player in match_players:
            # Генерируем случайную статистику
            minutes = random.choice([0, 0, 45, 60, 75, 90, 90])  # 0 минут = не играл
            goals = 0
            assists = 0
            clean_sheet = False
            goals_conceded = 0
            yellow = 0
            red = 0
            saves = 0

            if minutes > 0:
                # Вероятность гола зависит от позиции
                if player['position'] == 'FW':
                    goals = random.choices([0, 1, 2, 3], weights=[60, 25, 10, 5])[0]
                elif player['position'] == 'MF':
                    goals = random.choices([0, 1, 2], weights=[75, 20, 5])[0]
                elif player['position'] == 'DF':
                    goals = random.choices([0, 1], weights=[90, 10])[0]

                # Ассисты
                assists = random.choices([0, 1, 2], weights=[80, 15, 5])[0]

                # Карточки
                yellow = random.choices([0, 1], weights=[90, 10])[0]
                red = random.choices([0, 1], weights=[98, 2])[0]

                # Сухой матч (только для GK/DF)
                if player['position'] in ['GK', 'DF'] and minutes >= 60:
                    clean_sheet = random.choice([True, False])

                # Сейвы (только вратари)
                if player['position'] == 'GK':
                    saves = random.randint(0, 6) * 3  # Кратно 3 для FPL

                # Пропущенные голы
                if player['position'] in ['GK', 'DF'] and minutes >= 60:
                    goals_conceded = random.randint(0, 3)

            # Считаем fantasy points по формуле FPL
            points = calculate_fpl_points(
                player['position'], minutes, goals, assists,
                clean_sheet, goals_conceded, saves, yellow, red
            )

            stats.append((
                stat_id, player['id'], match_id, gw, season,
                minutes, goals, assists, clean_sheet, goals_conceded,
                0, 0, 0, yellow, red, saves, 0, points
            ))
            stat_id += 1

    return stats


def calculate_fpl_points(position, minutes, goals, assists, clean_sheet, goals_conceded, saves, yellow, red):
    """Формула подсчёта очков FPL"""
    points = 0

    # Минуты
    if minutes >= 60:
        points += 2
    elif minutes > 0:
        points += 1

    # Голы
    goal_points = {'GK': 6, 'DF': 6, 'MF': 5, 'FW': 4}
    points += goals * goal_points.get(position, 4)

    # Ассисты
    points += assists * 3

    # Сухой матч
    if clean_sheet and minutes >= 60:
        if position in ['GK', 'DF']:
            points += 4
        elif position == 'MF':
            points += 1

    # Сейвы (вратари)
    if position == 'GK':
        points += (saves // 3)

    # Пропущенные (GK/DF)
    if position in ['GK', 'DF'] and minutes >= 60:
        points += (goals_conceded // 2) * -1

    # Карточки
    points += yellow * -1
    points += red * -3

    return points


def insert_stats():
    stats = generate_player_stats()

    query = """
        INSERT INTO player_stats 
        (id, player_id, fixture_id, gameweek, season, minutes_played, goals, assists,
         clean_sheet, goals_conceded, own_goals, penalties_saved, penalties_missed,
         yellow_cards, red_cards, saves, bonus_points, fantasy_points)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        minutes_played=VALUES(minutes_played), goals=VALUES(goals),
        assists=VALUES(assists), fantasy_points=VALUES(fantasy_points)
    """

    Database.execute_many(query, stats)
    print(f"✅ Статистики загружено: {len(stats)} записей")


def main():
    print("🚀 Генерация статистики игроков...")
    insert_stats()
    print("🎉 Готово!")


if __name__ == '__main__':
    main()