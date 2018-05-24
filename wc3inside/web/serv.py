import os
import web
import json

from wc3inside.web.views import MyEnemiesView, MyStatsView, MyHistoryView, \
    DBStateView


urls = (
    '/', 'index',
    '/u/(.*)/(.*)', 'index',
    '/opponents', 'opponents',
    '/stats', 'stats',
    '/history', 'history',
    '/xp', 'xp',
    '/dbstate', 'dbstate'
)


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


class stats(object):
    def GET(self):
        inp = web.input(username=None, gateway=None)
        msv = MyStatsView(inp.username, inp.gateway)
        return json.dumps(list(msv.get().items()))


class index(object):
    def GET(self, gateway: str="", username: str=""):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(path + "/templates/app.js") as fl:
            js = fl.read()

        with open(path + "/templates/solo_stats.html") as fl:
            return fl.read().replace("{{ app.js }}", js)


class opponents(object):
    def GET(self):
        inp = web.input(username=None, gateway=None)

        data = {
            "error": "not enough data in request",
            "request": {
                "name": inp.username,
                "gateway": inp.gateway
            }
        }

        if inp.username and inp.gateway:
            mew = MyEnemiesView(inp.gateway)
            data = mew.get_stats(inp.username)

        if len(data) == 0:
            data = {
                "info": "User not found."
            }

        return json.dumps(data)


def main():
    app = web.application(urls, globals())
    # try:
    #     web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    # except (ImportError, ModuleNotFoundError, Exception):
    #     LOG.error("Do you have spawn-fcgi?")
    app.run()


if __name__ == "__main__":
    main()