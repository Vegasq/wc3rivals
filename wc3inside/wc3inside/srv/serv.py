import os
from flask import Flask, send_file
import abc
import logging
import os
# import web
import json
# import jinja2

from wc3inside.utils.log import LOG

from wc3inside.srv.views import (
    TopOpponentsView,
    MyHistoryView,
    GamesPlayedView,
    DBStateView,
    GamesStatsView,
)


app = Flask(__name__)

# urls = (
#     ("/", "IndexRouter") +
#     ("/u/(.*)/(.*)", "IndexRouter") +
#     ("/opponents", "TopOpponentsRouter") +
#     ("/xp", "XPRouter") +
#     ("/dbstate", "DBStateRouter") +
#     ("/game_played_stats", "GamesPlayedRouter") +
#     ("/games_stats", "GamesStatsRouter") +
#     ("/history", "GameHistoryRouter")
# )

LOG.setLevel(logging.DEBUG)


# def check_args(inp, args):
#     for a in args:
#         if not getattr(inp, a, None):
#             return False
#     return True


# class Router(metaclass=abc.ABCMeta):
#     """

#     """

#     def GET(self) -> str:
#         ret = self._get()
#         return ret if type(ret) == str else json.dumps(ret)

#     @abc.abstractmethod
#     def _get(self) -> str:
#         pass


# @app.route("/")
# @app.route("/u/<gateway>/<username>")
# class IndexRouter(Router):
#     """
#     Not a router, just return WebAPP.
#     """

#     def _get(self):
#         pass

#     def GET(self, gateway: str = "", username: str = ""):
#         env = jinja2.Environment(
#             loader=jinja2.PackageLoader('wc3inside', 'templates'),
#             # autoescape=jinja2.select_autoescape(['html', 'xml', 'js'])
#         )
#         tpl = env.get_template("solo_stats.html")
#         return tpl.render(app_js=env.get_template("app.js").render())


# class DBStateRouter(Router):

#     def _get(self):
#         return DBStateView().get()


# class XPRouter(Router):

#     def _get(self):
#         inp = web.input(username=None, gateway=None)
#         if not check_args(inp, ["username", "gateway"]):
#             return {"error": "Malformed request."}

#         return MyHistoryView(inp.username, inp.gateway).get_solo_xp()


# class GameHistoryRouter(Router):

#     def _get(self):
#         inp = web.input(username=None, gateway=None, limit=-1)
#         if not check_args(inp, ["username", "gateway"]):
#             return {"error": "Malformed request."}

#         return MyHistoryView(inp.username, inp.gateway).get(int(inp.limit))


@app.route("/v1/enemies/<username>/<gateway>")
def top_opponents(username, gateway):
    return json.dumps(TopOpponentsView(gateway).get_stats(username))


@app.route("/v1/db/stats")
def stats():
    return json.dumps(DBStateView().get())


# https://hub.docker.com/r/tiangolo/uwsgi-nginx-flask/
@app.route("/")
def main():
    index_path = os.path.join(app.static_folder, 'index.html')
    return send_file(index_path)


@app.route('/<path:path>')
def route_frontend(path):
    # ...could be a static file needed by the front end that
    # doesn't use the `static` path (like in `<script src="bundle.js">`)
    file_path = os.path.join(app.static_folder, path)
    if os.path.isfile(file_path):
        return send_file(file_path)
    # ...or should be handled by the SPA's "router" in front end
    else:
        index_path = os.path.join(app.static_folder, 'index.html')
        return send_file(index_path)


# class GamesStatsRouter(Router):
#     """
#     GamesStats - information about races/maps and players.
#     """

#     def _get(self):
#         inp = web.input(gateway="")
#         if not check_args(inp, ["gateway"]):
#             return {"error": "Malformed request."}

#         return GamesStatsView(inp.gateway).get()


# class GamesPlayedRouter(Router):

#     def _get(self):
#         inp = web.input(username="", gateway="")
#         if not check_args(inp, ["username", "gateway"]):
#             return {"error": "Malformed request."}
#         return list(GamesPlayedView(inp.username, inp.gateway).get().items())


# def main():
#     app = web.application(urls, globals())
#     app.run()


if __name__ == "__main__":
    app.run()

# app = web.application(urls, globals())
# application = app.wsgifunc()
