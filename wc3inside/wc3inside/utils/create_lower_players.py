from wc3inside.utils import db
from wc3inside.utils.log import LOG


def up():
    # Keep lower cased names so we can index them.
    ladders = ["Lordaeron", "Azeroth", "Northrend"]
    for l in ladders:
        LOG.info(f"Processibg {l}.")
        col = db.DB(l).collection

        indexed = col.index_information().keys()
        if 'players_lower' not in indexed:
            LOG.info(f"Create `players_lower` index for {l}")
            col.create_index('players_lower')

        all_items = db.DB(l).collection.find({'players_lower': None})
        count_items = db.DB(l).collection.find({'players_lower': None}).count()
        LOG.info(f"We have {count_items} without lower players in {l}.")
        for item in all_items:
            iid = item['_id']
            # LOG.info(f"Working on f{iid}.")
            players_lower = [p.lower() for p in item["players"]]
            col.update(
                {"_id": item["_id"]},
                {"$set": {
                    "players_lower": players_lower
                }}
            )


if __name__ == "__main__":
    up()
