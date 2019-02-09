from wc3inside.utils import db
from wc3inside.utils.log import LOG

from pymongo import TEXT


def create_collection_players_text_index():
    """This index will let us create dropdown with nme suggestions.

    :return:
    """
    ladders = ["Lordaeron", "Azeroth", "Northrend"]

    for l in ladders:
        LOG.info(f"Processibg {l}.")
        p_col = db.DB(l).collection_players

        if "_id_text" not in p_col.index_information().keys():
            p_col.create_index([('_id', TEXT)])


def create_players_lower_index():
    """This way we can search games using case insensetive names."""
    ladders = ["Lordaeron", "Azeroth", "Northrend"]

    for l in ladders:
        LOG.info(f"Processibg {l}.")
        col = db.DB(l).collection

        indexed = col.index_information().keys()
        if 'players_lower' not in indexed:
            LOG.info(f"Create `players_lower` index for {l}")
            col.create_index('players_lower')


def create_playes_lower_field():
    # Keep lower cased names so we can index them.
    ladders = ["Lordaeron", "Azeroth", "Northrend"]
    for l in ladders:
        LOG.info(f"Processibg {l}.")
        col = db.DB(l).collection

        all_items = db.DB(l).collection.find({'players_lower': None})
        count_items = db.DB(l).collection.find({'players_lower': None}).count()
        LOG.info(f"We have {count_items} without lower players in {l}.")
        for item in all_items:
            players_lower = [p.lower() for p in item["players"]]
            col.update(
                {"_id": item["_id"]},
                {"$set": {
                    "players_lower": players_lower
                }}
            )


def up():
    create_playes_lower_field()
    create_players_lower_index()
    create_collection_players_text_index()


if __name__ == "__main__":
    up()
