
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import os
from db_connection import Database

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

COLORS = {
    'primary': '#2196F3',
    'secondary': '#4CAF50',
    'accent': '#FF9800',
    'danger': '#F44336',
    'bg': '#FFFFFF',
    'grid': '#E0E0E0',
}

CHARTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_charts')
os.makedirs(CHARTS_DIR, exist_ok=True)


def create_points_over_time_chart(user_id):

    query = """
        SELECT 
            l.gameweek,
            l.gameweek_points,
            l.total_points
        FROM leaderboard l
        WHERE l.user_id = %s
        ORDER BY l.gameweek
    """

    data = Database.execute_query(query, params=(user_id,), fetch=True)

    if not data:
        return None

    gameweek_nums = [row['gameweek'] for row in data]
    gw_points = [row['gameweek_points'] for row in data]
    total_points = [row['total_points'] for row in data]

    fig, ax1 = plt.subplots(figsize=(10, 6))

    bars = ax1.bar(gameweek_nums, gw_points, color=COLORS['primary'], alpha=0.7, label='Очки за GW')
    ax1.set_xlabel('Gameweek', fontsize=12)
    ax1.set_ylabel('Очки за геймвик', color=COLORS['primary'], fontsize=12)
    ax1.tick_params(axis='y', labelcolor=COLORS['primary'])

    ax2 = ax1.twinx()
    ax2.plot(gameweek_nums, total_points, color=COLORS['secondary'], linewidth=2,
             marker='o', markersize=6, label='Суммарные очки')
    ax2.set_ylabel('Суммарные очки', color=COLORS['secondary'], fontsize=12)
    ax2.tick_params(axis='y', labelcolor=COLORS['secondary'])

    plt.title('Динамика очков по геймвикам', fontsize=14, fontweight='bold', pad=20)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    ax1.grid(axis='y', alpha=0.3, color=COLORS['grid'])
    ax1.set_xticks(gameweek_nums)

    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f'points_over_time_{user_id}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath


def create_position_distribution_chart(user_id):

    query = """
        SELECT 
            rp.position,
            COUNT(*) as count
        FROM user_team_players utp
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN user_teams ut ON utp.user_team_id = ut.id
        WHERE ut.user_id = %s
        GROUP BY rp.position
        ORDER BY 
            CASE rp.position 
                WHEN 'GK' THEN 1 
                WHEN 'DF' THEN 2 
                WHEN 'MF' THEN 3 
                WHEN 'FW' THEN 4 
            END
    """

    data = Database.execute_query(query, params=(user_id,), fetch=True)

    if not data:
        return None

    position_names = {'GK': 'Вратари', 'DF': 'Защитники', 'MF': 'Полузащитники', 'FW': 'Нападающие'}
    colors = ['#FFC107', '#2196F3', '#4CAF50', '#F44336']

    labels = [position_names.get(row['position'], row['position']) for row in data]
    sizes = [row['count'] for row in data]

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.0f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12},
        pctdistance=0.75,
        wedgeprops={'width': 0.5, 'edgecolor': 'white', 'linewidth': 2}
    )

    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')

    plt.title('Распределение игроков по позициям', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f'position_dist_{user_id}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath


def create_top_players_chart(user_id, top_n=5):

    query = """
        SELECT 
            rp.name,
            rp.position,
            SUM(ps.fantasy_points) as total_pts
        FROM user_team_players utp
        JOIN player_stats ps ON utp.player_id = ps.player_id
        JOIN real_players rp ON utp.player_id = rp.id
        JOIN user_teams ut ON utp.user_team_id = ut.id
        WHERE ut.user_id = %s
        GROUP BY rp.id, rp.name, rp.position
        ORDER BY total_pts DESC
        LIMIT %s
    """

    data = Database.execute_query(query, params=(user_id, top_n), fetch=True)

    if not data:
        return None

    names = [row['name'] for row in data]
    points = [row['total_pts'] for row in data]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(names[::-1], points[::-1], color=COLORS['primary'], alpha=0.8, edgecolor='white')

    for bar, point in zip(bars, points[::-1]):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{point} pts', va='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('Очки', fontsize=12)
    ax.set_title(f'Топ-{top_n} игроков по очкам', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, color=COLORS['grid'])

    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f'top_players_{user_id}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath


def create_player_form_chart(player_id, last_n=5):

    query = """
        SELECT 
            ps.gameweek,
            ps.fantasy_points,
            ps.goals,
            ps.assists
        FROM player_stats ps
        WHERE ps.player_id = %s
        ORDER BY ps.gameweek DESC
        LIMIT %s
    """

    data = Database.execute_query(query, params=(player_id, last_n), fetch=True)

    if not data:
        return None

    data = data[::-1]

    gameweeks = [row['gameweek'] for row in data]
    points = [row['fantasy_points'] for row in data]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(gameweeks, points, color=COLORS['accent'], linewidth=2, marker='o', markersize=8)
    ax.fill_between(gameweeks, points, alpha=0.3, color=COLORS['accent'])

    for gw, pt in zip(gameweeks, points):
        ax.annotate(f'{pt}', (gw, pt), textcoords="offset points",
                    xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')

    ax.set_xlabel('Gameweek', fontsize=12)
    ax.set_ylabel('Очки', fontsize=12)
    ax.set_title('Форма игрока', fontsize=14, fontweight='bold', pad=20)
    ax.grid(alpha=0.3, color=COLORS['grid'])
    ax.set_xticks(gameweeks)

    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f'player_form_{player_id}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath


def create_team_comparison_chart(user_id):

    query = """
        SELECT 
            utp.is_starting,
            SUM(ps.fantasy_points) as total_pts,
            COUNT(*) as player_count
        FROM user_team_players utp
        JOIN player_stats ps ON utp.player_id = ps.player_id
        JOIN user_teams ut ON utp.user_team_id = ut.id
        WHERE ut.user_id = %s
        GROUP BY utp.is_starting
    """

    data = Database.execute_query(query, params=(user_id,), fetch=True)

    if not data:
        return None

    labels = ['Стартовый состав', 'Скамейка']
    sizes = [0, 0]

    for row in data:
        idx = 0 if row['is_starting'] else 1
        sizes[idx] = row['total_pts']

    colors = [COLORS['primary'], COLORS['accent']]

    fig, ax = plt.subplots(figsize=(8, 8))

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 12},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )

    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_fontweight('bold')

    plt.title('Распределение очков: старт vs скамейка', fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()

    filepath = os.path.join(CHARTS_DIR, f'team_comparison_{user_id}.png')
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()

    return filepath