class Enemies {
    constructor(username, gateway) {
        this.username = username;
        this.gateway = gateway;
    }

    start() {
        var self = this;
        do_get(
            "/v1/enemies/"+this.username+"/"+this.gateway,
            function(data){
                self.parse(data);
            }
        );
    }

    detect_result(info) {
        var result = "even";
        if (info["win"] > info["loss"]) {
            result = "up";
        } else if (info["loss"] > info["win"]){
            result = "down";
        }
        return result;
    }

    get_avg_game_len(history){
        var avg = 0;
        for (var z = history.length - 1; z >= 0; z--) {
            avg += history[z]["length"];
        }
        avg = avg / history.length;
        return avg;
    }

    get_random_sex(){
        var sex_list = ['male', 'female'];  
        return sex_list[Math.floor(Math.random() * sex_list.length)];
    }

    get_race(input_race) {
        input_race = input_race.toLowerCase();
        input_race = input_race.split(" ").join("");

        if (input_race.indexOf("orc") !== -1) {
            return "orc";
        } else if (input_race.indexOf("nightelf") !== -1) {
            return "nightelf";
        } else if (input_race.indexOf("human") !== -1) {
            return "human";
        } else if (input_race.indexOf("undead") !== -1) {
            return "undead";
        }
        return "dragon";
    }

    parse(data) {
        data = JSON.parse(data);

        var tpl;
        var rendered_table = "";

        for (var i = data.length - 1; i >= 0; i--) {
            var result_icon = this.detect_result(data[i][1]);
            var avg = Math.floor(this.get_avg_game_len(data[i][1]["history"]));
            var opponent = data[i][0];
            var players_data = data[i][1]["history"][0]["players_data"];
            var last_game = data[i][1]["history"][0]["date"].split(" ")[0];
            var race = "";
            if (opponent == players_data[0]["username"]){
                race = players_data[0]["race"];
            } else {
                race = players_data[1]["race"];                
            }

            tpl = render_template(
                "opponent_row_template",
                {
                    "username": data[i][0],
                    "won": data[i][1]["win"],
                    "loss": data[i][1]["loss"],
                    "last_game": last_game,
                    "result_icon": result_icon,
                    "avg_game": avg,
                    "race": this.get_race(race),
                    "sex": this.get_random_sex(),
                    "gateway": this.gateway
                }
            );

            rendered_table = tpl + rendered_table;
        }
        document.getElementById("enemies_table_body").innerHTML = rendered_table;
        on_search();
    }
}