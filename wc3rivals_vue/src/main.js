import Vue from 'vue'
import Vuex from 'vuex'
import VueRouter from 'vue-router'
import App from './App.vue'
import axios from 'axios'

import NotablePlayers from './components/NotablePlayers.vue'
import Rivals from './components/Rivals.vue'
import History from './components/History.vue'
import ErrorPage from './components/ErrorPage.vue'

Vue.config.productionTip = false;
Vue.use(VueRouter);
Vue.use(Vuex);


const store = new Vuex.Store({
    state: {
        v1_db_stats: [],
        v1_usernames: []
    },
    getters: {
        getDbStats: state => {
            return state.v1_db_stats;
        }
    },
    actions: {
        getDBStats: ({ commit }, data) => {
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
        }
    },
    mutations: {
        GET_DBSTATS: (state, data) => {
            state.v1_db_stats = data;
        },
        GET_USERNAMES: (state, data) => {
            state.v1_usernames = data;
        }
    }
});
  

const routes = [
    {name: 'main', path: '/', component: NotablePlayers},
    {name: 'rivals', path: '/u/:gateway/:username', component: Rivals},
    {name: 'history', path: '/h/:gateway/:username_a/:username_b', component: History},
    {name: 'error', path: '*', component: ErrorPage}
];
const router = new VueRouter({
    routes: routes
});

new Vue({
    render: h => h(App),
    store: store,
    router: router
}).$mount('#app')
