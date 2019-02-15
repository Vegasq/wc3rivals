<script>
    import axios from 'axios'
    export default {
        data: function() {
            return {
                gateway: "",
                history: []
            }
        },
        mounted() {
            var self = this;
            var callback = function(response){
                self.gateway = self.$route.params.gateway;
                function compare(a, b) {
                    if (a.username < b.username)
                        return -1;
                    if (a.username > b.username)
                        return 1;
                    return 0;
                }
                for (var i=0; i<response.data.length; i++){
                    // Sort players within history
                    response.data[i].players_data = response.data[i].players_data.sort(compare);

                    // Date without H:M:S
                    response.data[i].date_short = response.data[i].date[0].split(" ")[0];

                    response.data[i].players_data[0].result = response.data[i].players_data[0].result.toLowerCase()
                    response.data[i].players_data[1].result = response.data[i].players_data[1].result.toLowerCase()

                    // XP earnings prepend with +
                    var p0_xp = response.data[i].players_data[0].xp_diff;
                    var p1_xp = response.data[i].players_data[1].xp_diff;
                    if (p0_xp > 0){
                        response.data[i].players_data[0].xp_diff = "+" + p0_xp;
                    }
                    if (p1_xp > 0){
                        response.data[i].players_data[1].xp_diff = "+" + p1_xp;
                    }
                }
                self.history = response.data;
                self.history.reverse();
            };

            // axios
            //     .get('/v1/history/'+this.$route.params.gateway+'/'+this.$route.params.username_a+'/'+this.$route.params.username_b)
            //     .then(callback,
            //           error => axios.get('http://127.0.0.1:/v1/history/'+this.$route.params.gateway+'/'+this.$route.params.username_a+'/'+this.$route.params.username_b)
            //                         .then(callback));
            axios
                .get('/v1/history/'+this.$route.params.gateway+'/'+this.$route.params.username_a+'/'+this.$route.params.username_b)
                .then(callback);
        },
        methods: {
            fixMapName: function(map){
                map = map.replace("_ L V", " LV");
                return map;
            },
            mapURL: function(map){
                map = map.toLowerCase();
                map = map.split(" ").join("_");
                // TODO: Should we force naming in backend?
                map = map.replace("__l_v", "_lv");

                try {
                    return require('../assets/maps/' + map + '.png');
                } catch (e) {
                    return require('../assets/maps/default.png');
                }
            },
            playerIconURL: function(race){
                race = race.toLowerCase();
                if (race.indexOf('orc') !== -1){
                    race = 'orc';
                } else if (race.indexOf('elf') !== -1){
                    race = 'nightelf';
                } else if (race.indexOf('human') !== -1){
                    race = 'human';
                } else if (race.indexOf('undead') !== -1){
                    race = 'undead';
                } else {
                    race = 'random';
                }
                var sex = ['male', 'female'];
                var rand = sex[Math.floor(Math.random() * sex.length)];

                return require('../assets/' + race + '_' + rand + '.png');
            }
        }
    }
</script>

<template>
    <table id="history_table">
        <thead>
            <tr v-if="history[0]">
                <th>
                    <router-link :to="{ name: 'rivals', params: {gateway: gateway, username: history[0].players_data[0].username}}">
                        <img class="race_icon" v-bind:src="playerIconURL(history[0].players_data[1].race)">
                        {{history[0].players_data[0].username}}
                    </router-link>
                </th>
                <th><div>vs</div></th>
                <th>
                    <router-link :to="{ name: 'rivals', params: {gateway: gateway, username: history[0].players_data[1].username}}">
                        <img class="race_icon" v-bind:src="playerIconURL(history[0].players_data[1].race)">
                        {{history[0].players_data[1].username}}
                    </router-link>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="record in history" :key="record.date[0]">

                <td class="player_column">
                    <div v-bind:class="'icon_'+record.players_data[0].result">
                        <img class="race_icon" v-bind:src="playerIconURL(record.players_data[0].race)">
                    </div>
                    <div v-bind:class="'xp_'+record.players_data[0].result">
                        <p><b>LEVEL:</b> {{ record.players_data[0].level }} ({{ record.players_data[0].xp }} XP)</p>
                        <p><b>RESULT:</b> {{ record.players_data[0].result }} </p>
                        <p><b>CHANGE:</b> {{ record.players_data[0].xp_diff }} XP</p>
                    </div>

                </td>

                <td class="map_column">
                    <section>
                        <img v-bind:src="mapURL(record.map)">
                        <div>
                            <p><b>{{ fixMapName(record.map) }}</b></p>
                            <p>{{record.date_short}}</p>
                            <p>{{record.length}} minutes</p>
                        </div>
                    </section>
                </td>

                <td class="player_column">
                    <div v-bind:class="'icon_'+record.players_data[1].result">
                        <img class="race_icon" v-bind:src="playerIconURL(record.players_data[1].race)">
                    </div>
                    <div v-bind:class="'xp_'+record.players_data[1].result">
                        <p><b>LEVEL:</b> {{ record.players_data[1].level }} ({{ record.players_data[1].xp }} XP)</p>
                        <p><b>RESULT:</b> {{ record.players_data[1].result }} </p>
                        <p><b>CHANGE:</b> {{ record.players_data[1].xp_diff }} XP</p>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>

