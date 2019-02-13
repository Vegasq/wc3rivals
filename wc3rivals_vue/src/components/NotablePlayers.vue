<template>
    <div id="notable_players_vue">
        <table id="notable_players_table">
            <thead>
                <tr class="table_title">
                    <th colspan="5">
                        NOTABLE PLAYERS
                    </th>
                </tr>
                <tr>
                    <th scope="col" class="first_col">USER</th>
                    <th scope="col" class="total_games_col">TOTAL GAMES</th>
                    <th scope="col" class="kdr_col">K/D RATIO</th>
                    <th scope="col" class="server_col">SERVER</th>
                    <th scope="col" class="twitch_col">TWITCH</th>
                </tr>
            </thead>
            <tbody>
            <tr v-for="player in players" :key="player.real_username">
                <td class="user_col first_col">
                    <router-link :to="{ name: 'rivals', params: {gateway: player.gateway, username: player.account}}">
                        <img class="race_icon"
                             v-bind:src="playerIconURL(player.race)">{{ player.real_username }}
                    </router-link>
                </td>

                <td>{{ player.total_games }}</td>
                <td>{{ player.kdr }}</td>
                <td>{{ player.gateway }}</td>
                <td>
                    <img class="twitch_icon" src="../assets/twitch.png"> 
                    <a class="twitch_link"
                        v-bind:href="'https://twitch.tv/' + player.twitch">{{ player.twitch }}
                </a></td>

            </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    data() {
        return {
            players: [],
        }
    },
    mounted() {
        // axios
        //     .get('/v1/notable_players')
        //     .then(response => (this.players = response.data),
        //           error => axios.get('http://127.0.0.1:5000/v1/notable_players')
        //                         .then(response => (this.players = response.data)));
        axios
            .get('/v1/notable_players')
            .then(response => (this.players = response.data));

},
    methods: {
      playerIconURL: function(race){
        var sex = ['male', 'female'];
        var rand = sex[Math.floor(Math.random() * sex.length)];

        return require('../assets/' + race + '_' + rand + '.png');
      },
    }
}
</script>

<style scoped>
#notable_players_table {
    width: 100%;
    color: #f0f0f0;
    font-family: Roboto;

}

#notable_players_table .twitch_link {
    color: #f0f0f0;
}

#notable_players_table thead {
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
#notable_players_table > tbody > tr > td {
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

#notable_players_table tr.table_title {
    border-bottom: 0;
}
#notable_players_table tr.table_title th {
    text-align: center;
    font-size: 20px;
    font-weight: bold;
    font-style: normal;
    font-stretch: normal;
    color: #f0f0f0;
}
#notable_players_table .first_col {
    padding-left: 20px;
}
#notable_players_table thead tr th {
    text-align: left;

}
#notable_players_table tr {
    height: 49px;
    line-height: 49px;
    border-bottom: 1px solid #6d6d6d;
}

#notable_players_table tbody tr:hover {
    background-color: rgba(216, 216, 216, 0.15);
}
#notable_players_table .user_col, #notable_players_table .user_col a {
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
#notable_players_table .user_col a:hover {
    color: #ea760e;;
}
#notable_players_table .race_icon {
    position: relative;
    width: 30px;
    height: 30px;
    top:10px;
    padding-right: 10px;
}

#notable_players_table .twitch_icon {
    position: relative;
    width: 20px;
    top: 4px;
    padding-right: 10px;
}

#notable_players_table > thead > tr:nth-child(2) > th:nth-child(1) {
    width: 200px;
}
#notable_players_table > thead > tr:nth-child(2) > th:nth-child(2) {
    width: 150px;
}
#notable_players_table > thead > tr:nth-child(2) > th:nth-child(3) {
    width: 150px;
}
#notable_players_table > thead > tr:nth-child(2) > th:nth-child(4) {
    /*width: 20px;*/
}
#notable_players_table > thead > tr:nth-child(2) > th:nth-child(5) {
    width: 143px;
}

</style>
