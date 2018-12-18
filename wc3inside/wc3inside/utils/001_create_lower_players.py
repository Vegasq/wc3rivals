from wc3inside.utils import db


def up():
    # Keep lower cased names so we can index them.
    ladders = ["Lordaeron", "Azeroth", "Northrend"]
    for l in ladders:
        col = db.DB(l).collection

        indexed = col.index_information().keys()
        if 'players_lower' not in indexed:
            col.create_index('players_lower')

        all_items = db.DB(l).collection.find({'players_lower': None})
        for item in all_items:
            players_lower = [p.lower() for p in item["players"]]
            col.update(
                {"_id": item["_id"]},
                {"$set": {
                    "players_lower": players_lower
                }}
            )


if __name__ == "__main__":
    up()