</template>

<style scoped>
#history_table {
    width: 100%;
}
#history_table thead tr th img {
    width: 30px;
    height: 30px;

    position: relative;
    top: 7px;
}
#history_table thead tr th:nth-child(1),
#history_table thead tr th:nth-child(3) {
    font-family: Roboto;
    font-size: 20px;
    font-weight: 400;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.5px;
    color: #ffffff;
}

#history_table thead tr th:nth-child(1) a,
#history_table thead tr th:nth-child(3) a {
    text-decoration: none;
    color: #ffffff;
}

#history_table thead tr th:nth-child(2) div {
    width: 50px;
    height: 50px;
    margin: 0 auto;
    border: 2px solid #54ea7c;
    border-radius: 30px;
    font-family: Roboto;
    font-size: 16px;
    font-weight: 400;
    font-style: normal;
    font-stretch: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
    line-height: 50px;
    margin-bottom: 50px;
}

.map_column {

    width: 300px;
    height: 100px;
    font-family: Roboto;
    font-size: 16px;
    font-weight: normal;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
}
.player_column {
    width: 250px;
    border-bottom: 1px solid gray;
    border-top: 1px solid gray;
    background-color: rgba(216, 216, 216, 0.05);
}
.player_column:nth-child(1) div:nth-child(1) {
    float:left;
}
.player_column:nth-child(1) div:nth-child(1) {
    float:right;
}

#history_table > tbody > tr > td:nth-child(1) > div {
    float: left;
}
#history_table > tbody > tr > td:nth-child(3) > div {
    float: right;
}

.player_column div img {
    padding: 15px;
    width: 60px;
    height: 60px;
}

.map_column > section > div:nth-child(1) {
    float: left;
    width: 80px;
    padding-left: 33px;
    padding-right: 20px;

}

.map_column > section > img {
    max-width: 80px;
    max-height: 80px;
    float: left;
    padding: 10px 20px 10px 30px;
}

.map_column > section > div:nth-child(2) {
    padding-top: 10px;
    float: left;
    width: 140px;
}
.map_column > section > div:nth-child(2) > p:nth-child(1) {
    font-family: Roboto;
    font-size: 16px;
    font-weight: 400;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
}
.map_column > section > div:nth-child(2) > p:nth-child(2) {
    font-family: Roboto;
    font-size: 16px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
}
.map_column > section > div:nth-child(2) > p:nth-child(3) {
    font-family: Roboto;
    font-size: 16px;
    font-weight: 300;
    font-style: normal;
    font-stretch: normal;
    line-height: normal;
    letter-spacing: 0.4px;
    color: #f0f0f0;
}

.xp_win, .xp_loss {
    line-height: 1.6em;
    font-size: 12px;
    font-weight: 300;
    font-family: Roboto;
    color: #f0f0f0;

}
.xp_win > p > b, .xp_loss > p > b{
    font-weight: 400;
}
.xp_win {
    /* color: #54ea7c; */
    padding: 20px 20px 15px 15px;
}
.xp_loss {
    padding: 20px 20px 15px 15px;

    /* color: #ea4335; */
}
</style>
