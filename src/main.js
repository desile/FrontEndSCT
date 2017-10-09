import Vue from 'vue'
import VueRes from 'vue-resource'
import VueRouter from 'vue-router'
import App from './App.vue'
import Vuetify from 'vuetify'

import router from './router'
import store from './store/index'
import {sync} from 'vuex-router-sync'

import './stylus/main.styl'

sync(store, router);

Vue.use(Vuetify);
Vue.use(VueRes);

new Vue({
    el: '#app',
    router,
    store,
    template: '<App/>',
    components: {App},
    render: h => h(App)
});

