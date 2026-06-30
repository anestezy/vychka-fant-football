"""
Загрузка 100 реальных игроков АПЛ в БД
"""
from db_connection import Database

# Реальные игроки АПЛ (сезон 2025/26)
PLAYERS = [
    # Arsenal (team_id: 1)
    {'id': 1, 'name': 'David Raya', 'position': 'GK', 'team_id': 1, 'price': 5.5, 'points': 142, 'form': 5.2},
    {'id': 2, 'name': 'William Saliba', 'position': 'DF', 'team_id': 1, 'price': 6.0, 'points': 128, 'form': 4.8},
    {'id': 3, 'name': 'Gabriel Magalhães', 'position': 'DF', 'team_id': 1, 'price': 5.5, 'points': 115, 'form': 4.5},
    {'id': 4, 'name': 'Ben White', 'position': 'DF', 'team_id': 1, 'price': 5.5, 'points': 108, 'form': 4.2},
    {'id': 5, 'name': 'Bukayo Saka', 'position': 'MF', 'team_id': 1, 'price': 10.5, 'points': 205, 'form': 7.8},
    {'id': 6, 'name': 'Martin Ødegaard', 'position': 'MF', 'team_id': 1, 'price': 8.5, 'points': 168, 'form': 6.5},
    {'id': 7, 'name': 'Declan Rice', 'position': 'MF', 'team_id': 1, 'price': 7.0, 'points': 145, 'form': 5.0},
    {'id': 8, 'name': 'Kai Havertz', 'position': 'FW', 'team_id': 1, 'price': 8.0, 'points': 152, 'form': 5.5},
    {'id': 9, 'name': 'Gabriel Martinelli', 'position': 'FW', 'team_id': 1, 'price': 7.5, 'points': 138, 'form': 5.0},
    {'id': 10, 'name': 'Leandro Trossard', 'position': 'FW', 'team_id': 1, 'price': 7.0, 'points': 125, 'form': 4.8},

    # Man City (team_id: 2)
    {'id': 11, 'name': 'Ederson', 'position': 'GK', 'team_id': 2, 'price': 5.5, 'points': 138, 'form': 5.0},
    {'id': 12, 'name': 'Rúben Dias', 'position': 'DF', 'team_id': 2, 'price': 6.5, 'points': 132, 'form': 5.2},
    {'id': 13, 'name': 'John Stones', 'position': 'DF', 'team_id': 2, 'price': 5.5, 'points': 98, 'form': 4.0},
    {'id': 14, 'name': 'Nathan Aké', 'position': 'DF', 'team_id': 2, 'price': 5.0, 'points': 105, 'form': 4.2},
    {'id': 15, 'name': 'Kevin De Bruyne', 'position': 'MF', 'team_id': 2, 'price': 10.0, 'points': 195, 'form': 7.5},
    {'id': 16, 'name': 'Phil Foden', 'position': 'MF', 'team_id': 2, 'price': 9.5, 'points': 188, 'form': 7.2},
    {'id': 17, 'name': 'Bernardo Silva', 'position': 'MF', 'team_id': 2, 'price': 7.5, 'points': 155, 'form': 5.8},
    {'id': 18, 'name': 'Erling Haaland', 'position': 'FW', 'team_id': 2, 'price': 14.0, 'points': 260, 'form': 9.5},
    {'id': 19, 'name': 'Jérémy Doku', 'position': 'FW', 'team_id': 2, 'price': 7.0, 'points': 120, 'form': 4.5},
    {'id': 20, 'name': 'Jack Grealish', 'position': 'FW', 'team_id': 2, 'price': 7.5, 'points': 115, 'form': 4.8},

    # Liverpool (team_id: 3)
    {'id': 21, 'name': 'Alisson Becker', 'position': 'GK', 'team_id': 3, 'price': 5.5, 'points': 145, 'form': 5.5},
    {'id': 22, 'name': 'Virgil van Dijk', 'position': 'DF', 'team_id': 3, 'price': 6.5, 'points': 140, 'form': 5.8},
    {'id': 23, 'name': 'Trent Alexander-Arnold', 'position': 'DF', 'team_id': 3, 'price': 7.0, 'points': 165,
     'form': 6.5},
    {'id': 24, 'name': 'Ibrahima Konaté', 'position': 'DF', 'team_id': 3, 'price': 5.5, 'points': 112, 'form': 4.5},
    {'id': 25, 'name': 'Mohamed Salah', 'position': 'MF', 'team_id': 3, 'price': 12.5, 'points': 220, 'form': 8.5},
    {'id': 26, 'name': 'Dominik Szoboszlai', 'position': 'MF', 'team_id': 3, 'price': 7.0, 'points': 148, 'form': 5.5},
    {'id': 27, 'name': 'Alexis Mac Allister', 'position': 'MF', 'team_id': 3, 'price': 6.5, 'points': 135, 'form': 5.0},
    {'id': 28, 'name': 'Darwin Núñez', 'position': 'FW', 'team_id': 3, 'price': 7.5, 'points': 155, 'form': 5.8},
    {'id': 29, 'name': 'Luis Díaz', 'position': 'FW', 'team_id': 3, 'price': 7.5, 'points': 148, 'form': 5.5},
    {'id': 30, 'name': 'Diogo Jota', 'position': 'FW', 'team_id': 3, 'price': 8.0, 'points': 142, 'form': 5.2},

    # Chelsea (team_id: 4)
    {'id': 31, 'name': 'Robert Sánchez', 'position': 'GK', 'team_id': 4, 'price': 4.5, 'points': 98, 'form': 4.0},
    {'id': 32, 'name': 'Reece James', 'position': 'DF', 'team_id': 4, 'price': 5.5, 'points': 88, 'form': 3.8},
    {'id': 33, 'name': 'Levi Colwill', 'position': 'DF', 'team_id': 4, 'price': 5.0, 'points': 105, 'form': 4.2},
    {'id': 34, 'name': 'Marc Cucurella', 'position': 'DF', 'team_id': 4, 'price': 5.0, 'points': 112, 'form': 4.5},
    {'id': 35, 'name': 'Enzo Fernández', 'position': 'MF', 'team_id': 4, 'price': 7.0, 'points': 125, 'form': 4.8},
    {'id': 36, 'name': 'Cole Palmer', 'position': 'MF', 'team_id': 4, 'price': 8.5, 'points': 195, 'form': 7.5},
    {'id': 37, 'name': 'Moisés Caicedo', 'position': 'MF', 'team_id': 4, 'price': 6.5, 'points': 118, 'form': 4.5},
    {'id': 38, 'name': 'Nicolas Jackson', 'position': 'FW', 'team_id': 4, 'price': 7.0, 'points': 145, 'form': 5.5},
    {'id': 39, 'name': 'Noni Madueke', 'position': 'FW', 'team_id': 4, 'price': 6.5, 'points': 128, 'form': 5.0},
    {'id': 40, 'name': 'Pedro Neto', 'position': 'FW', 'team_id': 4, 'price': 6.5, 'points': 115, 'form': 4.5},

    # Man United (team_id: 5)
    {'id': 41, 'name': 'André Onana', 'position': 'GK', 'team_id': 5, 'price': 5.0, 'points': 108, 'form': 4.5},
    {'id': 42, 'name': 'Lisandro Martínez', 'position': 'DF', 'team_id': 5, 'price': 5.5, 'points': 98, 'form': 4.0},
    {'id': 43, 'name': 'Matthijs de Ligt', 'position': 'DF', 'team_id': 5, 'price': 6.0, 'points': 105, 'form': 4.2},
    {'id': 44, 'name': 'Diogo Dalot', 'position': 'DF', 'team_id': 5, 'price': 5.0, 'points': 112, 'form': 4.5},
    {'id': 45, 'name': 'Bruno Fernandes', 'position': 'MF', 'team_id': 5, 'price': 8.5, 'points': 168, 'form': 6.5},
    {'id': 46, 'name': 'Kobbie Mainoo', 'position': 'MF', 'team_id': 5, 'price': 5.5, 'points': 105, 'form': 4.2},
    {'id': 47, 'name': 'Mason Mount', 'position': 'MF', 'team_id': 5, 'price': 6.5, 'points': 88, 'form': 3.5},
    {'id': 48, 'name': 'Rasmus Højlund', 'position': 'FW', 'team_id': 5, 'price': 7.0, 'points': 118, 'form': 4.8},
    {'id': 49, 'name': 'Alejandro Garnacho', 'position': 'FW', 'team_id': 5, 'price': 6.5, 'points': 125, 'form': 5.0},
    {'id': 50, 'name': 'Joshua Zirkzee', 'position': 'FW', 'team_id': 5, 'price': 7.0, 'points': 95, 'form': 4.0},

    # Tottenham (team_id: 6)
    {'id': 51, 'name': 'Guglielmo Vicario', 'position': 'GK', 'team_id': 6, 'price': 5.0, 'points': 125, 'form': 5.0},
    {'id': 52, 'name': 'Cristian Romero', 'position': 'DF', 'team_id': 6, 'price': 5.5, 'points': 108, 'form': 4.5},
    {'id': 53, 'name': 'Micky van de Ven', 'position': 'DF', 'team_id': 6, 'price': 5.5, 'points': 115, 'form': 4.8},
    {'id': 54, 'name': 'Destiny Udogie', 'position': 'DF', 'team_id': 6, 'price': 5.0, 'points': 120, 'form': 5.0},
    {'id': 55, 'name': 'James Maddison', 'position': 'MF', 'team_id': 6, 'price': 7.5, 'points': 155, 'form': 6.0},
    {'id': 56, 'name': 'Dejan Kulusevski', 'position': 'MF', 'team_id': 6, 'price': 7.0, 'points': 148, 'form': 5.8},
    {'id': 57, 'name': 'Brennan Johnson', 'position': 'MF', 'team_id': 6, 'price': 6.5, 'points': 138, 'form': 5.5},
    {'id': 58, 'name': 'Son Heung-min', 'position': 'FW', 'team_id': 6, 'price': 9.5, 'points': 185, 'form': 7.2},
    {'id': 59, 'name': 'Dominic Solanke', 'position': 'FW', 'team_id': 6, 'price': 7.5, 'points': 152, 'form': 5.8},
    {'id': 60, 'name': 'Richarlison', 'position': 'FW', 'team_id': 6, 'price': 7.0, 'points': 115, 'form': 4.5},

    # Aston Villa (team_id: 7)
    {'id': 61, 'name': 'Emiliano Martínez', 'position': 'GK', 'team_id': 7, 'price': 5.5, 'points': 155, 'form': 6.0},
    {'id': 62, 'name': 'Pau Torres', 'position': 'DF', 'team_id': 7, 'price': 5.5, 'points': 118, 'form': 4.8},
    {'id': 63, 'name': 'Ezri Konsa', 'position': 'DF', 'team_id': 7, 'price': 5.0, 'points': 125, 'form': 5.0},
    {'id': 64, 'name': 'Lucas Digne', 'position': 'DF', 'team_id': 7, 'price': 4.5, 'points': 108, 'form': 4.5},
    {'id': 65, 'name': 'Douglas Luiz', 'position': 'MF', 'team_id': 7, 'price': 6.5, 'points': 138, 'form': 5.5},
    {'id': 66, 'name': 'John McGinn', 'position': 'MF', 'team_id': 7, 'price': 6.0, 'points': 128, 'form': 5.0},
    {'id': 67, 'name': 'Jacob Ramsey', 'position': 'MF', 'team_id': 7, 'price': 6.0, 'points': 115, 'form': 4.8},
    {'id': 68, 'name': 'Ollie Watkins', 'position': 'FW', 'team_id': 7, 'price': 8.5, 'points': 198, 'form': 7.5},
    {'id': 69, 'name': 'Morgan Rogers', 'position': 'FW', 'team_id': 7, 'price': 5.5, 'points': 105, 'form': 4.2},
    {'id': 70, 'name': 'Jhon Durán', 'position': 'FW', 'team_id': 7, 'price': 6.0, 'points': 98, 'form': 4.0},

    # Newcastle (team_id: 8)
    {'id': 71, 'name': 'Nick Pope', 'position': 'GK', 'team_id': 8, 'price': 5.5, 'points': 135, 'form': 5.5},
    {'id': 72, 'name': 'Sven Botman', 'position': 'DF', 'team_id': 8, 'price': 5.5, 'points': 108, 'form': 4.5},
    {'id': 73, 'name': 'Fabian Schär', 'position': 'DF', 'team_id': 8, 'price': 5.5, 'points': 125, 'form': 5.0},
    {'id': 74, 'name': 'Dan Burn', 'position': 'DF', 'team_id': 8, 'price': 4.5, 'points': 98, 'form': 4.0},
    {'id': 75, 'name': 'Bruno Guimarães', 'position': 'MF', 'team_id': 8, 'price': 7.0, 'points': 148, 'form': 5.8},
    {'id': 76, 'name': 'Joelinton', 'position': 'MF', 'team_id': 8, 'price': 6.5, 'points': 135, 'form': 5.2},
    {'id': 77, 'name': 'Sandro Tonali', 'position': 'MF', 'team_id': 8, 'price': 6.5, 'points': 88, 'form': 4.0},
    {'id': 78, 'name': 'Alexander Isak', 'position': 'FW', 'team_id': 8, 'price': 8.5, 'points': 185, 'form': 7.2},
    {'id': 79, 'name': 'Anthony Gordon', 'position': 'FW', 'team_id': 8, 'price': 7.5, 'points': 168, 'form': 6.5},
    {'id': 80, 'name': 'Callum Wilson', 'position': 'FW', 'team_id': 8, 'price': 7.5, 'points': 105, 'form': 4.5},

    # Brighton (team_id: 9)
    {'id': 81, 'name': 'Bart Verbruggen', 'position': 'GK', 'team_id': 9, 'price': 4.5, 'points': 108, 'form': 4.5},
    {'id': 82, 'name': 'Lewis Dunk', 'position': 'DF', 'team_id': 9, 'price': 5.0, 'points': 118, 'form': 4.8},
    {'id': 83, 'name': 'Jan Paul van Hecke', 'position': 'DF', 'team_id': 9, 'price': 4.5, 'points': 105, 'form': 4.2},
    {'id': 84, 'name': 'Pervis Estupiñán', 'position': 'DF', 'team_id': 9, 'price': 5.0, 'points': 128, 'form': 5.2},
    {'id': 85, 'name': 'Kaoru Mitoma', 'position': 'MF', 'team_id': 9, 'price': 7.0, 'points': 145, 'form': 5.8},
    {'id': 86, 'name': 'Billy Gilmour', 'position': 'MF', 'team_id': 9, 'price': 5.5, 'points': 98, 'form': 4.0},
    {'id': 87, 'name': 'Simon Adingra', 'position': 'MF', 'team_id': 9, 'price': 6.0, 'points': 115, 'form': 4.8},
    {'id': 88, 'name': 'João Pedro', 'position': 'FW', 'team_id': 9, 'price': 7.0, 'points': 148, 'form': 5.8},
    {'id': 89, 'name': 'Danny Welbeck', 'position': 'FW', 'team_id': 9, 'price': 6.0, 'points': 118, 'form': 4.8},
    {'id': 90, 'name': 'Evan Ferguson', 'position': 'FW', 'team_id': 9, 'price': 6.5, 'points': 88, 'form': 3.8},

    # West Ham (team_id: 10)
    {'id': 91, 'name': 'Alphonse Areola', 'position': 'GK', 'team_id': 10, 'price': 4.5, 'points': 105, 'form': 4.5},
    {'id': 92, 'name': 'Vladimír Coufal', 'position': 'DF', 'team_id': 10, 'price': 4.5, 'points': 112, 'form': 4.8},
    {'id': 93, 'name': 'Konstantinos Mavropanos', 'position': 'DF', 'team_id': 10, 'price': 4.5, 'points': 98,
     'form': 4.0},
    {'id': 94, 'name': 'Aaron Cresswell', 'position': 'DF', 'team_id': 10, 'price': 4.5, 'points': 85, 'form': 3.8},
    {'id': 95, 'name': 'Lucas Paquetá', 'position': 'MF', 'team_id': 10, 'price': 7.0, 'points': 145, 'form': 5.8},
    {'id': 96, 'name': 'James Ward-Prowse', 'position': 'MF', 'team_id': 10, 'price': 6.5, 'points': 128, 'form': 5.2},
    {'id': 97, 'name': 'Mohammed Kudus', 'position': 'MF', 'team_id': 10, 'price': 7.0, 'points': 155, 'form': 6.0},
    {'id': 98, 'name': 'Jarrod Bowen', 'position': 'FW', 'team_id': 10, 'price': 7.5, 'points': 168, 'form': 6.5},
    {'id': 99, 'name': 'Michail Antonio', 'position': 'FW', 'team_id': 10, 'price': 6.5, 'points': 118, 'form': 4.8},
    {'id': 100, 'name': 'Danny Ings', 'position': 'FW', 'team_id': 10, 'price': 6.0, 'points': 88, 'form': 4.0},
]

