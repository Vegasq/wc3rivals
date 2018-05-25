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


class DBConnection(object):

    def __init__(self):
        if settings.username and settings.password:
            uri = "mongodb://%s:%s@%s" % (
                quote_plus(settings.username),
                quote_plus(settings.password),
                settings.hostname,
            )
        else:
            uri = "mongodb://%s" % settings.hostname

        self._db = MongoClient(uri).battle


class DB(DBConnection):

    def __init__(self, gateway: str) -> None:
        super().__init__()
        self.set_gateway(gateway)

    def set_gateway(self, gateway: str):
        self._gateway = gateway.lower()

        self._games_table = gateway.lower() + "_games"
        self._maps_table = gateway.lower() + "_maps"
        self._players_table = gateway.lower() + "_players"
        self._races_table = gateway.lower() + "_races"

    @property
    def collection(self):
        return self._db[self._games_table]

    @property
    def collection_maps(self):
        return self._db[self._maps_table]

    @property
    def collection_players(self):
        return self._db[self._players_table]

    @property
    def collection_races(self):
        return self._db[self._races_table]

    def get_by_id(self, game_id) -> Dict:
        return self.collection.find_one({"game_id": game_id})

    def insert(self, data) -> None:
        LOG.debug(f"Save {data} to DB.")
        self.collection.insert_one(data)

    def get_by_range(self, low, high):
        LOG.info(f"Collect entries between {low} and {high}")
        return self.collection.find(
            {"$and": [{"game_id": {"$gte": low}}, {"game_id": {"$lte": high}}]}
        ).sort("game_id", 1)


class DBTopOpponents(DB):

    def get_solo_games_by_user(self, username: str):
        return self.collection.find(
            {"players": username, "type": "Solo", "length": {"$gt": 3}}
        )

    def get_solo_games_with_users(self, usernames: List[str]):
        return self.collection.find(
            {
                "$and": [{"players": usernames[0]}, {"players": usernames[1]}],
                "type": "Solo",
                "length": {"$gt": 3},
            }
        )


class DBHistory(DB):

    def get_history(self, username: str):
        d = datetime.today() - timedelta(days=90)

        return self.collection.find(
            {"players": username, "length": {"$gt": 3}, "date": {"$gt": d}}
        ).sort("date", -1)

    def get_solo_history(self, username: str):
        d = datetime.today() - timedelta(days=90)

        return self.collection.find(
            {
                "type": "Solo",
                "players": username,
                "length": {"$gt": 3},
                "date": {"$gt": d},
            }
        ).sort("date", -1)

    def get_history_last(self, username: str, limit: int = 5):
        if limit > 50:
            limit = 50
        return (
            self.collection.find({"players": username, "length": {"$gt": 3}})
            .sort("date", -1)
            .limit(limit)
        )


class DBState(DB):

    def __init__(self):
        super(DBState, self).__init__("?")

    def get_entries_count(self):
        data = {
            "Lordaeron": 0,
            "Azeroth": 0,
            "Northrend": 0,
            # "Kalimdor": 0
        }
        for e in data.keys():
            self.set_gateway(e)
            data[e] = self.collection.count()
        return [(k, v) for k, v in data.items()]


class DBGamesStats(DB):

    def extract_top_players(self, limit: int = 10):
        return self.collection_players.find().sort("value", -1).limit(limit)

    def extract_maps(self):
        return self.collection_maps.find({}).sort("value.total_games", -1)

    def extract_races(self):
        return self.collection_races.find()
