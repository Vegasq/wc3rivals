from urllib.parse import quote_plus
from pymongo import MongoClient
from typing import Dict, List
from datetime import datetime, timedelta

from wc3inside.utils.log import LOG


try:
    from wc3inside.settings import settings
except ImportError:
    class settings(object):
        hostname = "localhost"
        username = ""
        password = ""


__author__ = "Mykola Yakovliev"
__copyright__ = "Copyright 2018, Mykola Yakovliev"
__credits__ = ["Mykola Yakovliev"]
__license__ = "Proprietary software"
__version__ = "1.0"
__maintainer__ = "Mykola Yakovliev"
__email__ = "vegasq@gmail.com"
__status__ = "Production"


class DB(object):
    def __init__(self, gateway: str) -> None:
        if settings.username and settings.password:
            uri = "mongodb://%s:%s@%s" % (quote_plus(settings.username),
                                          quote_plus(settings.password),
                                          settings.hostname)
        else:
            uri = "mongodb://%s" % settings.hostname

        self._db = MongoClient(uri).battle
        self._gateway = gateway.lower()+"_games"

    def set_gateway(self, gateway: str):
        self._gateway = gateway.lower()+"_games"

    @property
    def collection(self):
        return self._db[self._gateway]

    def get_by_id(self, game_id) -> Dict:
        return self.collection.find_one({"game_id": game_id})

    def insert(self, data) -> None:
        LOG.debug(f"Save {data} to DB.")
        self.collection.insert_one(data)

    def get_by_range(self, low, high):
        LOG.info(f"Collect entries between {low} and {high}")
        return self.collection.find({
            "$and": [
                {"game_id": {"$gte": low}},
                {"game_id": {"$lte": high}}
            ]
        }).sort("game_id", 1)


class EnemiesDB(DB):
    def get_solo_games_by_user(self, username: str):
        return self.collection.find(
            {"players": username, "type": "Solo", "length": {"$gt": 3}})

    def get_solo_games_with_users(self, usernames: List[str]):
        return self.collection.find(
            {
                "$and": [
                    {"players": usernames[0]},
                    {"players": usernames[1]}
                ],
                "type": "Solo", "length": {"$gt": 3}
            }
        )


class HistoryDB(DB):
    def get_history(self, username: str):
        d = datetime.today() - timedelta(days=90)

        return self.collection.find({
            "players": username,
            "length": {"$gt": 3},
            "date": {"$gt": d}
        }).sort("date", -1)

    def get_solo_history(self, username: str):
        d = datetime.today() - timedelta(days=90)

        return self.collection.find({
            "type": "Solo",
            "players": username,
            "length": {"$gt": 3},
            "date": {"$gt": d}
        }).sort("date", -1)

    def get_history_last(self, username: str, limit: int=5):
        if limit > 50:
            limit = 50
        return self.collection.find({
            "players": username,
            "length": {"$gt": 3}
        }).sort("date", -1).limit(limit)


class DBState(DB):
    def __init__(self):
        super(DBState, self).__init__("?")
        self.envs = ["Lordaeron", "Azeroth", "Northrend"]

    def get_entries_count(self):
        data = {
            "Lordaeron": 0,
            "Azeroth": 0,
            "Northrend": 0,
            # "Kalimdor": 0
        }
        for e in self.envs:
            self.set_gateway(e)
            data[e] = self.collection.count()
        return [(k, v) for k, v in data.items()]
