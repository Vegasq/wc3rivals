import web
from views import MyEnemiesView
import json


urls = (
    '/', 'index',
    '/api', 'api'
)


class index:
    def GET(self):
        with open("templates/solo_stats.html") as fl:
            return fl.read()


class api(object):
    def GET(self):
        print("API CALL")
        inp = web.input(name=None, gateway=None)

        data = {
            "error": "not enough data in request",
            "request": {
                "name": inp.name,
                "gateway": inp.gateway
            }
        }

        if inp.name and inp.gateway:
            mew = MyEnemiesView(inp.gateway)
            data = mew.get_stats(inp.name)

        print(data, len(data), type(data))
        if len(data) == 0:
            data = {
                "info": "User not found."
            }
        print(data)

        return json.dumps(data)


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
