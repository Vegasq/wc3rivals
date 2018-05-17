#!/usr/bin/env python3.6

import argparse
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
import urllib

from bs4 import BeautifulSoup
from bs4.element import Tag as BSTag

from gamesparser import GamePageParser
from db import DB
from log import LOG


class UserNotFound(Exception):
    """In case of unavailable User profile"""
    pass


class ProfileHistoryParser(object):
    """
    ProfileHistoryParser - collect information about games played
    by specified user.
    """

    def __init__(self, args: argparse.Namespace, username: str,
                 gateway: str) -> None:
        """
        :param args: Settings
        :param username: Battle.Net username
        :param gateway: Battle.Net classic Realm
        """
        self.args = args
        self.username = username
        self.gateway = gateway

        self.game_matches = []

        self.database = DB(self.gateway)

    def _get_history_page_count(self) -> int:
        """Returns total count of pages with games"""
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

        if soup.find("title"):
            if "Player Full Game Listings" not in soup.find( "title").text:
                raise UserNotFound(
                    "Title: %s, url %s" % (soup.find("title").text, url))

        pages = soup.find_all("td", class_="rankingFiller")
        if pages and pages[0].find_all("a"):
            last_page = int(pages[0].find_all("a")[-1].text)
        else:
            last_page = 1
        return last_page

    def _parse_game_tr(self, game: BSTag) -> None:
        """Extract GameID and send it to GamePageParser"""
        game_uri = game.find(class_="rankingRow").find("a").attrs["href"]
        parsed_url = urlparse(game_uri)
        parsed_query = parse_qs(parsed_url.query)

        game_match_id = int(parsed_query["GameID"][0])

        GamePageParser(gateway=self.gateway, game_id=game_match_id,
                       db=self.database).fetch()

    def fetch_page(self, page: int) -> None:
        """
        Read history page, and parse games one-by-one.

        :param page: page number to request.
        """
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
            self._parse_game_tr(game)

    def fetch(self) -> None:
        """Collect information about player games and save it to DB."""
        LOG.info(f"Fetch history for {self.username}.")

        try:
            total_pages = self._get_history_page_count()
        except UserNotFound as e:
            LOG.debug(f"User not found {e}")
            return

        for i in range(1, total_pages+1):
            LOG.debug(f"Read page {i}.")

            exit_now = False
            self.fetch_page(page=i)

            self._save()

            if exit_now:
                return

    def check_game_in_db(self, game_id: int) -> bool:
        """
        Check if GameID already exists in database.

        :param game_id: Uniq Battle.Net game ID.
        :return: True if game already in DB, False if not.
        """
        data = self.database.get_by_id(game_id)
        LOG.debug("check_game_in_db", data)
        if data:
            return True
        return False

    def _save(self) -> None:
        """
        Save all games from buffer to DB
        """
        for g in self.game_matches:
            LOG.debug("save game ", g)
            if not self.check_game_in_db(g.id):
                self.database.insert(g.generate_json())
        self.game_matches = []

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
    def __init__(self, args: argparse.Namespace, gateway: str) -> None:
        """
        :param args: Settings
        :param gateway: Battle.Net classic Realm
        """
        self.gateway = gateway
        self.player_counter = 0
        self.args = args

    def _get_ladder_page_count(self) -> int:
        """Returns count of pages with games"""
        url = (f"http://classic.battle.net/war3/ladder/w3xp-ladder-solo.aspx"
               f"?Gateway={self.gateway}")
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        pages = soup.find_all("td", class_="rankingFiller")
        last_page = int(pages[0].find_all("a")[-1].text)
        return last_page

    def fetch(self) -> None:
        """Read all players from ladder one by one."""
        LOG.info(f"Fetch ladder for {self.gateway}.")
        total_pages = self._get_ladder_page_count()

        if self.args.max_per_user != -1:
            new_total_pages = int(self.args.max_per_user / 20)
            if total_pages > new_total_pages:
                total_pages = new_total_pages

        for i in range(1, total_pages+1):
            self.fetch_page(i)

    def fetch_page(self, page: int) -> None:
        """Read single page from battle.net."""
        url = (f"http://classic.battle.net/war3/ladder/w3xp-ladder-solo.aspx"
               f"?Gateway={self.gateway}&"
               f"PageNo={page}")
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')
        names = soup.find_all("span", class_="rankingName")
        for name in names:
            n = name.find("a")
            self.player_counter += 1
            LOG.info(f"Ladder placement #{self.player_counter}")

            parsed_url = urlparse(n.attrs["href"])
            parsed_query = parse_qs(parsed_url.query)
            p = ProfileHistoryParser(
                self.args,
                username=urllib.parse.quote(parsed_query["PlayerName"][0]),
                gateway=self.gateway)
            p.fetch()


def main():
    parser = argparse.ArgumentParser()

    ladders = ["Lordaeron", "Azeroth", "Northrend", "Kalimdor"]
    parser.add_argument("--gateway", help="Specify gateway", choices=ladders)
    parser.add_argument("--max-per-user", help="Total games to parse",
                        type=int, default=-1)
    args = parser.parse_args()

    Ladder(args, args.gateway).fetch()


if __name__ == "__main__":
    main()