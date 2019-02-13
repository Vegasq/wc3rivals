import Vue from 'vue'
import VueRouter from 'vue-router'
import App from './App.vue'

import NotablePlayers from './components/NotablePlayers.vue'
import Rivals from './components/Rivals.vue'
import History from './components/History.vue'

Vue.config.productionTip = false;
Vue.use(VueRouter);

const routes = [
    {name: 'main', path: '/', component: NotablePlayers},
    {name: 'rivals', path: '/u/:gateway/:username', component: Rivals},
    {name: 'history', path: '/h/:gateway/:username_a/:username_b', component: History}
];
const router = new VueRouter({
    routes: routes
});

new Vue({
    render: h => h(App),
    router: router
}).$mount('#app')
