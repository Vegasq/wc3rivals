<script>
import axios from 'axios'
export default {
    data() {
        return {
            records: [],
            api_response: [],
            username: "",
            gateway: "",
            race: "random",
            gw_id_to_name: {
                'europe': 'Europe',
                'us_west': 'US West',
                'us_east': 'US East'
            }
        }
    },
    mounted: function(){
        this.call_api();
    },
    methods: {
        call_api: function(){
            this.username = this.$route.params.username;
            this.gateway = this.$route.params.gateway;

            // axios
            //     .get('/v1/enemies/'+this.$route.params.gateway+'/'+this.$route.params.username)
            //     .then(response => (this.api_response = response.data),
            //           error => axios.get('http://127.0.0.1:5000/v1/enemies/'+this.$route.params.gateway+'/'+this.$route.params.username)
            //                         .then(response => (this.api_response = response.data)));
            axios
                .get('/v1/enemies/'+this.$route.params.gateway+'/'+this.$route.params.username)
                .then(response => (this.api_response = response.data));
        },
        playerIconURL: function(race){
            race = this.get_race(race);
            var sex = ['male', 'female'];
            var rand = sex[Math.floor(Math.random() * sex.length)];

            return require('../assets/' + race + '_' + rand + '.png');
        },
        resultsIconURL: function(result){
            return require('../assets/' + result + '.svg');
        },
        get_race: function (input_race) {
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
            return "random";
        }
    },
    watch: {
        '$route' (to) {
            this.username = to.params.username;
            this.gateway = to.params.gateway;
            this.call_api();
        },
        api_response: function(val) {
            function detect_result(info) {
                var result = "even";
                if (info["win"] > info["loss"]) {
                    result = "up";
                } else if (info["loss"] > info["win"]){
                    result = "down";
                }
                return result;
            }

            function get_avg_game_len(history){
                var avg = 0;
                for (var z = history.length - 1; z >= 0; z--) {
                    avg += history[z]["length"];
                }
                avg = avg / history.length;
                return avg;
            }

            function get_random_sex(){
                var sex_list = ['male', 'female'];
                return sex_list[Math.floor(Math.random() * sex_list.length)];
            }

            var rows = [];
            for (var i = 0; i < val.length; i++) {
                var result_icon = detect_result(val[i][1]);
                var avg = Math.floor(get_avg_game_len(val[i][1]["history"]));
                var opponent = val[i][0];
                var players_data = val[i][1]["history"][0]["players_data"];
                var last_game = val[i][1]["history"][0]["date"].split(" ")[0];
                var race = "";
                if (opponent == players_data[0]["username"]){
                    race = players_data[0]["race"];
                    this.race = players_data[1]["race"];
                } else {
                    race = players_data[1]["race"];
                    this.race = players_data[0]["race"];
                }

                rows.push({
                    "username": val[i][0],
                    "won": val[i][1]["win"],
                    "loss": val[i][1]["loss"],
                    "last_game": last_game,
                    "result_icon": result_icon,
                    "avg_game": avg,
                    "race": this.get_race(race),
                    "sex": get_random_sex(),
                    // "gateway": this.gateway
                });
            }
            this.records = rows;
        }
    },
    computed: {
        is_rivals_page(){
            return window.location.href.indexOf("/u/") !== -1 === true;
        }
    }
}
</script>

