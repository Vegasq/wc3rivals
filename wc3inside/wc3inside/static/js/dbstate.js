class DBState {
    constructor() {}

    start() {
        var self = this;
        do_get(
            "/v1/db/stats",
            function (data){
                self.parse(data);
            }
        );
    }

    parse(data) {
        var data = JSON.parse(data);

        var euro = "";
        var west = "";
        var east = "";

        for (let e of data) {
            if (e[0] === "Lordaeron") {
                west = e[1];
            } else if (e[0] === "Azeroth") {
                east = e[1];
            } else if (e[0] === "Northrend") {
                euro = e[1];
            }
        }

        var tpl = render_template(
            "db_state",
            {
                "euro": euro,
                "west": west,
                "east": east
            }
        );

        document.getElementById("db_stats_view").innerHTML = tpl + data;
    }
}
