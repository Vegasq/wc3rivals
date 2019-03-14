<script>
    export default {
        mounted() {
            this.$store.dispatch('getHistory', {
                'gateway': this.$route.params.gateway,
                'username_a': this.$route.params.username_a,
                'username_b': this.$route.params.username_b
            });
        },
        computed: {
            gateway: function(){
                return this.$route.params.gateway;
            },
            history: function(){
                var data = this.$store.getters.getHistory;

                function compare(a, b) {
                    if (a.username < b.username)
                        return -1;
                    if (a.username > b.username)
                        return 1;
                    return 0;
                }
                for (var i=0; i<data.length; i++){
                    // Sort players within history
                    data[i].players_data = data[i].players_data.sort(compare);

                    // Date without H:M:S
                    data[i].date_short = data[i].date[0].split(" ")[0];

                    data[i].players_data[0].result = data[i].players_data[0].result.toLowerCase()
                    data[i].players_data[1].result = data[i].players_data[1].result.toLowerCase()

                    // XP earnings prepend with +
                    var p0_xp = data[i].players_data[0].xp_diff;
                    var p1_xp = data[i].players_data[1].xp_diff;
                    if (p0_xp > 0){
                        data[i].players_data[0].xp_diff = "+" + p0_xp;
                    }
                    if (p1_xp > 0){
                        data[i].players_data[1].xp_diff = "+" + p1_xp;
                    }
                }
                // this.history = data;
                data.reverse();
                return data;
            }
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
                <th colspan="7">
                    <div>
                        <router-link :to="{ name: 'rivals', params: {gateway: gateway, username: history[0].players_data[0].username}}">
                            <img class="race_icon" v-bind:src="playerIconURL(history[0].players_data[0].race)">
                            {{history[0].players_data[0].username}}
                        </router-link>
                    </div>
                    <div>
                        <div class="vs_sign">vs</div>
                    </div>
                    <div>
                        <router-link :to="{ name: 'rivals', params: {gateway: gateway, username: history[0].players_data[1].username}}">
                            {{history[0].players_data[1].username}}
                            <img class="race_icon" v-bind:src="playerIconURL(history[0].players_data[1].race)">
                        </router-link>
                    </div>
                </th>
            </tr>
            <tr>
                <th>RESULT</th>
                <th>RACE</th>
                <th>DATE</th>
                <th>LENGTH</th>
                <th>MAP NAME</th>
                <th>RACE</th>
                <th>RESULT</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="record in history" :key="record.date[0]">
                <td class="player_col"><img class="result_icon" v-if="record.players_data[0].result == 'win'" v-bind:src="require('../assets/green.svg')"></td>
                <td class="player_col"><img class="race_icon" v-bind:src="playerIconURL(record.players_data[0].race)"></td>
                <td>{{record.date_short}}</td>
                <td>{{record.length}} min</td>
                <td class="map_name">{{ fixMapName(record.map) }}</td>
                <td class="player_col"><img class="race_icon" v-bind:src="playerIconURL(record.players_data[1].race)"></td>
                <td class="player_col"><img class="result_icon" v-if="record.players_data[1].result == 'win'" v-bind:src="require('../assets/green.svg')"></td>
            </tr>
        </tbody>
    </table>

</template>

<style lang="sass" scoped>
%header-font
    font-family: Roboto
    font-size: 14px
    font-weight: 400
    font-style: normal
    font-stretch: normal
    line-height: normal
    letter-spacing: 0.4px
    color: #ffffff

%regular-font
    font-family: Roboto
    font-size: 16px
    font-weight: 300
    font-style: normal
    font-stretch: normal
    line-height: normal
    letter-spacing: 0.4px
    color: #ffffff

#history_table
    width: 100%

    tr
        height: 50px
        line-height: 50px
        border-bottom: 1px solid #6d6d6d

        td
            padding-left: 20px

    thead
        @extend %header-font
        text-align: left

        tr
            &:nth-child(2)
                th
                    padding-left: 20px

            &:nth-child(1)
                border-bottom: 0px
                div
                    &:nth-child(1),
                    &:nth-child(2),
                    &:nth-child(3)
                        float: left

                    &:nth-child(1)
                        text-align: left

                    &:nth-child(3)
                        text-align: right


                    &:nth-child(1),
                    &:nth-child(3)
                        width: 375px

                        img.race_icon
                            width: 40px
                            height: 40px
                            position: relative
                            top: 10px
                        a
                            text-decoration: none
                            font-family: Roboto
                            font-size: 24px
                            font-weight: 400
                            color: #ffffff

                    &:nth-child(2)
                        width: 50px
                        .vs_sign
                            width: 50px
                            height: 50px
                            margin: 0 auto
                            border: 2px solid #54ea7c
                            border-radius: 30px
                            font-size: 16px
                            font-weight: 400
                            color: #f0f0f0
                            line-height: 50px
                            margin-bottom: 40px
                            text-align: center;

    tbody
        @extend %regular-font

        .race_icon
            width: 30px
            height: 30px
            top: 10px
            position: relative
        .result_icon
            top: 10px
            position: relative
        .player_col
            background-color: rgba(216, 216, 216, 0.05)
            width: 70px
        .map_name
            color: #54ea7c

</style>