TEAMS = [
    {'id': 1, 'name': 'Arsenal', 'short_name': 'ARS'},
    {'id': 2, 'name': 'Manchester City', 'short_name': 'MCI'},
    {'id': 3, 'name': 'Liverpool', 'short_name': 'LIV'},
    {'id': 4, 'name': 'Chelsea', 'short_name': 'CHE'},
    {'id': 5, 'name': 'Manchester United', 'short_name': 'MUN'},
    {'id': 6, 'name': 'Tottenham Hotspur', 'short_name': 'TOT'},
    {'id': 7, 'name': 'Aston Villa', 'short_name': 'AVL'},
    {'id': 8, 'name': 'Newcastle United', 'short_name': 'NEW'},
    {'id': 9, 'name': 'Brighton & Hove Albion', 'short_name': 'BHA'},
    {'id': 10, 'name': 'West Ham United', 'short_name': 'WHU'},
]


def insert_teams():
    query = """
        INSERT INTO real_teams (id, name, short_name, tla, area)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name=VALUES(name), short_name=VALUES(short_name)
    """
    params = [(t['id'], t['name'], t['short_name'], t['short_name'], 'England') for t in TEAMS]
    Database.execute_many(query, params)
    print(f"✅ Команд загружено: {len(TEAMS)}")


def insert_players():
    query = """
        INSERT INTO real_players 
        (id, name, position, current_team_id, price, total_points, form, shirt_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name=VALUES(name), position=VALUES(position), 
        current_team_id=VALUES(current_team_id), price=VALUES(price),
        total_points=VALUES(total_points), form=VALUES(form)
    """
    params = []
    for p in PLAYERS:
        params.append((
            p['id'], p['name'], p['position'], p['team_id'],
            p['price'], p['points'], p['form'], 0
        ))
    Database.execute_many(query, params)
    print(f"✅ Игроков загружено: {len(PLAYERS)}")


def main():
    print("🚀 Загрузка тестовых данных...")
    insert_teams()
    insert_players()
    print("🎉 Готово!")


if __name__ == '__main__':
    main()