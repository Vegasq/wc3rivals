import json
from wc3rivals.utils import db


class Stats:
    def generate_response(self):
        return json.dumps(db.StateDB().get_entries_count())
