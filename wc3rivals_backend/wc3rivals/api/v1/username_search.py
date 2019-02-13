import json
from wc3rivals.utils import db
from wc3rivals.utils import utils


class UserNameSearch:
    def __init__(self, gateway: str, username: str):
        self.gateway = utils.GATEWAY_MAP[gateway]
        self.username = username

    def generate_response(self):
        resp = []
        if len(self.username) >= 3:
            resp = db.UsernamesDB(self.gateway).search(self.username)

        return json.dumps(resp)
