import os
import re

from urllib.parse import quote_plus
from pymongo import MongoClient
from typing import Dict, List
from datetime import datetime, timedelta

from wc3rivals.utils.log import LOG


class settings(object):
    hostname = os.environ['WC3IMONGOHOSTNAME']
    username = os.environ['WC3IMONGOUSERNAME']
    password = os.environ['WC3IMONGOPASSWORD']


__author__ = "Mykola Yakovliev"
__copyright__ = "Copyright 2018, Mykola Yakovliev"
__credits__ = ["Mykola Yakovliev"]
__license__ = "Proprietary software"
__version__ = "1.0"
__maintainer__ = "Mykola Yakovliev"
__email__ = "vegasq@gmail.com"
__status__ = "Production"


class DBConnection(object):
    def __init__(self):
        LOG.debug("Connecting to %s as %s." % (settings.hostname,
                                               settings.username))
        if settings.username and settings.password:
            uri = "mongodb://%s:%s@%s" % (
                quote_plus(settings.username),
                quote_plus(settings.password),
                settings.hostname,
            )
        else:
            uri = "mongodb://%s" % settings.hostname

        LOG.debug(f"Create MongoClient for {uri}.")
        self._db = MongoClient(uri).battle
        LOG.debug(f"Connected to db {self._db}.")


class DB(DBConnection):

    def __init__(self, gateway: str) -> None:
        super().__init__()
        self.set_gateway(gateway)

    def set_gateway(self, gateway: str):
        LOG.debug(f"Set gateway {gateway}.")
        self._gateway = gateway.lower()

        self._games_table = gateway.lower() + "_games"
        self._maps_table = gateway.lower() + "_maps"
        self._players_table = gateway.lower() + "_players"
        self._races_table = gateway.lower() + "_races"
        self._usernames_table = gateway.lower() + "_usernames"

    def mark_game_as_failed(self, id: int, reason: str = "") -> None:
        LOG.debug(f"Report game {self._gateway}#{id} as failed.")
        self._db["failed"].insert({
            "gateway": self._gateway,
            "game_id": id,
            "report_date": datetime.now(),
            "reason": reason
        })

    def get_failed_by_id(self, game_id: int) -> Dict:
        LOG.debug(f"Get failed by ID {game_id}.")
        return self._db["failed"].find_one({
            "game_id": game_id,
            "gateway": self._gateway})

    @property
    def collection(self):
        LOG.debug(f"Get collection {self._games_table}.")
        return self._db[self._games_table]

    @property
    def collection_maps(self):
        LOG.debug(f"Get collection {self._maps_table}.")
        return self._db[self._maps_table]

    @property
    def collection_players(self):
        LOG.debug(f"Get collection {self._players_table}.")
        return self._db[self._players_table]

    @property
    def collection_races(self):
        LOG.debug(f"Get collection {self._races_table}.")
        return self._db[self._races_table]

    @property
    def collection_usernames(self):
        LOG.debug(f"Get collection {self._usernames_table}.")
        return self._db[self._usernames_table]

    def get_by_id(self, game_id) -> Dict:
        LOG.debug(f"Get by ID {game_id}.")
        return self.collection.find_one({"game_id": game_id})

    def insert(self, data) -> None:
        LOG.debug(f"Save {data} to DB.")
        self.collection.insert_one(data)

    def get_by_range(self, low, high):
        LOG.info(f"Collect entries between {low} and {high}")
        return self.collection.find(
            {"$and": [{"game_id": {"$gte": low}}, {"game_id": {"$lte": high}}]}
        ).sort("game_id", 1)

    # def real_username(self, username: str):
    #     game = self.collection.find_one({"players_lower": username.lower()})
    #     if not game:
    #         raise Exception(f"User {username} not found in {self._gateway}.")
    #     for player in game['players']:
    #         if player.lower() == username.lower():
    #             return player
    #     LOG.error(f"Can't find real username for {username}")
    #     return username


class HistoryDB(DB):
    def get_history(self, username: str):
        LOG.debug(f"Collect history for {username}.")

        d = datetime.today() - timedelta(days=90)
        return self.collection.find(
            {"players": username,
             "length": {"$gt": 3}, "date": {"$gt": d}}
        ).sort("date", -1)

    def get_solo_history(self, username: str):
        LOG.debug(f"Collect solo history for {username}.")
        d = datetime.today() - timedelta(days=90)

        return self.collection.find(
            {
                "type": "Solo",
                "players": username,
                "length": {"$gt": 3},
                "date": {"$gt": d},
            }
        ).sort("date", -1)

    def get_solo_history_all_time(self, username: str):
        LOG.debug(f"Collect solo history for {username}.")

        return self.collection.find(
            {
                "type": "Solo",
                "players": username,
                "length": {"$gt": 3},
            }
        )

    def get_history_last(self, username: str, limit: int = 5):
        LOG.debug(f"Collect last history for {username}.")
        if limit > 50:
            limit = 50
        return (
            self.collection.find({"players": username,
                                  "length": {"$gt": 3}})
            .sort("date", -1)
            .limit(limit)
        )


class OpponentsDB(DB):
    def get_solo_games_by_user(self, username: str):
        LOG.debug(f"Collect solo games for {username}.")
        return self.collection.find(
            {"players": username,
             "type": "Solo", "length": {"$gt": 3}}
        )

    def get_solo_games_with_users(self, usernames: List[str]):
        LOG.debug(f"Collect solo games for {usernames}.")
        return self.collection.find(
            {
                "$and": [{"players": usernames[0]},
                         {"players": usernames[1]}],
                "type": "Solo",
                "length": {"$gt": 3},
            }
        )


class StateDB(DB):
    def __init__(self):
        super(StateDB, self).__init__("?")

    def get_entries_count(self):
        LOG.debug(f"Collect entry count.")
        data = {
            "Lordaeron": 0,
            "Azeroth": 0,
            "Northrend": 0,
        }
        for e in data.keys():
            self.set_gateway(e)
            data[e] = self.collection.count()
        return [(k, v) for k, v in data.items()]


class NotablePlayersDB(DBConnection):
    def get_players(self):
        players = [p for p in self._db['notable_players'].find()]
        for p in players:
            del p['_id']
        return players


class UsernamesDB(DB):
    def insert(self, username: str):
        self.collection_usernames.insert({
            '_id': username,
            'value': username.lower()
        })

    def is_exist(self, username: str) -> str:
        return self.collection_usernames.find_one({
            'value': username.lower()
        })

    def search_one(self, username: str) -> str:
        return str(self.collection_usernames.find_one({
            'value': username.lower()
        })["_id"])

    def search(self, username: str) -> List:
        results = self.collection_usernames.find(
            {'value': {
                '$regex': username}}).limit(10)
        if not results:
            return []
        return [str(u['_id']) for u in results]

    def insert_if_not_exist(self, username: str):
        if not self.is_exist(username):
            self.insert(username)

    # def real_username(self, username: str):
    #     game = self.collection.find_one({"players_lower": username.lower()})
    #     if not game:
    #         raise Exception(f"User {username} not found in {self._gateway}.")
    #     for player in game['players']:
    #         if player.lower() == username.lower():
    #             return player
    #     LOG.error(f"Can't find real username for {username}")
    #     return username
