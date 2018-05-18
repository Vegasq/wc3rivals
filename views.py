
from db import EnemiesDB
from collections import OrderedDict
from typing import List


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


class MyEnemiesView(object):
    def __init__(self, gateway: str):
        self.gateway = gateway
        self.db = EnemiesDB(gateway)

    def get_stats(self, username: str) -> str:
        if username and "," in username:
            usernames = [u.strip() for u in username.split(",")]
            username = usernames[0]
            all_games = [MatchObject(g, username)
                         for g in self.db.get_solo_games_with_users(usernames)]
        else:
            all_games = [MatchObject(g, username)
                         for g in self.db.get_solo_games_by_user(username)]
        enemies = []
        for game in all_games:
            match_enemies = game.get_enemies()
            enemies += match_enemies

        game_history = []
        stats = {}
        for enemy, result in enemies:
            if enemy not in stats:
                stats[enemy] = {
                    "primary_player": username,
                    "secondary_player": enemy,
                    "win": 0,
                    "loss": 0,
                    "state": 0
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

        ordered_stats = sorted(stats.items(),
                               key=lambda x: -1 * (x[1]["win"] + x[1]["loss"]))

        stats = ordered_stats[0:20]
        return stats
