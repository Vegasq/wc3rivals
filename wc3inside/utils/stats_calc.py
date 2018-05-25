# Collection of mapReduce functions to collect various statistics


# db.getCollection('lordaeron_games').mapReduce(
#     function(){
#         this.players_data.forEach(function(z){
#             emit(z.race, 1);
#         });
#     },
#     function(k, v){
#         var total = 0;
#         for (var i = 0; i < values.length; i++) {
#             total += values[i];
#         }
#
#         return total;
#     },
#     {
#         "out": "races",
#         "query": {"players": "SumniyRobot"}
#     }
# )


from wc3inside.utils import db
from wc3inside.utils.log import LOG

from bson.code import Code


class RacesStats(object):
    map_fn = Code("""
        function(){
            this.players_data.forEach(function(z){
                if (z.race.indexOf("Rand") !== -1) {
                    emit("TotalRandom", 1);
                }
                // Execute emit for all races including random to collect info
                // how fair it get splitted in ladder.
                emit(z.race, 1);
            });
        }
    """)

    reduce_fn = Code("""
        function(k, v){
            var total = 0;
            for (var i = 0; i < v.length; i++) {
                total += v[i];
            }
            return total;
        }
    """)

    @classmethod
    def build(cls):
        ladders = ["Lordaeron", "Azeroth", "Northrend"]
        for l in ladders:
            LOG.info(f"Creating race stats for ladder {l}.")
            db.DB(l).collection.map_reduce(cls.map_fn, cls.reduce_fn,
                                           l.lower()+"_races")


class PlayerTopGamesStats(object):
    map_fn = Code("""
        function(){
            if (this.players.length === 2){
                this.players.forEach(function(z){
                    emit(z, 1);
                });
            };
        }
    """)

    reduce_fn = Code("""
        function(k, v){
            var total = 0;
            for (var i = 0; i < v.length; i++) {
                total += v[i];
            }

            return total;
        }
    """)

    @classmethod
    def build(cls):
        ladders = ["Lordaeron", "Azeroth", "Northrend"]
        for l in ladders:
            LOG.info(f"Creating per-player stats for ladder {l}.")
            db.DB(l).collection.map_reduce(cls.map_fn, cls.reduce_fn,
                                           l.lower() + "_players")


class MapsStats(object):
    map_fn = Code("""
        function(){
            var o = {
                total_games: 1,
                players: this.players.length,
                map_name: this.map
            };
            emit(this.map+'#'+this.players.length, o);
        }
    """)

    reduce_fn = Code("""
        function(k, v){
            var total_games = 0;
            var avg = 2; // Assume most popular value
            var map_name = '';

            for (var i = 0; i < v.length; i++) {
                total_games += v[i].total_games;
                avg = (v[i].players + avg) / 2;
                map_name = v[i].map_name
            };

            var o = {
                total_games: total_games,
                players: avg,
                map_name: map_name
            };
            return o;
        }
    """)

    @classmethod
    def build(cls):
        ladders = ["Lordaeron", "Azeroth", "Northrend"]
        conn = db.DB("")
        for l in ladders:
            LOG.info(f"Creating per-map stats for ladder {l}.")
            conn.set_gateway(l)
            conn.collection.map_reduce(
                cls.map_fn,
                cls.reduce_fn,
                l.lower()+"_maps")


def main():
    PlayerTopGamesStats.build()
    RacesStats.build()
    MapsStats.build()


if __name__ == "__main__":
    main()