<template>
    <div id="rivals_vue" v-if="is_rivals_page">
        <table id="enemies_table">
            <thead>
                <tr>
                    <th colspan="5">
                        <img class="race_icon table_header_icon"
                            v-bind:src="playerIconURL(this.race)">
                        {{ username }}
                        <span class="table_header_gateway">{{ gw_id_to_name[gateway] }}</span>
                    </th>
                </tr>
                <tr>
                    <th scope="col" class="first_col">USER</th>
                    <th scope="col">SCORE</th>
                    <th scope="col">LAST GAME</th>
                    <th scope="col">AVG. TIME</th>
                    <th scope="col"></th>
                </tr>
            </thead>
            <tbody id="enemies_table_body">
                <tr v-for="record in records" :key="username + '_' + record.username">
                    <td class="user_col first_col">
                        <router-link :to="{ name: 'rivals', params: {gateway: gateway, username: record.username}}">
                            <img class="race_icon"
                                 v-bind:src="playerIconURL(record.race)">
                            {{ record.username }}
                        </router-link>
                    </td>
                    <td v-bind:class="'score_col score_col_' + record.result_icon">
                        <img v-bind:src="resultsIconURL(record.result_icon)">
                        {{ record.won }} x {{ record.loss }}
                    </td>
                    <td class="last_game_col">{{ record.last_game }}</td>
                    <td class="avg_col">{{ record.avg_game }} min</td>
                    <td class="more_col">
                        <router-link :to="{ name: 'history', params: {gateway: gateway, username_a:username, username_b: record.username}}">
                            <img src="../assets/more.svg">
                        </router-link>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

</template>



<style scoped>
#enemies_table {
    width: 100%;
}

#enemies_table thead {
  font-family: Roboto;
  font-size: 16px;
  font-weight: bold;
  font-style: normal;
  font-stretch: normal;
  line-height: normal;
  letter-spacing: 0.4px;
  color: #f0f0f0;

  border-bottom: 1px solid #6d6d6d;
}

#enemies_table .first_col {
    padding-left: 20px;
}
#enemies_table thead tr th {
    /* margin-top: 11px; */
    /* padding-top: 11px;
    padding-bottom: 11px; */
    text-align: left;

}
#enemies_table thead tr:nth-child(1) th {
    text-align: left;
    font-size: 20px;
    font-weight: bold;
    font-style: normal;
    font-stretch: normal;
    color: #f0f0f0;
}
#enemies_table thead tr:nth-child(1) th img.table_header_icon {
    top: 8px;
    padding-right: 5px;
}
#enemies_table thead tr:nth-child(1) th span.table_header_gateway {
    font-family: Roboto;
    font-size: 20px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.5px;
    color: #ffffff;
}

#enemies_table thead tr:nth-child(1){
    border-bottom: 0;
}
#enemies_table tr {
    height: 49px;
    line-height: 49px;
    border-bottom: 1px solid #6d6d6d;
}

#enemies_table tbody tr:hover {
    background-color: rgba(216, 216, 216, 0.15);
}
#enemies_table .user_col, #enemies_table .user_col a {
    width: 260px;
    /* height: 19px; */
    font-family: Roboto;
    font-size: 16px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
    text-decoration: none;
}
#enemies_table .user_col a:hover {
    color: #ea760e;;
}
#enemies_table .race_icon {
    position: relative;
    width: 30px;
    height: 30px;
    top:10px;
    padding-right: 10px;
}
#enemies_table .score_col {
    width: 165px;
    height: 19px;
    font-family: Roboto;
    font-size: 16px;
    font-weight: bold;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
}
#enemies_table .score_col img {
    position: relative;
    top: 2px;
    padding-right: 10px;
}
#enemies_table .score_col_up {
    color: #54ea7c;
}
#enemies_table .score_col_down {
    color: #ea4335;
}
#enemies_table .score_col_even {
    color: #f0f0f0;
}
#enemies_table .last_game_col {
    width: 180px;
    height: 19px;
    font-family: Roboto;
    font-size: 16px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
}
#enemies_table .avg_col {
    width: 145px;
    height: 19px;
    font-family: Roboto;
    font-size: 16px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
}
#enemies_table .more_col > img {
    position: relative;
    top: 3px;
    -webkit-transform: rotate(-90deg);
    -moz-transform: rotate(-90deg);
    -o-transform: rotate(-90deg);
    -ms-transform: rotate(-90deg);
    transform: rotate(-90deg);
}
</style>
