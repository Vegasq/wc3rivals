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
        var data2 = JSON.parse(data);
        console.log(data2);

        var tpl = render_template(
            "db_stats",
            {
                "eu": 123,
                "west": 321,
                "east": 532
            }
        );

        document.getElementById("db_stats_view").innerHTML = tpl + data;
    }
}
