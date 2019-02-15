from wc3rivals.utils import db
from wc3rivals.utils.log import LOG

from pymongo import TEXT
from pymongo import errors
from bson.code import Code


ladders = ["Lordaeron", "Azeroth", "Northrend"]


def index_usernames_db():
    """This index used in Header.vue to earch for usernames"""
    for l in ladders:
        usernames = db.UsernamesDB(l)
        col = usernames.collection_usernames
        if "value_1" not in col.index_information().keys():
            print(f"Create index for {l}#usernames#value.")
            col.create_index('value')


def index_history_db():
    for l in ladders:
        usernames = db.HistoryDB(l)
        col = usernames.collection
        if "players" not in col.index_information().keys():
            print(f"Create index for {l}_games#players.")
            col.create_index('players')
        if "game_id" not in col.index_information().keys():
            print(f"Create index for {l}_games#game_id.")
            col.create_index('game_id')

        if "players_lower_1" in col.index_information().keys():
            print(f"Delete index for {l}_game#players_lower.")
            col.drop_index('players_lower_1')


def up():
    index_usernames_db()
    index_history_db()


if __name__ == "__main__":
    up()
