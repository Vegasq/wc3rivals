import abc
import os
import web
import json

from wc3inside.web.views import TopOpponentsView, MyHistoryView, GamesPlayedView,\
    DBStateView, GamesStatsView


urls = (
    '/', 'index',
    '/u/(.*)/(.*)', 'index',
    '/opponents', 'TopOpponentsRouter',
    '/history', 'history',
    '/xp', 'xp',
    '/dbstate', 'dbstate',
    '/game_played_stats', 'GamesPlayedRouter',
    '/games_stats', 'GamesStatsRouter'
)


def check_args(inp, args):
    for a in args:
        if not getattr(inp, a, None):
            return False
    return True


class Router(metaclass=abc.ABCMeta):
    """

    """
    def GET(self) -> str:
        return self._get()

    @abc.abstractmethod
    def _get(self) -> str:
        pass


class dbstate(object):
    def GET(self):
        dbs = DBStateView()
        return json.dumps(dbs.get())


class xp(object):
    def GET(self):
        inp = web.input(username=None, gateway=None)
        msv = MyHistoryView(inp.username, inp.gateway)
        xp = []
        for game in msv.get_solo():
            for p in game["players_data"]:
                if p["username"] == inp.username:
                    xp.append([str(game["date"]), p["xp"]])
        return json.dumps(xp)


class history(object):
    def GET(self):
        inp = web.input(username=None, gateway=None, limit=-1)
        msv = MyHistoryView(inp.username, inp.gateway)
        games = []
        if inp.limit == -1:
            games_resp = msv.get()
        else:
            games_resp = msv.get(int(inp.limit))

        for g in games_resp:
            games.append({
                "primary_player": inp.username,
                "map": g["map"],
                "date": str(g["date"]),
                "type": g["type"],
                "length": g["length"],
                "players_data": g["players_data"]
            })
        return json.dumps(games)


class index(object):
    def GET(self, gateway: str="", username: str=""):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + "/templates/app.js") as fl:
            js = fl.read()

        with open(path + "/templates/solo_stats.html") as fl:
            return fl.read().replace("{{ app.js }}", js)


class TopOpponentsRouter(Router):
    def _get(self):
        inp = web.input(username="", gateway="")
        data = TopOpponentsView(inp.gateway).get_stats(inp.username)
        return json.dumps(data)


class GamesStatsRouter(Router):
    """
    GamesStats - information about races/maps and players. 
    """
    def _get(self):
        inp = web.input(gateway="")
        if not check_args(inp, ["gateway"]):
            return json.dumps({"error": "Malformed request."})

        return GamesStatsView(inp.gateway).get()


class GamesPlayedRouter(Router):
    def _get(self):
        inp = web.input(username="", gateway="")
        msv = GamesPlayedView(inp.username, inp.gateway)
        return json.dumps(list(msv.get().items()))


def main():
    app = web.application(urls, globals())
    # try:
    #     web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    # except (ImportError, ModuleNotFoundError, Exception):
    #     LOG.error("Do you have spawn-fcgi?")
    app.run()


if __name__ == "__main__":
    main()
