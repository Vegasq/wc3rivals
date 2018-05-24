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
            this.players.forEach(function(z){
                emit(z, 1);
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
            LOG.info(f"Creating per-player stats for ladder {l}.")
            db.DB(l).collection.map_reduce(cls.map_fn, cls.reduce_fn,
                                           l.lower() + "_players")


def main():
    PlayerTopGamesStats.build()
    RacesStats.build()


if __name__ == "__main__":
    main()
