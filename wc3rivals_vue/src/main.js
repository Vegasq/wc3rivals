import Vue from 'vue'
import Vuex from 'vuex'
import VueRouter from 'vue-router'
import App from './App.vue'
import api from './api.js'

import NotablePlayers from './components/NotablePlayers.vue'
import Rivals from './components/Rivals.vue'
import History from './components/History.vue'
import ErrorPage from './components/ErrorPage.vue'

Vue.config.productionTip = false;
Vue.use(VueRouter);
Vue.use(Vuex);

var store = new Vuex.Store(api.api); 
const routes = [
    {name: 'main', path: '/', component: NotablePlayers},
    {name: 'rivals', path: '/u/:gateway/:username', component: Rivals},
    {name: 'history', path: '/h/:gateway/:username_a/:username_b', component: History},
    {name: 'error', path: '*', component: ErrorPage}
];
const router = new VueRouter({
    routes: routes
});
// router.beforeEach((to, from, next) => {
//     // console.log(to.name, to.from);
//     if (to.name == 'rivals' && to.name == from.name) {
//         console.log(132321);
//         store.dispatch('getHistory');
//     }
//     next();

// });


new Vue({
    render: h => h(App),
    store: store,
    router: router
}).$mount('#app')
