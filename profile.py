#!/usr/bin/env python3.6

from datetime import datetime
import logging
import requests
from typing import List, Dict
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib

from bs4 import BeautifulSoup
from bs4.element import Tag as BSTag
from pymongo import MongoClient


LOG = logging.getLogger("classicbnet")
LOG.setLevel(logging.INFO)

ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

LOG.addHandler(ch)


class AlreadyParsed(Exception):
    pass


class DB(object):
    def __init__(self):
        self.client = MongoClient(host="localhost")
        self.db = MongoClient().battle

    def get_by_id(self, game_id):
        d =  self.db["lordaeron"].find_one({"game_id": game_id})
        # print(d)
        return d

    def insert(self, data):
        # print(data)
        LOG.debug("Save to DB")
        self.db["lordaeron"].insert_one(data)


class Player(object):
    def __init__(self, username: str, gateway: str) -> None:
        self.username = username
        self.gateway = gateway


class GameMatch(object):
    def __init__(self, game_id: int, gateway: str, date: str, game_map: str,
                 winner: Player) -> None:
        self.id = game_id
        self.gateway = gateway
        self.date = date
        self.map = game_map
        self.winner = winner

        self.own_team = []
        self.their_team = []

    def __str__(self):
        return f"{self.winner.username}-vs-{self.their_team[0].username}"

    def add_player(self, player: Player, opponent: bool = True):
        if opponent:
            self.their_team.append(player)
        else:
            self.own_team.append(player)

    def generate_json(self) -> Dict:
        return {
            "player_left": self.own_team[0].username,
            "player_right": self.their_team[0].username,
            "map": self.map,
            "winner": self.winner.username,
            "game_id": self.id,
            "gateway": self.gateway,
            "date": self.date,
        }


