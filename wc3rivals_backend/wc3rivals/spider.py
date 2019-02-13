#!/usr/bin/env python3.6

"""
GameParser:

Parses all game in Battle.Net one-by-one and collect information in database.
"""

from bs4 import BeautifulSoup
import os
import pymongo
import requests
import time

import argparse
from datetime import datetime
import logging
import subprocess
from typing import List, Dict, NewType
import json

from wc3rivals.utils.db import DB
from wc3rivals.utils.log import LOG
from wc3rivals.utils import unused


__author__ = "Mykola Yakovliev"
__copyright__ = "Copyright 2018, Mykola Yakovliev"
__credits__ = ["Mykola Yakovliev"]
__license__ = "Proprietary software"
__version__ = "1.0"
__maintainer__ = "Mykola Yakovliev"
__email__ = "vegasq@gmail.com"
__status__ = "Production"


Race = NewType("Race", str)
BNetRealm = NewType("BNetRealm", str)


CONNECTION_ERROR = "CONNECTION_ERROR"
PARSING_ERROR = "PARSING_ERROR"


class UrlUnavailable(Exception):
    pass


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
    def race(self) -> Race:
        return self["race"]

    @race.setter
    def race(self, value: Race) -> None:
        self["race"] = value

    @property
    def result(self) -> str:
        return self["result"]

    @result.setter
    def result(self, value) -> None:
        self["result"] = value

    def __str__(self) -> str:
        return (f"User: {self.username}\n"
                f"Race: {self.race}\n"
                f"Result: {self.result}")

    def __repr__(self) -> str:
        return json.dumps(
            {"username": self.username,
             "race": self.race,
             "result": self.result}
        )


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

    def __init__(self, gateway: BNetRealm, game_id: int, db: DB) -> None:
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
        LOG.debug(f"Parse players for {self.game_id}.")
        ranking_row_left = self.soup.find_all("td", class_="rankingRowLeft")

        players = []
        for i in range(0, len(ranking_row_left), 3):
            player = ranking_row_left[i: i + 3]

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
        LOG.debug(f"Parse levels for {self.game_id}.")
        levels = []
        levels_row = self.soup.find_all(class_="rankingRow")
        for i in range(0, len(levels_row), 4):
            player = levels_row[i: i + 4]

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
        LOG.debug(f"Parse stats for {self.game_id}.")
        timer = time.time()
        player_stats_data_left = self.soup.find_all(
            "td", class_="playerStatsDataLeft")
        LOG.debug("Get playerStatsDataLeft: %f" % (time.time() - timer))

        # START date
        timer = time.time()
        match_date = " ".join(player_stats_data_left[0].text.split()[:-1])
        match_date = datetime.strptime(match_date, "%m/%d/%Y %I:%M:%S %p")
        LOG.debug("Extract date: %f" % (time.time() - timer))
        # END date

        # START map
        match_map = player_stats_data_left[1].text
        # END map

        # START match_type
        match_type = player_stats_data_left[2].text
        # END match_type

        # START match_length
        match_len = player_stats_data_left[3].text
        if "minutes" in match_len:
            match_len = int(match_len.split()[0])
        else:
            LOG.error(f"Unknown length {match_len}")
            match_len = 0

        # END match_length

        return {
            "map": match_map,
            "date": match_date,
            "type": match_type,
            "length": match_len,
        }

    def get(self, url: str) -> str:
        timer = time.time()

        retry = 5
        while retry > 0:
            retry -= 1
            try:
                LOG.debug(f"GET {url}, #{retry}.")
                data = requests.get(url, timeout=(5, 5))
                LOG.debug(f"GET successful for {url}.")

                LOG.debug("HTTP request to Battle.Net took: "
                          "%f" % (time.time() - timer))
                return data.text

            except requests.exceptions.ConnectionError as err:
                LOG.error(f"Conection error for {url}. "
                           "Sleep for 1 second and retry.")
                time.sleep(1)
            except Exception as err:
                LOG.error(f"Unknown error {err}."
                           "Sleep for 1 second and retry.")
                time.sleep(1)
        raise UrlUnavailable(url)

    def fetch(self) -> bool:
        """
        Parse game page.

        :return: True if success and False if other case.
        """
        LOG.debug(f"Fetch game {self.game_id}.")
        timer = time.time()
        if self.db.get_by_id(self.game_id):
            LOG.info(f"Game {self.gateway}#{self.game_id} exists.")
            return True
        if self.db.get_failed_by_id(self.game_id):
            LOG.info(f"Game {self.gateway}#{self.game_id} found in failed db.")
            return True

        LOG.debug(
            "Check if game exists in DB took: %f" % (time.time() - timer))

        url = (
            f"http://classic.battle.net/war3/ladder/w3xp-game-detail.aspx"
            f"?Gateway={self.gateway}&GameID={self.game_id}"
        )

        timer = time.time()

        try:
            output = self.get(url)
        except UrlUnavailable as err:
            LOG.error(f"Skip {url} due to {err}.")
            self.db.mark_game_as_failed(self.game_id, reason=CONNECTION_ERROR)
            return

        timer = time.time()
        self.soup = BeautifulSoup(output, "html.parser")
        LOG.debug("BeautifulSoup init: %f" % (time.time() - timer))

        if (
            not self.soup.find("b") or
            "error" in self.soup.find("b").text.lower()
        ):
            LOG.error("Failed to parse page.")
            self.db.mark_game_as_failed(self.game_id, reason=PARSING_ERROR)
            return False

        timer = time.time()
        self.stats = self._parse_stats()
        LOG.debug("Parse stats: %f" % (time.time() - timer))

        timer = time.time()
        self.stats["players_data"] = self._parse_players()
        LOG.debug("Parse players: %f" % (time.time() - timer))

        self.stats["players"] = [p.username
                                 for p in self.stats["players_data"]]
        self.stats["players_lower"] = [p.username.lower()
                                       for p in self.stats["players_data"]]

        timer = time.time()
        levels = self._parse_levels()
        LOG.debug("Parse levels: %f" % (time.time() - timer))

        for i, p in enumerate(self.stats["players_data"]):
            self.stats["players_data"][i].update(levels[i])

        self.stats["game_id"] = self.game_id
        self.stats["gateway"] = self.gateway
        LOG.debug("Game parsing took: %f" % (time.time() - timer))

        timer = time.time()
        self.db.insert(self.stats)
        LOG.debug("Save game in DB took: %f" % (time.time() - timer))
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

    def __init__(self, gateway: BNetRealm, new: bool = True, init: int = 0):
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
        self.exit = False

    def _start(self) -> None:
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
            if self.exit:
                return

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
                    LOG.info("More than 10 errors in a row.")
                    self.exit = True

                if self.new:
                    self.game_id += 1
                else:
                    self.game_id -= 1
            else:
                LOG.info("Parsing old games")
                ids = unused.unused(self.db, self.game_id)
                LOG.info(f"Found {len(ids)} not parsed games.")
                for i in ids:
                    gpp = GamePageParser(BNetRealm(self.gateway), i,
                                         db=self.db)
                    gpp.fetch()
                self.game_id -= unused.chunk_size

    def start(self) -> None:
        try:
            self._start()
        except KeyboardInterrupt:
            LOG.info("Quitting...")
            self.exit = True


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--debug", action="store_true", help="Debug")
    parser.add_argument("--old", action="store_true", help="Parse backwards.")
    ladders = ["Lordaeron", "Azeroth", "Northrend", "Kalimdor"]
    parser.add_argument(
        "--gateway", help="Specify gateway", choices=ladders, required=False
    )
    parser.add_argument("--init-id", help="Initial game_id", type=int,
                        default=-1)

    args = parser.parse_args()

    if args.debug:
        LOG.setLevel(logging.DEBUG)

    if not args.gateway:
        gateway = os.environ["WC3IMONGOGATEWAY"]
        LOG.debug(f"Select gateway {gateway} from env.WC3I_GATEWAY.")
    else:
        gateway = args.gateway
        LOG.debug(f"Select gateway {gateway} from env.WC3I_GATEWAY.")

    while True:
        GPManager(BNetRealm(gateway), not args.old, args.init_id).start()
        LOG.info("All games fetched. Sleep for 10 minutes.")
        time.sleep(60 * 10)


if __name__ == "__main__":
    main()
