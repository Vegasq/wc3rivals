// Utils START
function do_get(url, report_to) {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'text';

    xhr.onload = function () {
        if (xhr.readyState === xhr.DONE) {
            if (xhr.status === 200) {
                report_to(xhr.responseText);
            }
        }
    };

    xhr.send(null);
}

function simplify_race(race){
    let r = "";
    if (race.indexOf("Random") !== -1){
        r += "?";
    }
    if (race.indexOf("Orc") !== -1){
        r += "O";
    }
    if (race.indexOf("Human") !== -1){
        r += "H";
    }
    if (race.indexOf("Night Elf") !== -1){
        r += "N";
    }
    if (race.indexOf("Undead") !== -1){
        r += "U";
    }
    return r;
}

function fix_location(username, gateway){
    let href = "/u/"+gateway+"/"+username;
    history.pushState({}, "", href);
}

function current_gateway(){
    if (window.location.href.indexOf("/u/") !== -1) {
        let q = window.location.href.split("/u/")[1].split("/");
        return q[0];
    } else {
        return document.getElementById("search_gateway").value;

    }
}
// Utils END

// Charts START
function draw_statistic(source_data){
    source_data = JSON.parse(source_data);
    if (source_data.length === 0) {
        return
    }

    // To display left-to-right
    source_data = source_data.reverse();

    // Prepend header
    Array.prototype.unshift.apply(source_data, [["Day", "Games"]]);

    let data = google.visualization.arrayToDataTable(source_data);
    let options = {legend: 'none'};
    let chart = new google.visualization.AreaChart(
        document.getElementById('games_per_day_chart'));
    chart.draw(data, options);
}

function draw_xp_statistic(source_data){
    source_data = JSON.parse(source_data);
    if (source_data.length === 0) {
        return
    }

    // To display left-to-right
    source_data = source_data.reverse();

    // Prepend header
    Array.prototype.unshift.apply(source_data, [["#", "XP"]]);

    let data = google.visualization.arrayToDataTable(source_data);
    let options = {legend: 'none'};
    let chart = new google.visualization.AreaChart(
        document.getElementById('xp_chart'));
    chart.draw(data, options);
}
// Charts END


class GamesStatistic {
    constructor(username, gateway) {
        this.username = username;
        this.gateway = gateway;
    }

    start() {
        do_get(
            "/game_played_stats?username="+this.username+"&gateway="+this.gateway,
            this.parse
        );
    }

    parse(data) {
        draw_statistic(data);
    }
}

class OpponentsStatistic {
    constructor(username, gateway) {
        this.username = username;
        this.gateway = gateway;
    }

    start() {
        document.getElementById("score_against_table").style.display = "none";
        do_get(
            "/opponents?username="+this.username+"&gateway="+this.gateway,
            this.parse
        );
    }

