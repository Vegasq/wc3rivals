import abc
import logging
import os
import web
import json
import jinja2

from wc3inside.utils.log import LOG

from wc3inside.web.views import (
    TopOpponentsView,
    MyHistoryView,
    GamesPlayedView,
    DBStateView,
    GamesStatsView,
)


urls = (
    ("/", "IndexRouter")
    + ("/u/(.*)/(.*)", "IndexRouter")
    + ("/opponents", "TopOpponentsRouter")
    + ("/xp", "XPRouter")
    + ("/dbstate", "DBStateRouter")
    + ("/game_played_stats", "GamesPlayedRouter")
    + ("/games_stats", "GamesStatsRouter")
    + ("/history", "GameHistoryRouter")
)

LOG.setLevel(logging.DEBUG)


def check_args(inp, args):
    for a in args:
        if not getattr(inp, a, None):
            return False
    return True


class Router(metaclass=abc.ABCMeta):
    """

    """

    def GET(self) -> str:
        ret = self._get()
        return ret if type(ret) == str else json.dumps(ret)

    @abc.abstractmethod
    def _get(self) -> str:
        pass


class IndexRouter(Router):
    """
    Not a router, just return WebAPP.
    """

    def _get(self):
        pass

    def GET(self, gateway: str = "", username: str = ""):
        env = jinja2.Environment(
            loader=jinja2.PackageLoader('wc3inside', 'templates'),
            # autoescape=jinja2.select_autoescape(['html', 'xml', 'js'])
        )
        tpl = env.get_template("solo_stats.html")
        return tpl.render(app_js=env.get_template("app.js").render())


class DBStateRouter(Router):

    def _get(self):
        return DBStateView().get()


class XPRouter(Router):

    def _get(self):
        inp = web.input(username=None, gateway=None)
        if not check_args(inp, ["username", "gateway"]):
            return {"error": "Malformed request."}

        return MyHistoryView(inp.username, inp.gateway).get_solo_xp()


class GameHistoryRouter(Router):

    def _get(self):
        inp = web.input(username=None, gateway=None, limit=-1)
        if not check_args(inp, ["username", "gateway"]):
            return {"error": "Malformed request."}

        return MyHistoryView(inp.username, inp.gateway).get(int(inp.limit))


class TopOpponentsRouter(Router):

    def _get(self):
        inp = web.input(username="", gateway="")
        if not check_args(inp, ["username", "gateway"]):
            return {"error": "Malformed request."}
        return TopOpponentsView(inp.gateway).get_stats(inp.username)


class GamesStatsRouter(Router):
    """
    GamesStats - information about races/maps and players.
    """

    def _get(self):
        inp = web.input(gateway="")
        if not check_args(inp, ["gateway"]):
            return {"error": "Malformed request."}

        return GamesStatsView(inp.gateway).get()


class GamesPlayedRouter(Router):

    def _get(self):
        inp = web.input(username="", gateway="")
        if not check_args(inp, ["username", "gateway"]):
            return {"error": "Malformed request."}
        return list(GamesPlayedView(inp.username, inp.gateway).get().items())


def main():
    app = web.application(urls, globals())
    app.run()


if __name__ == "__main__":
    main()