class Profile(object):
    def __init__(self, username: str, gateway: str) -> None:
        self.username = username
        self.gateway = gateway
        self.player = Player(username=self.username, gateway=self.gateway)

        self.game_matches = []

        self.wins = 0
        self.looses = 0

        self.database = DB()

    def _get_history_page_count(self) -> int:
        """Returns count of pages with games"""
        page = 1
        url = (f"http://classic.battle.net/war3/ladder/"
               f"w3xp-player-logged-games.aspx"
               f"?Gateway={self.gateway}&"
               f"PlayerName={self.username}&"
               f"SortField=game_date&"
               f"SortDir=Desc&PageNo={page}")
        LOG.debug(f"Read page count from {url}")
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        if "Player Full Game Listings" not in soup.find("title").text:
            raise Exception(
                "User not found. Title: %s" % soup.find("title").text)

        pages = soup.find_all("td", class_="rankingFiller")
        if pages[0].find_all("a"):
            last_page = int(pages[0].find_all("a")[-1].text)
        else:
            last_page = 1
        return last_page

    def _parse_game_tr(self, game: BSTag) -> GameMatch:
        # Parse game type START
        game_match_type = game.find_all(class_="rankingRowLeft")[1].text
        if "Solo" not in game_match_type:
            LOG.debug("Not solo")
            return
        # Parse game type END

        # Parse Game ID START
        game_uri = game.find(class_="rankingRow").find("a").attrs["href"]
        parsed_url = urlparse(game_uri)
        parsed_query = parse_qs(parsed_url.query)

        game_match_id = parsed_query["GameID"][0]
        if self.database.get_by_id(game_match_id):
            raise AlreadyParsed()
        game_match_gateway = parsed_query["Gateway"][0]
        # Parse Game ID END

        # Parse players START
        opponents = game.find(class_="rankingRowAlt"). \
            find_all("tr")[1].find_all("a")
        opponents_list: List[Player] = []
        for opponent in opponents:
            parsed_url = urlparse(opponent.attrs["href"])
            parsed_query = parse_qs(parsed_url.query)
            pl = Player(username=parsed_query["PlayerName"][0],
                        gateway=parsed_query["Gateway"][0])
            opponents_list.append(pl)
        if not opponents_list:
            return

        allies_list = [self.player]

        # Parse players END

        # Parse game date START
        game_match_date = game.find(class_="rankingRowLeft").text
        game_match_date = game_match_date.replace("\n", "")
        game_match_date = game_match_date[0:-3]
        game_match_date = game_match_date.strip()
        game_match_date = datetime.strptime(game_match_date,
                                            "%m/%d/%Y %I:%M %p")
        # Parse game date END

        # Parse map START
        game_match_map = game.find_all(class_="rankingRowLeft")[-2].text
        game_match_map = game_match_map.replace("_ L V", "_LV")
        game_match_map = game_match_map.replace("\n", "")
        # Parse map END

        # Parse winner START
        win_line = game.find_all(class_="rankingRowLeft")[-1].text
        if "Win" in win_line:
            game_match_winner = self.player
            self.wins += 1
        elif opponents_list:
            game_match_winner = opponents_list[0]
            self.looses += 1
        else:
            game_match_winner = Player(username="",
                                       gateway="")
        # Parse winner END

        gm = GameMatch(game_id=game_match_id, gateway=game_match_gateway,
                       date=game_match_date, game_map=game_match_map,
                       winner=game_match_winner)
        for a in allies_list:
            gm.add_player(a, opponent=False)
        for a in opponents_list:
            gm.add_player(a)
        return gm

    def _read_history_page(self, page: int) -> None:
        url = (f"http://classic.battle.net/war3/ladder/"
               f"w3xp-player-logged-games.aspx"
               f"?Gateway={self.gateway}&"
               f"PlayerName={self.username}&"
               f"SortField=game_date&"
               f"SortDir=Desc&PageNo={page}")
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')
        games_on_page = soup.find_all("tr", class_="rankingRow")
        for game in games_on_page:
            gm = self._parse_game_tr(game)
            if gm:
                LOG.info(f"New game found {gm}")
                self.game_matches.append(gm)

    def _read_history(self) -> None:
        total_pages = self._get_history_page_count()
        # if total_pages > 100:
        #     total_pages = 100
        for i in range(1, total_pages+1):
            LOG.debug(f"Read page {i}.")

            exit_now = False
            try:
                self._read_history_page(page=i)
            except AlreadyParsed:
                exit_now = True

            self._save()

            if exit_now:
                return

    def check_game_in_db(self, game_id: int):
        data = self.database.get_by_id(game_id)
        LOG.debug("check_game_in_db", data)
        if data:
            return True
        return False

    def _save(self):
        for g in self.game_matches:
            LOG.debug("save game ", g)
            if not self.check_game_in_db(g.id):
                self.database.insert(g.generate_json())
        self.game_matches = []

    def fetch(self) -> None:
        """Collect information about player games and save it to DB."""
        LOG.info(f"Fetch history for {self.username}.")
        self._read_history()

    # def print_wins(self):
    #     print(f"Wins: {self.wins}\nLooses: {self.looses}")
    #
    # def rematches(self):
    #     names = {}
    #     for g in self.game_matches:
    #         for e in g.their_team:
    #             if e.username not in names:
    #                 names[e.username] = []
    #             names[e.username].append(g.winner.username ==
    #                                      self.player.username)
    #
    #     n = {k: v for k, v in names.items() if len(v) > 1}
    #
    #     n = OrderedDict(sorted(n.items(), key=lambda t: -1 * len(t[1])))
    #
    #     for op, res in n.items():
    #         win = res.count(True)
    #         lose = res.count(False)
    #         print(f"{self.player.username} [{win} x {lose}] {op}")


class Ladder(object):
    def __init__(self, gateway: str):
        self.gateway = gateway

    def _get_ladder_page_count(self) -> int:
        """Returns count of pages with games"""
        url = (f"http://classic.battle.net/war3/ladder/w3xp-ladder-solo.aspx"
               f"?Gateway={self.gateway}")
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        pages = soup.find_all("td", class_="rankingFiller")
        last_page = int(pages[0].find_all("a")[-1].text)
        return last_page

    def fetch(self):
        LOG.info(f"Fetch ladder for {self.gateway}.")
        # url = (f"http://classic.battle.net/war3/ladder/w3xp-ladder-solo.aspx"
        #        f"?Gateway={self.gateway}")
        total_pages = self._get_ladder_page_count()
        for i in range(1, total_pages+1):
            self.fetch_page(i)

    def fetch_page(self, page: int):
        url = (f"http://classic.battle.net/war3/ladder/w3xp-ladder-solo.aspx"
               f"?Gateway={self.gateway}&"
               f"PageNo={page}")
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')
        names = soup.find_all("span", class_="rankingName")
        for name in names:
            n = name.find("a")

            parsed_url = urlparse(n.attrs["href"])
            parsed_query = parse_qs(parsed_url.query)
            p = Profile(
                username=urllib.parse.quote(parsed_query["PlayerName"][0]),
                gateway=self.gateway)
            p.fetch()


ladders = ["Northrend", "Lordaeron", "Azeroth", "Kalimdor"]


if __name__ == "__main__":
    Ladder("Lordaeron").fetch()

# Profile(username="Hero.M.Magic", gateway="Lordaeron").fetch()