    parse(result) {
        result = JSON.parse(result);

        let stats_body = document.getElementById("stats_body");
        stats_body.innerHTML = "";

        let err_msg_box = document.getElementById("error_msg");
        let info_msg_box = document.getElementById("info_msg");
        err_msg_box.style.display = "none";
        info_msg_box.style.display = "none";

        if ("error" in result) {
            err_msg_box.innerHTML = result["error"];
            err_msg_box.style.display = "block";
            return;
        } else if  ("info" in result) {
            info_msg_box.innerHTML = result["info"];
            info_msg_box.style.display = "block";
            return;
        }

        // arrow &#9657;
        // arrow on hover &#9656;
        // arrow pressed &#9663;
        // arrow pressed on hover &#9663;

        let tpl = "" +
                  "            <tr class=''>\n" +
                  "                <td class='show_opponent_details'>&#9657;</td>\n" +
                  "                                                    <td class='%state_class%'>\n" +
                  "                    <span class=\"win\">%win%</span>\n" +
                  "                    x\n" +
                  "                    <span class=\"loss\">%loss%</span>\n" +
                  "                </td>\n" +
                  "                <td>%opponent%</td>\n" +
                  "            </tr>\n" +
                  "            <tr class='hidden'>\n" +
                  "                <td colspan='3'>" +
                  "                    <table class='table '>" +
                  "                        %games_info%" +
                  "                    </table>" +
                  "                </td>\n" +
                  "            </tr>\n" +
                  "            ";

        let player_url_tpl =
            "<a " +
            "onclick='send_request(\"%player_name%\", \"%gateway%\");return false;' " +
            "href='#'>%link_text%</a>";

        for (let i=0; i<result.length;i+=1) {
            let secondary_player = player_url_tpl.replace("%player_name%", result[i][1]["secondary_player"]);
            let primary_player = result[i][1]["primary_player"]
            secondary_player = secondary_player.replace("%gateway%", current_gateway());
            secondary_player = secondary_player.replace("%link_text%", result[i][1]["secondary_player"]);

            let body = "";
            body += tpl.replace("%win%", result[i][1]["win"]);
            body = body.replace("%loss%", result[i][1]["loss"]);
            body = body.replace("%opponent%", secondary_player);
            body = body.replace("%player%", result[i][1]["primary_player"]);

            let game_info_html = "";
            for (let g of result[i][1]["history"]){
                let result = "";
                for (let p of g["players_data"]){
                    if (p["username"] === primary_player){
                        result = p["result"];
                    }
                }
                game_info_html += "<tr>" +
                    "<td>"+result+"</td>" +
                    "<td>"+g["date"].split(" ")[0]+"</td>" +
                    "<td>"+g["map"]+"</td>" +
                    "<td>"+g["length"]+" min</td>" +
                    "</tr>";
            }
            body = body.replace("%games_info%", game_info_html);

            let state = "";
            if (result[i][1]["state"] === 1) {
                state = "table-success";
            } else if (result[i][1]["state"] === -1) {
                state = "table-danger";
            }
            body = body.replace("%state_class%", state);

            stats_body.innerHTML += body;
        }
        let rows = document.getElementsByClassName("show_opponent_details");
        for (let r of rows){
            r.addEventListener("click",
                function(e){
                    console.log(e);
                    if (e.target.className === "show_opponent_details"){
                        if (e.target.parentNode.nextElementSibling.style.display === "table-row") {
                            e.target.parentNode.nextElementSibling.style.display = "none";
                        } else {
                            e.target.parentNode.nextElementSibling.style.display = "table-row";
                        }

                    }
                }
            )
        }

        document.getElementById("score_against_table").style.display = "";
    }
}

class XpStatistic {
    constructor(username, gateway) {
        this.username = username;
        this.gateway = gateway;
    }

    start() {
        do_get(
            "/xp?username="+this.username+"&gateway="+this.gateway,
            this.parse
        );
    }

    parse(data) {
        draw_xp_statistic(data);
    }
}


class DBState {
    constructor() {}

    start() {
        do_get(
            "/dbstate",
            this.parse
        );
    }

    parse(data) {
        data = JSON.parse(data);
        var html = "";
        for (let e of data) {
            html += "<div>" + e[0] + ": " + e[1] + "</div>";
        }
        document.getElementById("db_state").innerHTML = html;
    }
}


class GameHistory {
    constructor(username, gateway) {
        this.username = username;
        this.gateway = gateway;
    }

    start() {
        document.getElementById("game_history_table").style.display = "none";
        do_get(
            "/history?username="+this.username+"&gateway="+this.gateway+"&limit=5",
            this.parse
        );
    }

    parse(data) {
        let game_history_body = document.getElementById("game_history_body");
        game_history_body.innerHTML = "";
        data = JSON.parse(data);

        if (data.length === 0){
            console.error("Empty response in GameHistory.");
            return;
        }

        let tpl = "" +
                  "            <tr>\n" +
                  "                <td>%date%</td>\n" +
                  "                <td>%map%</td>\n" +
                  "                <td>%winners%</td>\n" +
                  "                <td>%loosers%</td>\n" +
                  "            </tr>\n";
        let player_url_tpl =
            "<a " +
            "onclick='send_request(\"%player_name%\", \"%gateway%\");return false;' " +
            "href='#'>%link_text%</a>";

        document.getElementById(
            "username_block").innerHTML = data[0]["primary_player"];

        let level = 0;
        for (let o of data[0]["players_data"]) {
            if (o["username"] === data[0]["primary_player"]) {
                level = o["level"];
            }
        }
        document.getElementById("level_block").innerHTML = "Level " + level;

        for (let i=0; i<data.length;i++) {
            let game_info = data[i];

            let winners = "";

            for (let z=0; z<game_info["players_data"].length;z++) {
                let player = game_info["players_data"][z];
                if (player["result"] === "Win") {
                    let player_link = player_url_tpl.replace("%player_name%", player["username"]);
                    player_link = player_link.replace("%gateway%", current_gateway());
                    player_link = player_link.replace(
                        "%link_text%",
                        player["username"] + " ["+simplify_race(player["race"])+"]");

                    winners += player_link;
                }
            }

            let loosers = "";
            for (let z=0; z<game_info["players_data"].length;z++) {
                let player = game_info["players_data"][z];
                if (player["result"] === "Loss") {
                    let player_link = player_url_tpl.replace("%player_name%", player["username"]);
                    player_link = player_link.replace("%gateway%", current_gateway());
                    player_link = player_link.replace(
                        "%link_text%",
                        player["username"] + " ["+simplify_race(player["race"])+"]");

                    loosers += player_link;
                }
            }

            let body = "";
            body += tpl.replace("%date%", game_info["date"]);
            body = body.replace("%map%", game_info["map"]);
            body = body.replace("%winners%", winners);
            body = body.replace("%loosers%", loosers);

            game_history_body.innerHTML += body;
        }
        document.getElementById("game_history_table").style.display = "";
    }
}

