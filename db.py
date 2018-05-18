from urllib.parse import quote_plus
from pymongo import MongoClient
from typing import Dict, List
from log import LOG
from datetime import datetime, timedelta


try:
    from settings import settings
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

    @property
    def collection(self):
        return self._db[self._gateway]

    def get_by_id(self, game_id) -> Dict:
        return self.collection.find_one({"game_id": game_id})

    def insert(self, data) -> None:
        LOG.debug(f"Save {data} to DB.")
        self.collection.insert_one(data)


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
