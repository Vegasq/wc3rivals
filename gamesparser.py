#!/usr/bin/env python3.6

from bs4 import BeautifulSoup
import pymongo
import requests

import argparse
from datetime import datetime
from typing import List, Dict
import json

from db import DB
from log import LOG


class Player(dict):
    @property
    def username(self):
        return self["username"]

    @username.setter
    def username(self, value):
        self["username"] = value

    @property
    def race(self):
        return self["race"]

    @race.setter
    def race(self, value):
        self["race"] = value

    @property
    def result(self):
        return self["result"]

    @result.setter
    def result(self, value):
        self["result"] = value

    def __str__(self) -> str:
        return (f"User: {self.username}\nRace: {self.race}\n"
                f"Result: {self.result}")

    def __repr__(self):
        return json.dumps({"username": self.username,
                           "race": self.race,
                           "result": self.result})


class LastSavedGameSelector(object):
    """
    Return last known game.

    Usage:
    >>> game_obj = LastSavedGameSelector("Lordaeron").get()
    """

    def __init__(self, gateway: str):
        self.db = DB(gateway)

    def last(self) -> int:
        return self.db.collection.find_one(
            sort=[("game_id", pymongo.DESCENDING)])

    def first(self) -> int:
        return self.db.collection.find_one(
            sort=[("game_id", pymongo.ASCENDING)])


class GamePageParser(object):
    def __init__(self, gateway: str, game_id: int, db: DB) -> None:
        LOG.info(f"Parse game {gateway}#{game_id}.")
        self.gateway = gateway
        self.game_id = game_id

        if db:
            self.db = db
        else:
            self.db = DB(gateway)

        self.soup = None
        self.stats = None

    def _parse_players(self) -> List[Player]:
        ranking_row_left = self.soup.find_all("td", class_="rankingRowLeft")

        players = []
        for i in range(0, len(ranking_row_left), 3):
            player = ranking_row_left[i:i+3]

            p = Player()
            p.username = player[0].text
            p.race = player[1].text
            p.result = player[2].text

            players.append(p)

        return players

    def _parse_levels(self) -> List[Dict]:
        levels = []
        levels_row = self.soup.find_all(class_="rankingRow")
        for i in range(0, len(levels_row), 4):
            player = levels_row[i:i+4]

            if player[1].text:
                level = int(player[1].text)
            else:
                level = 0

            if player[2].text:
                xp = int(player[2].text.replace(",", ""))
            else:
                xp = 0

            if player[3].text:
                xp_diff = int(player[3].text.replace(",", ""))
            else:
                xp_diff = 0

            levels.append({"level": level, "xp": xp, "xp_diff": xp_diff})
        return levels

    def _parse_stats(self) -> Dict:
        player_stats_data_left = self.soup.find_all(
            "td", class_="playerStatsDataLeft")

        # START date
        match_date = " ".join(player_stats_data_left[0].text.split()[:-1])
        match_date = datetime.strptime(match_date, "%m/%d/%Y %I:%M:%S %p")
        LOG.debug("match_date", match_date)
        # END date

        # START map
        match_map = self.soup.find_all(
            "td", class_="playerStatsDataLeft")[1].text
        LOG.debug("match_map", match_map)
        # END map

        # START match_type
        match_type = self.soup.find_all(
            "td", class_="playerStatsDataLeft")[2].text
        LOG.debug("match_type", match_type)
        # END match_type

        # START match_length
        match_len = self.soup.find_all(
            "td", class_="playerStatsDataLeft")[3].text
        LOG.debug("match_length", match_len)
        # END match_length

        return {
            "map": match_map,
            "date": match_date,
            "type": match_type,
            "length": match_len
        }

    def fetch(self) -> bool:
        if self.db.get_by_id(self.game_id):
            LOG.info(f"Game {self.gateway}#{self.game_id} exists.")
            return

        url = (f"http://classic.battle.net/war3/ladder/w3xp-game-detail.aspx"
               f"?Gateway={self.gateway}&GameID={self.game_id}")
        data = requests.get(url)
        self.soup = BeautifulSoup(data.text, 'html.parser')

        if "error" in self.soup.find("b").text.lower():
            LOG.error("Failed to parse page: {}".format(
                self.soup.find("b").text))
            return False

        self.stats = self._parse_stats()
        self.stats["players_data"] = self._parse_players()

        self.stats["players"] = [p.username for p in self.stats["players_data"]]
        levels = self._parse_levels()
        for i, p in enumerate(self.stats["players_data"]):
            self.stats["players_data"][i].update(levels[i])

        self.stats["game_id"] = self.game_id
        self.stats["gateway"] = self.gateway

        self.db.insert(self.stats)
        LOG.info(f"Game {self.gateway}#{self.game_id} saved.")

        return True


class GPManager(object):
    def __init__(self, gateway: str, new: bool=True, init: int=0):
        self.gateway = gateway
        self.new = new
        self.game_id = init
        self.errors_pool = 0

        self.db = DB(gateway)

    def start(self):
        if self.game_id == -1:
            lsgs = LastSavedGameSelector(self.gateway)
            try:
                if self.new:
                    self.game_id = lsgs.last()["game_id"] + 1
                else:
                    self.game_id = lsgs.first()["game_id"] - 1
            except TypeError:
                LOG.error("Database is empty. Use --init-id to bootstrap.")
                exit()

        while True:
            if self.game_id <= 0:
                LOG.info("Last game parsed.")
                return

            gpp = GamePageParser(self.gateway, self.game_id, db=self.db)
            success = gpp.fetch()

            if not success:
                self.errors_pool += 1

            if self.errors_pool >= 100:
                LOG.error("More than 100 errors in pool. Exit.")
                exit()

            if self.new:
                self.game_id += 1
            else:
                self.game_id -= 1


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--old", action="store_true", help="Parse backwards.")
    ladders = ["Lordaeron", "Azeroth", "Northrend", "Kalimdor"]
    parser.add_argument("--gateway", help="Specify gateway", choices=ladders)
    parser.add_argument("--init-id", help="Initial game_id", type=int,
                        default=-1)

    args = parser.parse_args()

    GPManager(args.gateway, not args.old, args.init_id).start()


if __name__ == "__main__":
    main()
