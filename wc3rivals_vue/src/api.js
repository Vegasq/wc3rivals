import axios from "axios";

const api = {
    state: {
        v1_db_stats: [],
        v1_usernames: [],
        v1_history: [],
        v1_enemies: [],
    },
    getters: {
        getDBStats: state => {
            return state.v1_db_stats;
        },
        getUsernames: state => {
            return state.v1_usernames;
        },
        getHistory: state => {
            return state.v1_history;
        },
        getEnemies: state => {
            return state.v1_enemies;
        },
    },
    actions: {
        getHistory: ({ commit }, args) => {
            axios
                .get('/v1/history/'+args.gateway+'/'+args.username_a+'/'+args.username_b)
                .then((response) => {
                    commit('GET_HISTORY', response.data);
                }, (err) => {
                    console.log(err);
                });
        },
        // resetHistory: ({ commit }) => {
        //     commit('RESET_HISTORY');
        // },
        getDBStats: ({ commit }) => {
            axios
                .get('/v1/db/stats')
                .then((response) => {
                    commit('GET_DBSTATS', response.data);
                }, (err) => {
                    console.log(err);
                });
        },
        getUsernames: ({ commit }, args) => {
            axios
                .get('/v1/usernames/'+args.gateway+"/"+args.username.toLowerCase())
                .then((response) => {
                    commit('GET_USERNAMES', response.data);
                }, (err) => {
                    console.log(err);
                });
        },
        getEnemies: ({ commit }, args) => {
            axios
                .get('/v1/enemies/'+args.gateway+'/'+args.username)
                .then((response) => {
                    commit('GET_ENEMIES', response.data);
                }, (err) => {
                    console.log(err);
                });
        }
    },
    mutations: {
        GET_DBSTATS: (state, data) => {
            state.v1_db_stats = data;
        },
        GET_USERNAMES: (state, data) => {
            state.v1_usernames = data;
        },
        GET_HISTORY: (state, data) => {
            state.v1_history = data;
        },
        // RESET_HISTORY: (state) => {
        //     state.v1_history = [];
        // },
        GET_ENEMIES: (state, data) => {
            state.v1_enemies = data;
        },
    }
}

export default {
    api
};