#!/usr/bin/env python3.6

"""
GameParser:

Parses all game in Battle.Net one-by-one and collect information in database.
"""

from bs4 import BeautifulSoup
import pymongo
import requests

import argparse
from datetime import datetime
from typing import List, Dict
import json

from db import DB
from log import LOG
from unused import unused


__author__ = "Mykola Yakovliev"
__copyright__ = "Copyright 2018, Mykola Yakovliev"
__credits__ = ["Mykola Yakovliev"]
__license__ = "Proprietary software"
__version__ = "1.0"
__maintainer__ = "Mykola Yakovliev"
__email__ = "vegasq@gmail.com"
__status__ = "Production"


class Player(dict):
    """
    Player representation.
    Inherit dict since we need some base class that can be serialized by
    pymongo.
    """
    @property
    def username(self) -> str:
        return self["username"]

    @username.setter
    def username(self, value) -> None:
        self["username"] = value

    @property
    def race(self) -> str:
        return self["race"]

    @race.setter
    def race(self, value) -> None:
        self["race"] = value

    @property
    def result(self) -> str:
        return self["result"]

    @result.setter
    def result(self, value) -> None:
        self["result"] = value

    def __str__(self) -> str:
        return (f"User: {self.username}\nRace: {self.race}\n"
                f"Result: {self.result}")

    def __repr__(self) -> str:
        return json.dumps({"username": self.username,
                           "race": self.race,
                           "result": self.result})


class LastSavedGameSelector(object):
    """
    Return last known game.

    Usage:
    >>> game_obj = LastSavedGameSelector("Lordaeron").last()
    """

    def __init__(self, gateway: str) -> None:
        """
        :param gateway: Battle.Net classic Realm
        """
        self.db = DB(gateway)

    def last(self) -> int:
        # Return game with biggest game_id
        return self.db.collection.find_one(
            sort=[("game_id", pymongo.DESCENDING)])

    def first(self) -> int:
        # Return game with smallest game_id
        return self.db.collection.find_one(
            sort=[("game_id", pymongo.ASCENDING)])


class GamePageParser(object):
    """
    GamePageParser - downloads game page from Battle.Net site,
    parses it and saves data in DB.

    Smart enough to ignore duplicates.
    """

    def __init__(self, gateway: str, game_id: int, db: DB) -> None:
        """
        :param gateway: Battle.Net classic Realm
        :param game_id: Uniq BNet game ID
        :param db: Instance of DB
        """
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
        """
        Collect players information like:
        Player(
            username,
            race,
            result
        )
        """
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
        """
        Collect players information like:
        Player(
            level,
            xp,
            xp_diff
        )
        """
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
        """
        Collect game information like:
        {
            map,
            date,
            type,
            length
        }
        """
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
        if "minutes" in match_len:
            match_len = int(match_len.split()[0])
        else:
            LOG.error("Unknown length {match_len}")
            match_len = 0

        LOG.debug("match_length", match_len)
        # END match_length

        return {
            "map": match_map,
            "date": match_date,
            "type": match_type,
            "length": match_len
        }

    def fetch(self) -> bool:
        """
        Parse game page.

        :return: True if success and False if other case.
        """
        if self.db.get_by_id(self.game_id):
            LOG.info(f"Game {self.gateway}#{self.game_id} exists.")
            return True

        url = (f"http://classic.battle.net/war3/ladder/w3xp-game-detail.aspx"
               f"?Gateway={self.gateway}&GameID={self.game_id}")
        data = requests.get(url)
        self.soup = BeautifulSoup(data.text, 'html.parser')

        if not self.soup.find("b") or "error" in self.soup.find(
                "b").text.lower():
            LOG.error("Failed to parse page: {}".format(
                self.soup.find("b").text))
            return False

        self.stats = self._parse_stats()
        self.stats["players_data"] = self._parse_players()

        self.stats["players"] = [p.username
                                 for p in self.stats["players_data"]]
        levels = self._parse_levels()
        for i, p in enumerate(self.stats["players_data"]):
            self.stats["players_data"][i].update(levels[i])

        self.stats["game_id"] = self.game_id
        self.stats["gateway"] = self.gateway

        self.db.insert(self.stats)
        LOG.info(f"Game {self.gateway}#{self.game_id} saved.")

        return True


class GPManager(object):
    """
    GameParser Manager:
    - Detect where to start parsing based on cli params.
    - Calls GamePageParser.fetch() for each entry.
    - Quits once errors_pool overflows. It works this way cause sometimes
      Bnet skips game IDs. And once in a while we can see game that not exists,
      when games around it are fine. So far I have seen only single skipped ID
      but in case of multiple skipped IDs we wait for 10 unknown games in a row
      before assume we at the end.
    """

    def __init__(self, gateway: str, new: bool=True, init: int=0):
        """
        :param gateway: Battle.Net classic Realm
        :param new: If True increase GameID each iteration.
                    If False decrease GameID each iteration.
        :param init: Game ID for start position
        """
        self.gateway = gateway
        self.new = new
        self.game_id = init
        self.errors_pool = 0

        self.db = DB(gateway)

    def start(self) -> None:
        """
        Start parsing Battle.Net games one-by-one.
        """
        if self.game_id == -1:
            lsgs = LastSavedGameSelector(self.gateway)
            try:
                # if self.new:
                #     self.game_id = lsgs.last()["game_id"] + 1
                # else:
                #     self.game_id = lsgs.first()["game_id"] - 1
                self.game_id = lsgs.last()["game_id"]
            except TypeError:
                LOG.error("Database is empty. Use --init-id to bootstrap.")
                exit()

        while True:
            if self.game_id <= 0:
                LOG.info("Last game parsed.")
                return

            if self.new:
                gpp = GamePageParser(self.gateway, self.game_id, db=self.db)
                success = gpp.fetch()

                if not success:
                    self.errors_pool += 1
                elif self.errors_pool > 0 and success:
                    self.errors_pool -= 1

                if self.errors_pool >= 10:
                    LOG.error("More than 10 errors in a row. Exit.")
                    exit()

                if self.new:
                    self.game_id += 1
                else:
                    self.game_id -= 1
            else:
                LOG.info("Parsing old games")
                ids = unused(self.db, self.game_id)
                LOG.info(f"Found {len(ids)} not parsed games.")
                for i in ids:
                    gpp = GamePageParser(self.gateway, i, db=self.db)
                    gpp.fetch()
                self.game_id -= 1000


def main() -> None:
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
