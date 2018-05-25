"""
This module acts as a middleware between DB and actual data that we want to
display. Here we request information from DB and preformat it to be used by
client.
"""

from wc3inside.utils.db import DBTopOpponents, DBHistory, DBState, DBGamesStats

from typing import List, Dict
import copy


class MatchObject(object):

    def __init__(self, game_dict: dict, player: str) -> None:
        self._game_dict = game_dict
        self._player = player
        self.we_won: bool = None

    def get_enemies(self) -> List:
        for p in self._game_dict["players_data"]:
            if p["username"] == self._player:
                if p["result"] == "Win":
                    self.we_won = True
                    break

        look_for_result = "Loss" if self.we_won else "Win"
        enemies = []
        for p in self._game_dict["players_data"]:
            if p["result"] == look_for_result:
                # Opponent name and our result
                enemies.append((p["username"], self.we_won))

        return enemies


class TopOpponentsView(object):

    def __init__(self, gateway: str):
        self.gateway = gateway
        self.db = DBTopOpponents(gateway)

    def _extract_stats(self, enemies: List, player: str) -> Dict:
        stats = {}
        for enemy, result in enemies:
            if enemy not in stats:
                stats[enemy] = {
                    "primary_player": player,
                    "secondary_player": enemy,
                    "win": 0,
                    "loss": 0,
                    "state": 0,
                    "history": [],
                }

            if result:
                stats[enemy]["win"] += 1
            else:
                stats[enemy]["loss"] += 1

        for e in stats.keys():
            if stats[e]["win"] > stats[e]["loss"]:
                stats[e]["state"] = 1
            elif stats[e]["win"] < stats[e]["loss"]:
                stats[e]["state"] = -1

        return stats

    def get_stats(self, username: str) -> str:
        all_games = [
            MatchObject(g, username) for g in self.db.get_solo_games_by_user(username)
        ]
        enemies = []
        for game in all_games:
            enemies += game.get_enemies()

        stats = self._extract_stats(enemies, username)

        ordered_stats = sorted(
            stats.items(), key=lambda x: -1 * (x[1]["win"] + x[1]["loss"])
        )

        stats = ordered_stats[0:20]
        only_enemies_to_display = [s[0] for s in stats]

        for game in all_games:
            for enemy in only_enemies_to_display:
                if enemy in game._game_dict["players"]:
                    for s in stats:
                        if len(s[1]["history"]) >= 5:
                            continue
                        if s[0] == enemy:
                            g = copy.copy(game._game_dict)
                            g.pop("_id")
                            g["date"] = str(g["date"])
                            s[1]["history"].append(g)

        return stats


class MyHistoryView(object):

    def __init__(self, username: str, gateway: str):
        self.username = username
        self.gateway = gateway

        self.db = DBHistory(self.gateway)

    def get(self, limit: int = -1):
        if limit == -1:
            return self.db.get_history(self.username)
        else:
            return self.db.get_history_last(self.username, limit)

    def get_solo(self):
        return self.db.get_solo_history(self.username)


class GamesPlayedView(MyHistoryView):

    def get(self):
        data = self.db.get_history(self.username)

        per_day = {}
        for game in data:
            if str(game["date"].date()) not in per_day:
                per_day[str(game["date"].date())] = 0
            per_day[str(game["date"].date())] += 1
        return per_day


class DBStateView(object):

    def __init__(self):
        self.db = DBState()

    def get(self):
        return self.db.get_entries_count()


class GamesStatsView(object):

    def __init__(self, gateway: str):
        self.db = DBGamesStats(gateway)

    def _get_maps(self):
        maps = self.db.extract_maps()
        maps_info = {
            1: [],  # ...
            2: [],
            3: [],  # ...
            4: [],
            5: [],  # ...
            6: [],
            7: [],  # ...
            8: [],
        }
        # TODO round correctly
        for m in maps:
            if len(maps_info[int(round(m["value"]["players"], 0))]) < 10:
                maps_info[int(round(m["value"]["players"], 0))].append(m)
        return maps_info

    def _get_races(self):
        races_stats = self.db.extract_races()
        races_names = ["Human", "Orc", "Night Elf", "Undead"]
        races_repr = []
        for r in races_stats:
            if r["_id"] in races_names:
                races_repr.append((r["_id"], r["value"]))
        return races_repr

    def _get_players(self):
        players = self.db.extract_top_players()
        p_list = []
        for p in players:
            p["name"] = p.pop("_id")
            p_list.append(p)
        return p_list

    def get(self):
        return {
            "maps": self._get_maps(),
            "players": self._get_players(),
            "races": self._get_races(),
        }
