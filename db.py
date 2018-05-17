from urllib.parse import quote_plus
from pymongo import MongoClient
from typing import Dict
from log import LOG

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

        # self.client = MongoClient(uri)
        self.db = MongoClient(uri).battle
        self.gateway = gateway.lower()+"_games"

    @property
    def collection(self):
        return self.db[self.gateway]

    def get_by_id(self, game_id) -> Dict:
        return self.db[self.gateway].find_one({"game_id": game_id})

    def insert(self, data) -> None:
        LOG.debug(f"Save {data} to DB.")
        self.db[self.gateway].insert_one(data)

    def fix_game_len(self):
        """
        Fix old records that had game len as a string.
        """
        broken_lens = self.db[self.gateway].find(
            {"length": {'$regex': 'minutes'}})
        for g in broken_lens:
            new_len = int(g['length'].split(" ")[0])
            LOG.info(f"Fix {g['game_id']}, from {g['length']} to {new_len}.")
            self.db[self.gateway].update_one({"game_id": g["game_id"]},
                                             {"$set": {"length": new_len}})
