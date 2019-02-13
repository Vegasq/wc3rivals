import os
from flask import Flask, send_file
from flask_cors import CORS

import abc
import copy
import logging
import os
import json

from wc3rivals.utils.log import LOG


from wc3rivals.api.v1 import notable_players as notable_players_api
from wc3rivals.api.v1 import username_search as username_search_api
from wc3rivals.api.v1 import opponents as opponents_api
from wc3rivals.api.v1 import stats as stats_api

app = Flask(__name__)
CORS(app)

if os.path.exists("/app/static"):
    app.static_folder = "/app/static"
else:
    app.static_folder = "/Users/myakovliev/PycharmProjects/" \
                        "wc3rivals/wc3rivals/wc3rivals/static"

LOG.setLevel(logging.DEBUG)


@app.route("/v1/enemies/<gateway>/<username>")
def top_opponents(gateway, username):
    return opponents_api.Opponents(gateway=gateway,
                                   username_a=username).generate_response()


@app.route("/v1/history/<gateway>/<usera>/<userb>")
def history(gateway, usera, userb):
    return opponents_api.Opponents(gateway=gateway,
                                   username_a=usera,
                                   username_b=userb).generate_response()


@app.route("/v1/db/stats")
def stats():
    return stats_api.Stats().generate_response()


@app.route('/v1/usernames/<string:gateway>/<string:username>')
def username_search(gateway: str, username: str):
    return username_search_api.UserNameSearch(
        gateway=gateway, username=username).generate_response()


@app.route('/v1/notable_players')
def notable_players():
    return notable_players_api.NotablePlayers().generate_response()


if __name__ == "__main__":
    app.run()