class DynamicSearchPage {
    constructor(){
        this.header = document.getElementById("row_header_block");
        this.footer = document.getElementById("row_footer_block");
    }

    check_state(){
        if (window.location.href.indexOf("/u/") !== -1){
            this.header.style.padding = "2em 0";
        } else {
            var w_height = "innerHeight" in window
                            ? window.innerHeight
                            : document.documentElement.offsetHeight;
            var h_height = "innerHeight" in this.header
                            ? this.header.innerHeight
                            : this.header.offsetHeight;

            var h_footer = "innerHeight" in this.footer
                            ? this.footer.innerHeight
                            : this.footer.offsetHeight;

            // let half_window = (w_height - h_footer - h_height/2) / 2;

            let half_window = w_height/2 - h_footer/2 - h_height/2;

            this.header.style.padding = "" + half_window + "px 5em";
        }
    }
}

function send_request(username, gateway){
    // for (let i=0;i<document.getElementsByClassName("show_on_search").length;i++){
    //     document.getElementsByClassName("show_on_search")[i].style.display = "none";
    // }

    // Enemies block
    let name;

    if (username && gateway){
        name = username;

        document.getElementById("search_box").value = username;
        document.getElementById("search_gateway").value = gateway;
    } else {
        name = document.getElementById("search_box").value;
        gateway = document.getElementById("search_gateway").value;
    }

    fix_location(name, gateway);

    for (let i=0;i<document.getElementsByClassName("show_on_search").length;i++){
        document.getElementsByClassName("show_on_search")[i].style.display = "flex";
    }

    // var out =
    //     http_get("/api?username="+name+"&gateway="+gateway);
    // render(out);

    let os = new OpponentsStatistic(name, gateway);
    os.start();

    // stats
    let gs = new GamesStatistic(name, gateway);
    gs.start();

    // history
    let gh = new GameHistory(name, gateway);
    gh.start();

    // xp
    let xs = new XpStatistic(name, gateway);
    xs.start();

    let dsp = new DynamicSearchPage();
    dsp.check_state();

}


// INIT START
(function(){
    let dsp = new DynamicSearchPage();
    dsp.check_state();
    // Module to draw charts.
    google.charts.load('current', {'packages':['corechart']});

    // Register events for search START
    // Search button
    var btn = document.getElementById("search_btn");
    btn.addEventListener("click", send_request);

    // Search on Enter
    var inp = document.getElementById("search_box");
    inp.addEventListener("keypress", function(e){
        var key = e.which || e.keyCode;
        if (key === 13) {
            send_request(undefined, undefined);
        }
    });
    // Register events for search END

    // DB state
    let dbs = new DBState();
    dbs.start()

    // Once page loaded - check href if it requests some user START
    window.onload = function () {
        if (window.location.href.indexOf("/u/") !== -1){
            var q = window.location.href.split("/u/")[1].split("/");
            var username = q[1];
            var gateway = q[0];

            document.getElementById("search_box").value = username;
            document.getElementById("search_gateway").value = gateway;

            send_request(username, gateway);
        }
    };
    // Once page loaded - check href if it requests some user END

    window.addEventListener('popstate', window.onload);

})();
// INIT END
