import Vuex from 'vuex'
import Vue from 'vue'
import questions from './questions'
import answers from './answers'

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
        questions,
        answers
    }
})