
MAX_TEAM_BUDGET = 100.00
MAX_PLAYERS_IN_TEAM = 15
MAX_STARTING_PLAYERS = 11
MAX_SUBSTITUTES = 4

VALID_FORMATIONS = [
    '3-4-3', '3-5-2', '4-3-3',
    '4-4-2', '4-5-1', '5-3-2'
]

FORMATION_RULES = {
    '3-4-3': {'GK': 1, 'DF': 3, 'MF': 4, 'FW': 3},
    '3-5-2': {'GK': 1, 'DF': 3, 'MF': 5, 'FW': 2},
    '4-3-3': {'GK': 1, 'DF': 4, 'MF': 3, 'FW': 3},
    '4-4-2': {'GK': 1, 'DF': 4, 'MF': 4, 'FW': 2},
    '4-5-1': {'GK': 1, 'DF': 4, 'MF': 5, 'FW': 1},
    '5-3-2': {'GK': 1, 'DF': 5, 'MF': 3, 'FW': 2},
}

CAPTAIN_MULTIPLIER = 2
VICE_CAPTAIN_MULTIPLIER = 2


BONUS_FIRST_PLACE = 3
BONUS_SECOND_PLACE = 2
BONUS_THIRD_PLACE = 1

BONUS_REWARDS = {
    1: BONUS_FIRST_PLACE,
    2: BONUS_SECOND_PLACE,
    3: BONUS_THIRD_PLACE,
}

MAX_TRANSFERS_PER_GW = 2
TRANSFER_PENALTY = 4

CURRENT_SEASON = '2025/2026'
DEFAULT_GAMEWEEK = 1

FPL_GOAL_POINTS = {
    'GK': 6,
    'DF': 6,
    'MF': 5,
    'FW': 4,
}

FPL_ASSIST_POINTS = 3
FPL_CLEAN_SHEET_GK_DF = 4
FPL_CLEAN_SHEET_MF = 1
FPL_SAVE_POINTS = 3
FPL_GOALS_CONCEDED_PENALTY = 2
FPL_YELLOW_CARD_PENALTY = 1
FPL_RED_CARD_PENALTY = 3
FPL_MINUTES_60_PLUS = 2
FPL_MINUTES_LESS_60 = 1

POSITION_EMOJI = {
    'GK': '🧤',
    'DF': '️',
    'MF': '⚙️',
    'FW': '⚽',
    'SUB': '',
}

POSITION_NAMES = {
    'GK': 'Вратарь',
    'DF': 'Защитник',
    'MF': 'Полузащитник',
    'FW': 'Нападающий',
}