from pprint import pprint

from src.player import PlayerData, PlayerService
from src.player_service import PlayerDataService
from src.roster_unit_service import RosterDataService, CreateUnitService


class UnitAggregateService:
    async def create_or_update_unit(self):
        """Создание юнита в БД"""
        ally_codes = await PlayerData().get_today_players_ally_codes()
        counter = 0
        for ally_code in ally_codes:
            player_id = await PlayerData().get_today_player_id(ally_code)
            comlink_raw_data = await PlayerService().get_comlink_player(ally_code)
            roster_data = await RosterDataService().get_roster_data(comlink_raw_data['rosterUnit'])
            units = []
            for roster_unit in roster_data:
                units.append(await CreateUnitService(roster_unit, player_id).update_today_units())

            await PlayerData().update_players_units(player_id, units)
            counter += 1
            print(counter)
        print(f"Юниты {counter} игроков обновлены.")