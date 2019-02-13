from wc3rivals.utils import db
from wc3rivals.utils.log import LOG

from pymongo import TEXT
from pymongo import errors
from bson.code import Code


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


def retry_cursor(fn):
    def wrapper(*arg, **kwargs):
        retry = 3
        while retry > 0:
            try:
                fn()
            except errors.CursorNotFound as err:
                LOG.info(f"Error: {err}.")
                if retry == 0:
                    raise
                retry -= 1
    return wrapper


@retry_cursor
def update_usernames_db():
    ladders = ["Lordaeron", "Azeroth", "Northrend"]
    for l in ladders:
        LOG.info(f"Connect to games {l}...")
        col = db.DB(l).collection
        LOG.info(f"Connect to usernames {l}...")
        usernames = db.UsernamesDB(l)

        LOG.info(f"Collect all games.")
        all_items = db.DB(l).collection.find()
        LOG.info(f"Collected all games.")
        for item in all_items:
            # LOG.info(f"Check {item}.")
            for name in item["players"]:
                if not usernames.is_exist(name):
                    LOG.info(f"Create {name}.")
                    usernames.insert(name)


def index_usernames_db():
    ladders = ["Lordaeron", "Azeroth", "Northrend"]
    for l in ladders:
        usernames = db.UsernamesDB(l)
        col = usernames.collection_usernames
        if "value_text" not in col.index_information().keys():
            # col.create_index([('value', TEXT)])
            col.create_index('value')


class PlayerUsernamesStats(object):
    map_fn = Code(
        """
        function(){
            if (this.players.length === 2){
                this.players.forEach(function(z){
                    emit(z, z.toLowerCase());
                });
            };
        }
    """
    )

    reduce_fn = Code(
        """
        function(k, v){
            return v[0];
        }
    """
    )

    @classmethod
    def build(cls):
        ladders = ["Lordaeron", "Azeroth", "Northrend"]
        for l in ladders:
            db.DB(l).collection.map_reduce(
                cls.map_fn, cls.reduce_fn, l.lower() + "_usernames"
            )


def up():
    # create_playes_lower_field()
    # create_players_lower_index()
    # create_collection_players_text_index()

    PlayerUsernamesStats.build()
    index_usernames_db()
    # update_usernames_db()


if __name__ == "__main__":
    up()
