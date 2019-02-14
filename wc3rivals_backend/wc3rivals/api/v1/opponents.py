import copy
import json
from typing import List, Dict

from wc3rivals.utils.db import OpponentsDB
from wc3rivals.utils import utils


class MatchObject:

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


class Opponents:
    def __init__(self, gateway: str, username_a: str, username_b: str = None):
        self.gateway = utils.GATEWAY_MAP[gateway]
        self.db = OpponentsDB(self.gateway)
        self.username_a = username_a
        self.username_b = username_b

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

    def get_stats(self) -> List:
        username = self.db.real_username(self.username_a)
        all_games = [
            MatchObject(g, username)
            for g in self.db.get_solo_games_by_user(username)
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

    def get_history_among(self):
        # username_a = self.db.real_username(self.username_a)
        # username_b = self.db.real_username(self.username_b)
        username_a = self.username_a
        username_b = self.username_b

        all_games = [
            g for g in self.db.get_solo_games_with_users([username_a,
                                                          username_b])
        ]
        for game in all_games:
            game["date"] = str(game["date"]),
            del game['_id']
        return all_games

    def generate_response(self):
        resp = []
        if self.username_b:
            resp = self.get_history_among()
        else:
            resp = self.get_stats()
        return json.dumps(resp)
