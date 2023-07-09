# src/player.py

import json
import os

import requests
from sqlalchemy import func

from create_bot import session
from datetime import datetime, timedelta, time

from db_models import Player, Guild
from pytz import timezone
from dotenv import load_dotenv

from src.errors import Status404Error, AddIdsError, DatabaseBuildError
from src.utils import get_new_day_start

load_dotenv()

utc_tz = timezone('UTC')

tz = str(os.environ.get("TIME_ZONE"))
time_tz = timezone(tz)

API_LINK = f"{os.environ.get('API_HOST')}:{os.environ.get('API_PORT')}"
GUILD_POST_DATA = {
    "payload": {
        "guildId": os.environ.get("GUILD_ID"),
        "includeRecentGuildActivityInfo": True
    },
    "enums": False
}


class PlayerData:
    @staticmethod
    def get_swgoh_player_data(ally_code):
        player_request = requests.get(f'http://api.swgoh.gg/player/{ally_code}/')
        if player_request.status_code == 200:
            data = player_request.json()
            return data['data']

    def __add_ids(self):
        try:
            with open("./api/ids.json", encoding="utf-8") as f:
                data = json.load(f)  # Загрузить список словарей

            result = {}  # Создать пустой словарь

            for d in data:  # Пройтись по всем словарям в списке
                for key, value in d.items():  # Пройтись по всем парам ключ-значение в словаре
                    result[key] = value  # Добавить ключ и значение в результат
            return result
        except Exception as e:
            raise AddIdsError(f"An error occurred while getting ids.json data: {e}") from e

    def create_or_update_player_data(self, data: dict):
        """Создает или обновляет данные пользователя на текущий день"""
        try:
            new_day_start = get_new_day_start()

            existing_user_today = session.query(Player).filter_by(ally_code=data['ally_code']).filter(
                Player.update_time >= new_day_start).first()

            # Если пользователь уже существует
            if existing_user_today:
                print(f"{data['name']}: old")
                self.__set_player_attributes(existing_user_today, data)
                session.commit()
            else:
                print(f"{data['name']}: new")
                # Добавляем нового пользователя
                new_user = self.__set_player_attributes(Player(), data)
                session.add(new_user)
                session.commit()

                # Удаление записей старше месяца
            month_old_date = datetime.now() - timedelta(days=30)
            session.query(Player).filter(Player.update_time < month_old_date).delete()
            session.commit()
        except Exception as e:
            raise DatabaseBuildError(f"An error occurred while building the Player database: {e}") from e

    def __set_player_attributes(self, player, data):
        """Устанавливает значения из переданного словаря в модель Player"""
        player.name = data['name']

        # конвертирует дату вступления в гильдии в удобочитабельный формат нужного часового пояса
        guild_join_time_utc = datetime.strptime(data['guild_join_time'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc_tz)
        player.guild_join_time = guild_join_time_utc.astimezone(time_tz)

        # конвертирует дату последей активности в удобочитабеольный формат нужного часового пояса
        timestamp_ms = data['lastActivityTime']
        timestamp = int(timestamp_ms) / 1000
        last_activity_time_utc = datetime.fromtimestamp(timestamp).replace(tzinfo=utc_tz)
        player.lastActivityTime = last_activity_time_utc.astimezone(time_tz)

        player.reid_points = int(data['reid_points'])
        player.guild_currency_earned = int(data['guild_points'])
        player.player_id = data['playerId']
        player.tg_id = data['existing_player']['tg_id']
        player.update_time = datetime.now(time_tz)
        player.ally_code = data['ally_code']
        player.arena_leader_base_id = data['arena_leader_base_id']
        player.arena_rank = data['arena_rank']
        player.level = data['level']

        last_updated_utc = datetime.strptime(data['last_updated'], '%Y-%m-%dT%H:%M:%S').replace(tzinfo=utc_tz)
        player.last_swgoh_updated = last_updated_utc.astimezone(time_tz)

        player.galactic_power = data['galactic_power']
        player.character_galactic_power = data['character_galactic_power']
        player.ship_galactic_power = data['ship_galactic_power']
        player.ship_battles_won = data['ship_battles_won']
        player.pvp_battles_won = data['pvp_battles_won']
        player.pve_battles_won = data['pve_battles_won']
        player.pve_hard_won = data['pve_hard_won']
        player.galactic_war_won = data['galactic_war_won']
        player.guild_raid_won = data['guild_raid_won']
        player.guild_exchange_donations = data['guild_exchange_donations']
        player.season_status = data['season_status']
        player.season_full_clears = data['season_full_clears']
        player.season_successful_defends = data['season_successful_defends']
        player.season_league_score = data['season_league_score']
        player.season_undersized_squad_wins = data['season_undersized_squad_wins']
        player.season_promotions_earned = data['season_promotions_earned']
        player.season_banners_earned = data['season_banners_earned']
        player.season_offensive_battles_won = data['season_offensive_battles_won']
        player.season_territories_defeated = data['season_territories_defeated']
        player.url = 'https://swgoh.gg' + data['url']

        return player

    def update_players_data(self):
        """Вытаскивает данные о гильдии и участниках, а после
         по имени участника гоняет циклом обновление бд для каждого участника"""
        try:
            swgoh_request = requests.get(f"http://api.swgoh.gg/guild-profile/{os.environ.get('GUILD_ID')}")
            error_list = []
            swgoh_request.raise_for_status()
            data = swgoh_request.json()
            existing_players = self.__add_ids()

            try:
                comlink_request = requests.post(f"{API_LINK}/guild", json=GUILD_POST_DATA)
                comlink_request.raise_for_status()
                raw_data = comlink_request.json()
                guild_data_dict = {player['playerName']: player for player in raw_data['guild']['member']}
            except requests.exceptions.HTTPError:
                raise Status404Error(f"Комлинк с гильдией не отвечает при построении базы для игрока")

            for i in data['data']['members']:
                if str(i['ally_code']) in existing_players:
                    final_data: dict = self.get_swgoh_player_data(i['ally_code'])
                    final_data.update({'guild_join_time': i['guild_join_time']})
                    final_data.update({'existing_player': existing_players[str(i['ally_code'])]})
                    try:
                        post_data = {
                            "payload": {
                                "allyCode": f"{i['ally_code']}"
                            },
                            "enums": False
                        }
                        comlink_player_request = requests.post(f"{API_LINK}/player", json=post_data)
                        comlink_player_request.raise_for_status()
                        comlink_data = comlink_player_request.json()
                        final_data.update({'name': comlink_data['name']})
                        final_data.update({'level': comlink_data['level']})
                        final_data.update({'playerId': comlink_data['playerId']})
                        final_data.update({'lastActivityTime': comlink_data['lastActivityTime']})
                        member_contribution_dict = {item['type']: item['currentValue'] for item in
                                                    guild_data_dict[comlink_data['name']]['memberContribution']}
                        final_data.update({'reid_points': member_contribution_dict[2]})
                        final_data.update({'guild_points': member_contribution_dict[1]})
                        final_data.update({'season_status': len(guild_data_dict[comlink_data['name']]['seasonStatus'])})

                        self.create_or_update_player_data(final_data)

                    except Exception as e:
                        raise Status404Error(
                            f"Комлинк с гильдией не отвечает при построении базы для игрока {e}") from e

                else:
                    error_list.append(f"Игрок {i['player_name']} отсутствует в гильдии. Обновите ids.json")

            print("\n".join(error_list))
            print("Данные игроков в базе обновлены.")

        except Exception as e:
            raise Status404Error(f"An error occurred while building the Player database: {e}") from e

    def extract_data(self, player: Player):
        """Выводит все данные по игроку"""
        data_dict = player.__dict__
        formatted_string = "\n".join(
            f"{key}: {value}\n{'-' * 30}" for key, value in data_dict.items() if not key.startswith('_'))
        return formatted_string

    @staticmethod
    def get_player_filtered_data(data: Player, key: str):
        """Возвращает данные игрока по ключу"""
        return data.__dict__[key]

    @staticmethod
    def get_raid_scores():
        new_day_start = get_new_day_start()
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # получить данные за (сегодня)
        recent_players = session.query(Player).filter(
            Player.update_time >= new_day_start
        ).all()

        if not recent_players:
            return "Нет данных об игроках."

        # отбираем самую свежую запись для каждого игрока
        players_dict = {}
        for player in recent_players:
            if player.name not in players_dict or player.update_time > players_dict[player.name].update_time:
                players_dict[player.name] = player

        # форматируем результат в нужный вид и сортируем по убыванию очков
        raid_scores = [
            f"{player.name} {player.reid_points} купонов"
            for player in sorted(players_dict.values(), key=lambda x: x.reid_points, reverse=True)
        ]

        return f"\n{'-' * 30}\n".join(raid_scores)

    @staticmethod
    def get_reid_lazy_fools():
        new_day_start = get_new_day_start()

        # existing_user_today = session.query(Player).filter_by(name=data['name']).filter(
        #     Player.update_time >= new_day_start).first()
        # today = datetime.now().date()

        # получить данные за (сегодня)
        recent_players = session.query(Player).filter(
            Player.update_time >= new_day_start
        ).all()

        if not recent_players:
            return "Нет данных об игроках."

        # отбираем самую свежую запись для каждого игрока
        players_dict = {}
        for player in recent_players:
            if player.name not in players_dict or player.update_time > players_dict[player.name].update_time:
                players_dict[player.name] = player
        # форматируем результат в нужный вид и сортируем по убыванию очков
        reid_scores = [
            f"{player.name} {player.reid_points} купонов"
            for player in sorted(players_dict.values(), key=lambda x: x.reid_points, reverse=True)
            if player.reid_points < 600  # добавляем условие
        ]

        # добавляем время обновления, используя время обновления первого игрока в списке
        update_time = recent_players[0].update_time.strftime('%H:%M:%S')
        reid_scores.insert(0,
                           f"Список не сдавших 600 купонов по состоянию на {update_time} {os.environ.get('TZ_SUFIX')}:\n")

        return f"\n{'-' * 30}\n".join(reid_scores)