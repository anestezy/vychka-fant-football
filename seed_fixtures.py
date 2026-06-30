"""
Загрузка 50 матчей в разных сезонах и датах
"""
from db_connection import Database

# Матчи в 3 сезонах: 2023/24, 2024/25, 2025/26
# Разные даты: январь, август, декабрь — для тестирования фильтров

FIXTURES = []

# ═══════════════════════════════════════
# СЕЗОН 2023/2024 (15 матчей)
# ═══════════════════════════════════════

# Январь 2024 (зимний период)
FIXTURES.extend([
    {'id': 1, 'matchday': 18, 'season': '2023/2024', 'home': 1, 'away': 2, 'date': '2024-01-13 13:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 1, 'winner': 'HOME'},
    {'id': 2, 'matchday': 18, 'season': '2023/2024', 'home': 3, 'away': 4, 'date': '2024-01-13 15:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 3, 'matchday': 18, 'season': '2023/2024', 'home': 5, 'away': 6, 'date': '2024-01-13 18:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 2, 'winner': 'AWAY'},
    {'id': 4, 'matchday': 18, 'season': '2023/2024', 'home': 7, 'away': 8, 'date': '2024-01-14 14:00',
     'status': 'FINISHED', 'home_score': 3, 'away_score': 0, 'winner': 'HOME'},
    {'id': 5, 'matchday': 18, 'season': '2023/2024', 'home': 9, 'away': 10, 'date': '2024-01-14 16:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 2, 'winner': 'AWAY'},
])

# Февраль 2024
FIXTURES.extend([
    {'id': 6, 'matchday': 24, 'season': '2023/2024', 'home': 2, 'away': 1, 'date': '2024-02-10 13:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 7, 'matchday': 24, 'season': '2023/2024', 'home': 4, 'away': 3, 'date': '2024-02-10 15:30',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 0, 'winner': 'HOME'},
    {'id': 8, 'matchday': 24, 'season': '2023/2024', 'home': 6, 'away': 5, 'date': '2024-02-10 18:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 3, 'winner': 'AWAY'},
    {'id': 9, 'matchday': 24, 'season': '2023/2024', 'home': 8, 'away': 7, 'date': '2024-02-11 14:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 1, 'winner': 'AWAY'},
    {'id': 10, 'matchday': 24, 'season': '2023/2024', 'home': 10, 'away': 9, 'date': '2024-02-11 16:30',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 2, 'winner': 'DRAW'},
])

# Май 2024 (конец сезона)
FIXTURES.extend([
    {'id': 11, 'matchday': 37, 'season': '2023/2024', 'home': 1, 'away': 3, 'date': '2024-05-11 13:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 1, 'winner': 'HOME'},
    {'id': 12, 'matchday': 37, 'season': '2023/2024', 'home': 2, 'away': 5, 'date': '2024-05-11 15:30',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 0, 'winner': 'DRAW'},
    {'id': 13, 'matchday': 37, 'season': '2023/2024', 'home': 4, 'away': 7, 'date': '2024-05-11 18:00',
     'status': 'FINISHED', 'home_score': 3, 'away_score': 2, 'winner': 'HOME'},
    {'id': 14, 'matchday': 38, 'season': '2023/2024', 'home': 6, 'away': 9, 'date': '2024-05-19 16:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 15, 'matchday': 38, 'season': '2023/2024', 'home': 8, 'away': 10, 'date': '2024-05-19 16:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 0, 'winner': 'HOME'},
])

# ═══════════════════════════════════════
# СЕЗОН 2024/2025 (20 матчей)
# ═══════════════════════════════════════

# Август 2024 (начало сезона)
FIXTURES.extend([
    {'id': 16, 'matchday': 1, 'season': '2024/2025', 'home': 1, 'away': 2, 'date': '2024-08-17 13:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 0, 'winner': 'HOME'},
    {'id': 17, 'matchday': 1, 'season': '2024/2025', 'home': 3, 'away': 4, 'date': '2024-08-17 15:30',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 2, 'winner': 'DRAW'},
    {'id': 18, 'matchday': 1, 'season': '2024/2025', 'home': 5, 'away': 6, 'date': '2024-08-17 18:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 1, 'winner': 'AWAY'},
    {'id': 19, 'matchday': 1, 'season': '2024/2025', 'home': 7, 'away': 8, 'date': '2024-08-18 14:00',
     'status': 'FINISHED', 'home_score': 3, 'away_score': 1, 'winner': 'HOME'},
    {'id': 20, 'matchday': 1, 'season': '2024/2025', 'home': 9, 'away': 10, 'date': '2024-08-18 16:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 2, 'winner': 'AWAY'},
])

# Октябрь 2024
FIXTURES.extend([
    {'id': 21, 'matchday': 8, 'season': '2024/2025', 'home': 2, 'away': 3, 'date': '2024-10-05 13:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 2, 'winner': 'DRAW'},
    {'id': 22, 'matchday': 8, 'season': '2024/2025', 'home': 4, 'away': 5, 'date': '2024-10-05 15:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 0, 'winner': 'HOME'},
    {'id': 23, 'matchday': 8, 'season': '2024/2025', 'home': 6, 'away': 7, 'date': '2024-10-05 18:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 3, 'winner': 'AWAY'},
    {'id': 24, 'matchday': 8, 'season': '2024/2025', 'home': 8, 'away': 9, 'date': '2024-10-06 14:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 1, 'winner': 'HOME'},
    {'id': 25, 'matchday': 8, 'season': '2024/2025', 'home': 10, 'away': 1, 'date': '2024-10-06 16:30',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 2, 'winner': 'AWAY'},
])

# Декабрь 2024
FIXTURES.extend([
    {'id': 26, 'matchday': 16, 'season': '2024/2025', 'home': 1, 'away': 4, 'date': '2024-12-14 13:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 1, 'winner': 'HOME'},
    {'id': 27, 'matchday': 16, 'season': '2024/2025', 'home': 2, 'away': 6, 'date': '2024-12-14 15:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 28, 'matchday': 16, 'season': '2024/2025', 'home': 3, 'away': 8, 'date': '2024-12-14 18:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 1, 'winner': 'AWAY'},
    {'id': 29, 'matchday': 16, 'season': '2024/2025', 'home': 5, 'away': 9, 'date': '2024-12-15 14:00',
     'status': 'FINISHED', 'home_score': 3, 'away_score': 0, 'winner': 'HOME'},
    {'id': 30, 'matchday': 16, 'season': '2024/2025', 'home': 7, 'away': 10, 'date': '2024-12-15 16:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 2, 'winner': 'AWAY'},
])

# Март 2025
FIXTURES.extend([
    {'id': 31, 'matchday': 28, 'season': '2024/2025', 'home': 4, 'away': 1, 'date': '2025-03-08 13:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 3, 'winner': 'AWAY'},
    {'id': 32, 'matchday': 28, 'season': '2024/2025', 'home': 6, 'away': 2, 'date': '2025-03-08 15:30',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 0, 'winner': 'HOME'},
    {'id': 33, 'matchday': 28, 'season': '2024/2025', 'home': 8, 'away': 3, 'date': '2025-03-08 18:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 34, 'matchday': 28, 'season': '2024/2025', 'home': 9, 'away': 5, 'date': '2025-03-09 14:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 2, 'winner': 'AWAY'},
    {'id': 35, 'matchday': 28, 'season': '2024/2025', 'home': 10, 'away': 7, 'date': '2025-03-09 16:30',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 2, 'winner': 'DRAW'},
])

# Май 2025 (конец сезона)
FIXTURES.extend([
    {'id': 36, 'matchday': 37, 'season': '2024/2025', 'home': 1, 'away': 5, 'date': '2025-05-10 13:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 1, 'winner': 'HOME'},
    {'id': 37, 'matchday': 37, 'season': '2024/2025', 'home': 2, 'away': 7, 'date': '2025-05-10 15:30',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 0, 'winner': 'DRAW'},
    {'id': 38, 'matchday': 37, 'season': '2024/2025', 'home': 3, 'away': 9, 'date': '2025-05-10 18:00',
     'status': 'FINISHED', 'home_score': 3, 'away_score': 2, 'winner': 'HOME'},
    {'id': 39, 'matchday': 38, 'season': '2024/2025', 'home': 4, 'away': 10, 'date': '2025-05-18 16:00',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 40, 'matchday': 38, 'season': '2024/2025', 'home': 6, 'away': 8, 'date': '2025-05-18 16:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 0, 'winner': 'HOME'},
])

# ═══════════════════════════════════════
# СЕЗОН 2025/2026 (15 матчей)
# ═══════════════════════════════════════

# Август 2025 (текущий сезон)
FIXTURES.extend([
    {'id': 41, 'matchday': 1, 'season': '2025/2026', 'home': 1, 'away': 2, 'date': '2025-08-16 13:00',
     'status': 'FINISHED', 'home_score': 2, 'away_score': 1, 'winner': 'HOME'},
    {'id': 42, 'matchday': 1, 'season': '2025/2026', 'home': 3, 'away': 4, 'date': '2025-08-16 15:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 1, 'winner': 'DRAW'},
    {'id': 43, 'matchday': 1, 'season': '2025/2026', 'home': 5, 'away': 6, 'date': '2025-08-16 18:00',
     'status': 'FINISHED', 'home_score': 0, 'away_score': 2, 'winner': 'AWAY'},
    {'id': 44, 'matchday': 1, 'season': '2025/2026', 'home': 7, 'away': 8, 'date': '2025-08-17 14:00',
     'status': 'FINISHED', 'home_score': 3, 'away_score': 0, 'winner': 'HOME'},
    {'id': 45, 'matchday': 1, 'season': '2025/2026', 'home': 9, 'away': 10, 'date': '2025-08-17 16:30',
     'status': 'FINISHED', 'home_score': 1, 'away_score': 2, 'winner': 'AWAY'},
])

# Сентябрь 2025 (текущий, будущие матчи)
FIXTURES.extend([
    {'id': 46, 'matchday': 5, 'season': '2025/2026', 'home': 2, 'away': 1, 'date': '2025-09-20 13:00',
     'status': 'SCHEDULED', 'home_score': None, 'away_score': None, 'winner': None},
    {'id': 47, 'matchday': 5, 'season': '2025/2026', 'home': 4, 'away': 3, 'date': '2025-09-20 15:30',
     'status': 'SCHEDULED', 'home_score': None, 'away_score': None, 'winner': None},
    {'id': 48, 'matchday': 5, 'season': '2025/2026', 'home': 6, 'away': 5, 'date': '2025-09-20 18:00',
     'status': 'SCHEDULED', 'home_score': None, 'away_score': None, 'winner': None},
    {'id': 49, 'matchday': 5, 'season': '2025/2026', 'home': 8, 'away': 7, 'date': '2025-09-21 14:00',
     'status': 'SCHEDULED', 'home_score': None, 'away_score': None, 'winner': None},
    {'id': 50, 'matchday': 5, 'season': '2025/2026', 'home': 10, 'away': 9, 'date': '2025-09-21 16:30',
     'status': 'SCHEDULED', 'home_score': None, 'away_score': None, 'winner': None},
])


def insert_fixtures():
    query = """
        INSERT INTO fixtures 
        (id, matchday, season, home_team_id, away_team_id, match_date, status, home_score, away_score, winner)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        match_date=VALUES(match_date), status=VALUES(status),
        home_score=VALUES(home_score), away_score=VALUES(away_score), winner=VALUES(winner)
    """
    params = []
    for f in FIXTURES:
        params.append((
            f['id'], f['matchday'], f['season'], f['home'], f['away'],
            f['date'], f['status'], f['home_score'], f['away_score'], f['winner']
        ))

    Database.execute_many(query, params)
    print(f"✅ Матчей загружено: {len(FIXTURES)}")

    # Статистика по сезонам
    stats = Database.execute_query(
        "SELECT season, COUNT(*) as cnt, status FROM fixtures GROUP BY season, status ORDER BY season",
        fetch=True
    )
    print("\n📊 Распределение по сезонам:")
    for row in stats:
        print(f"  {row['season']} | {row['status']}: {row['cnt']} матчей")


def main():
    print("🚀 Загрузка матчей в разных сезонах...")
    insert_fixtures()
    print("\n🎉 Готово!")


if __name__ == '__main__':
    main()