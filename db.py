from pymongo import MongoClient
from typing import Dict
from log import LOG


class DB(object):
    def __init__(self, gateway: str) -> None:
        self.client = MongoClient(host="localhost")
        self.db = MongoClient().battle
        self.gateway = gateway.lower()+"_games"

    @property
    def collection(self):
        return self.db[self.gateway]

    def get_by_id(self, game_id) -> Dict:
        return self.db[self.gateway].find_one({"game_id": game_id})

    def insert(self, data) -> None:
        LOG.debug(f"Save {data} to DB.")
        self.db[self.gateway].insert_one(data)
